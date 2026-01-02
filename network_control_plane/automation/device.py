"""
Network Device Abstraction

Provides Netmiko-style device connection and configuration management.
This abstraction allows the control plane to interact with devices in a
consistent way, similar to real network automation tools.
"""

import logging
from typing import List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class DeviceConnectionError(Exception):
    """Raised when device connection or operation fails."""
    pass


class NetworkDevice(ABC):
    """
    Abstract base class for network device automation.
    
    Provides Netmiko-style lifecycle methods:
    - connect: Establish connection to device
    - send_config: Send configuration commands
    - commit: Commit/apply configuration changes
    - disconnect: Close connection
    
    This abstraction enables idempotent deployment of desired state.
    """
    
    def __init__(self, device_name: str, device_type: str, **kwargs):
        """
        Initialize network device.
        
        Args:
            device_name: Name of the device
            device_type: Type of device (e.g., 'switch', 'router')
            **kwargs: Additional device-specific parameters
        """
        self.device_name = device_name
        self.device_type = device_type
        self.connected = False
        self._config_pending = False
        logger.info(f"Initialized {device_type} device: {device_name}")
    
    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the device.
        
        Raises:
            DeviceConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    def send_config(self, config: str) -> None:
        """
        Send configuration commands to the device.
        
        This method should be idempotent - sending the same configuration
        multiple times should result in the same final state.
        
        Args:
            config: Configuration string to apply
            
        Raises:
            DeviceConnectionError: If configuration send fails
        """
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """
        Commit/apply pending configuration changes.
        
        In some device types, configuration changes are staged and need
        to be explicitly committed to take effect.
        
        Raises:
            DeviceConnectionError: If commit fails
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        Close connection to the device.
        
        Should clean up any resources and ensure graceful shutdown.
        """
        pass
    
    def is_connected(self) -> bool:
        """Check if device is currently connected."""
        return self.connected
    
    def has_pending_config(self) -> bool:
        """Check if there are pending configuration changes."""
        return self._config_pending


class SimulatedDevice(NetworkDevice):
    """
    Simulated network device for local testing.
    
    This implementation simulates device behavior without requiring
    real network hardware. It's used with Mininet-based topologies.
    """
    
    def __init__(self, device_name: str, device_type: str, node=None, **kwargs):
        """
        Initialize simulated device.
        
        Args:
            device_name: Name of the device
            device_type: Type of device
            node: Mininet node object (if using Mininet)
            **kwargs: Additional parameters
        """
        super().__init__(device_name, device_type, **kwargs)
        self.node = node
        self._applied_config: List[str] = []
        self._current_interface = None
    
    def connect(self) -> None:
        """Establish connection to simulated device."""
        if self.connected:
            logger.warning(f"Device '{self.device_name}' already connected")
            return
        
        if self.node is None:
            raise DeviceConnectionError(f"Cannot connect to '{self.device_name}': no node object")
        
        self.connected = True
        logger.info(f"Connected to simulated device '{self.device_name}'")
    
    def send_config(self, config: str) -> None:
        """
        Send configuration to simulated device.
        
        In simulation, we parse and apply configuration commands to the
        Mininet node. This demonstrates the deployment abstraction.
        
        Args:
            config: Configuration string to apply
        """
        if not self.connected:
            raise DeviceConnectionError(f"Device '{self.device_name}' not connected")
        
        if self.node is None:
            raise DeviceConnectionError(f"Cannot apply config to '{self.device_name}': no node object")
        
        # Parse configuration lines (preserve indentation for nested configs)
        config_lines = [line for line in config.split('\n') 
                       if line.strip() and not line.strip().startswith('#')]
        
        # Track current interface being configured (reset at start of config)
        self._current_interface = None
        
        # Apply configuration commands to the Mininet node
        for line in config_lines:
            stripped = line.strip()
            try:
                # Parse and execute configuration commands
                if stripped.startswith('hostname '):
                    # Set hostname
                    hostname = stripped.split('hostname ', 1)[1].strip()
                    self.node.cmd(f'hostname {hostname}')
                    logger.debug(f"Set hostname to {hostname} on {self.device_name}")
                
                elif stripped.startswith('interface '):
                    # Interface configuration - next lines will configure this interface
                    self._current_interface = stripped.split('interface ', 1)[1].strip()
                    logger.debug(f"Configuring interface: {self._current_interface} for {self.device_name}")
                
                elif stripped.startswith('ip address ') or (line.startswith(' ') and 'ip address' in stripped):
                    # Configure IP address on interface
                    # Handle both "ip address" and " ip address" (with leading space)
                    if ' ip address ' in line:
                        ip_part = line.split(' ip address ', 1)[1].strip()
                    else:
                        ip_part = stripped.split('ip address ', 1)[1].strip()
                    parts = ip_part.split()
                    ip_addr = parts[0]
                    netmask = parts[1] if len(parts) > 1 else None
                    
                    # Map interface name to Mininet interface
                    # For hosts: {hostname}-eth0, {hostname}-eth1, etc. (starts at 0)
                    # For switches: {hostname}-eth1, {hostname}-eth2, etc. (starts at 1)
                    if self._current_interface:
                        # Extract eth number from interface name (e.g., eth0 -> 0, eth1 -> 1)
                        eth_num = self._current_interface.replace('eth', '')
                        if self.device_type == 'switch':
                            # Switches start numbering at 1, so eth0 -> eth1, eth1 -> eth2
                            eth_num = str(int(eth_num) + 1) if eth_num.isdigit() else '1'
                        if_name = f'{self.device_name}-eth{eth_num}'
                    else:
                        # Default to first interface
                        if self.device_type == 'switch':
                            if_name = f'{self.device_name}-eth1'  # Switches start at 1
                        else:
                            if_name = f'{self.device_name}-eth0'  # Hosts start at 0
                    
                    # Convert netmask to CIDR if needed
                    if netmask:
                        # Simple netmask to CIDR conversion for common cases
                        cidr_map = {
                            '255.255.255.0': '/24',
                            '255.255.0.0': '/16',
                            '255.0.0.0': '/8'
                        }
                        cidr = cidr_map.get(netmask, '/24')
                    else:
                        cidr = '/24'
                    
                    # First, flush any existing IPs on the interface (Mininet auto-assigns IPs)
                    flush_result = self.node.cmd(f'ip addr flush dev {if_name} 2>&1')
                    # Add the configured IP address
                    result = self.node.cmd(f'ip addr add {ip_addr}{cidr} dev {if_name} 2>&1')
                    if result and result.strip() and 'Cannot find device' not in result:
                        logger.warning(f"IP config result for {if_name}: {result.strip()}")
                    # Ensure interface is up
                    self.node.cmd(f'ip link set {if_name} up 2>/dev/null || true')
                    
                    # For switches, enable IP forwarding and configure ARP handling
                    if self.device_type == 'switch':
                        self.node.cmd('sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1')
                        # Enable proxy ARP so switch responds to ARP requests
                        self.node.cmd(f'echo 1 > /proc/sys/net/ipv4/conf/{if_name}/proxy_arp 2>/dev/null || true')
                        # Enable ARP on the interface
                        self.node.cmd(f'echo 1 > /proc/sys/net/ipv4/conf/{if_name}/arp_ignore 2>/dev/null || true')
                        self.node.cmd(f'echo 2 > /proc/sys/net/ipv4/conf/{if_name}/arp_announce 2>/dev/null || true')
                        logger.debug(f"Enabled IP forwarding and ARP on switch {self.device_name} interface {if_name}")
                    
                    # Verify IP was set by checking the interface
                    verify = self.node.cmd(f'ip addr show {if_name} 2>/dev/null')
                    if ip_addr in verify:
                        logger.info(f"✓ Configured IP {ip_addr}{cidr} on {if_name} for {self.device_name}")
                    else:
                        logger.warning(f"⚠ IP {ip_addr} not found on {if_name} after configuration. Interface shows: {verify[:200]}")
                
                elif line.startswith('ip route '):
                    # Add static route
                    route_part = line.split('ip route ', 1)[1].strip()
                    parts = route_part.split()
                    network = parts[0]
                    next_hop = parts[1] if len(parts) > 1 else None
                    
                    if next_hop:
                        # Add netmask if network doesn't have CIDR notation
                        if '/' not in network:
                            network = f'{network}/24'  # Default to /24 if not specified
                        # Remove existing route first, then add
                        self.node.cmd(f'ip route del {network} via {next_hop} 2>/dev/null || true')
                        # For switches, we might need to specify the interface
                        if self.device_type == 'switch':
                            # Try to find the interface connected to next_hop's subnet
                            # This is a simplified approach - in production would parse topology
                            result = self.node.cmd(f'ip route add {network} via {next_hop} 2>&1')
                        else:
                            result = self.node.cmd(f'ip route add {network} via {next_hop} 2>&1')
                        if result and 'File exists' not in result and 'Cannot find device' not in result:
                            logger.debug(f"Added route {network} via {next_hop} on {self.device_name}")
                        else:
                            logger.info(f"Added route {network} via {next_hop} on {self.device_name}")
                
            except Exception as e:
                logger.warning(f"Failed to apply config line '{line}' to {self.device_name}: {e}")
        
        # Store applied config
        self._applied_config.extend(config_lines)
        self._config_pending = True
        
        logger.info(f"Sent configuration to device '{self.device_name}' ({len(config_lines)} commands)")
    
    def commit(self) -> None:
        """Commit configuration changes."""
        if not self.connected:
            raise DeviceConnectionError(f"Device '{self.device_name}' not connected")
        
        if not self._config_pending:
            logger.debug(f"No pending configuration for device '{self.device_name}'")
            return
        
        # In simulation, commit is a no-op but we mark config as applied
        self._config_pending = False
        logger.info(f"Committed configuration changes for device '{self.device_name}'")
    
    def disconnect(self) -> None:
        """Disconnect from simulated device."""
        if not self.connected:
            return
        
        self.connected = False
        logger.info(f"Disconnected from device '{self.device_name}'")
    
    def get_applied_config(self) -> List[str]:
        """Get list of applied configuration commands."""
        return self._applied_config.copy()

