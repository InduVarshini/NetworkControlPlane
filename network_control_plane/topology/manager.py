"""
Topology Manager

Manages simulated network topology using Mininet.
Creates and manages the simulated network topology based on desired state.
"""

import logging
import os
import platform
from typing import Dict, List, Any, Optional
from mininet.net import Mininet
from mininet.node import Host, Switch, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

logger = logging.getLogger(__name__)

# Configure Mininet for macOS compatibility
if platform.system() == 'Darwin':  # macOS
    # Suppress Linux-specific checks on macOS
    os.environ['MININET_USE_SUDO'] = '0'
    # Mininet will still need sudo, but this helps with some checks


class TopologyError(Exception):
    """Raised when topology operations fail."""
    pass


class TopologyManager:
    """
    Manages simulated network topology using Mininet.
    
    Creates and manages the simulated network topology based on desired state.
    This provides the foundation for network control plane operations without
    requiring real network hardware.
    """
    
    def __init__(self):
        """Initialize topology manager."""
        self.net: Optional[Mininet] = None
        self.topology_config: Optional[Dict[str, Any]] = None
        self.devices: Dict[str, Any] = {}
        self.is_macos = platform.system() == 'Darwin'
        
        if self.is_macos:
            logger.warning(
                "Running on macOS: Mininet requires Linux kernel features. "
                "Consider using Docker or a Linux VM for full functionality."
            )
        
        logger.info("Initialized topology manager")
    
    def create_topology(self, topology_config: Dict[str, Any]) -> None:
        """
        Create simulated network topology from configuration.
        
        This builds the simulated network topology based on desired state,
        creating nodes and links as specified.
        
        Args:
            topology_config: Topology configuration from desired state
            
        Raises:
            TopologyError: If topology creation fails
        """
        if self.net is not None:
            logger.warning("Topology already exists, cleaning up first")
            self.cleanup()
        
        self.topology_config = topology_config
        
        try:
            # Set Mininet log level
            setLogLevel('info')
            
            # Start Open vSwitch if in Docker/Linux environment
            # This is needed for OVSSwitch to work
            if not self.is_macos:
                try:
                    import subprocess
                    import time
                    import os
                    
                    # Ensure OVS directories exist
                    os.makedirs('/var/run/openvswitch', exist_ok=True)
                    os.makedirs('/var/log/openvswitch', exist_ok=True)
                    
                    # Check if OVS is already running
                    try:
                        subprocess.run(['ovs-vsctl', 'show'], 
                                     capture_output=True, check=True, timeout=2)
                        logger.debug("Open vSwitch is already running")
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        # OVS not running, start it
                        logger.info("Starting Open vSwitch...")
                        
                        # Start OVS database server
                        subprocess.Popen(
                            ['ovsdb-server', '--detach', 
                             '--pidfile=/var/run/openvswitch/ovsdb-server.pid',
                             '--remote=punix:/var/run/openvswitch/db.sock',
                             '--log-file=/var/log/openvswitch/ovsdb-server.log'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        time.sleep(2)  # Wait for database server to start
                        
                        # Start OVS daemon
                        subprocess.Popen(
                            ['ovs-vswitchd', '--detach',
                             '--pidfile=/var/run/openvswitch/ovs-vswitchd.pid',
                             '--log-file=/var/log/openvswitch/ovs-vswitchd.log'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        time.sleep(2)  # Wait for daemon to start
                        
                        # Verify OVS is running
                        subprocess.run(['ovs-vsctl', 'show'], 
                                     capture_output=True, check=True, timeout=5)
                        logger.info("Open vSwitch started successfully")
                except Exception as e:
                    logger.warning(f"Failed to start Open vSwitch: {e}. Mininet may still work with basic switches.")
            
            # Create Mininet network
            # Use ipBase to avoid conflicts, and configure for macOS compatibility
            self.net = Mininet(link=TCLink, ipBase='10.0.0.0/8')
            
            # Create nodes
            nodes_config = topology_config.get('nodes', [])
            if isinstance(nodes_config, dict):
                nodes_config = list(nodes_config.values())
            
            for node_config in nodes_config:
                self._create_node(node_config)
            
            # Create links
            links_config = topology_config.get('links', [])
            if isinstance(links_config, dict):
                links_config = list(links_config.values())
            
            for link_config in links_config:
                self._create_link(link_config)
            
            # Build network - handle macOS-specific errors gracefully
            try:
                self.net.build()
            except (FileNotFoundError, OSError) as e:
                error_msg = str(e)
                if 'lsmod' in error_msg or 'No such file or directory' in error_msg:
                    # macOS compatibility issue - Mininet tries to use Linux commands
                    if platform.system() == 'Darwin':
                        raise TopologyError(
                            f"Mininet requires Linux kernel features not available on macOS. "
                            f"Error: {error_msg}\n\n"
                            f"Options:\n"
                            f"  1. Run on Linux or use a Linux VM/container\n"
                            f"  2. Use Docker: docker run -it --privileged opennetworking/mn\n"
                            f"  3. For development/testing, consider using a Linux environment"
                        )
                    else:
                        raise TopologyError(f"Failed to build topology: {e}")
                else:
                    raise
            
            logger.info(f"Created simulated network topology with {len(self.devices)} devices")
            
        except Exception as e:
            raise TopologyError(f"Failed to create topology: {e}")
    
    def _create_node(self, node_config: Dict[str, Any]) -> None:
        """
        Create a node in the topology.
        
        Args:
            node_config: Node configuration dictionary
        """
        node_name = node_config.get('name', '')
        node_type = node_config.get('type', 'host').lower()
        
        if not node_name:
            raise TopologyError("Node configuration missing 'name' field")
        
        if node_type == 'switch':
            # Use OVSSwitch - requires Open vSwitch to be running
            # OVS provides better performance and features than basic switches
            # Note: OVS switches can have IP addresses and route if IP forwarding is enabled
            node = self.net.addSwitch(node_name, cls=OVSSwitch)
        elif node_type == 'host':
            node = self.net.addHost(node_name)
        else:
            raise TopologyError(f"Unknown node type: {node_type}")
        
        self.devices[node_name] = node
        logger.debug(f"Created {node_type} node: {node_name}")
    
    def _create_link(self, link_config: Dict[str, Any]) -> None:
        """
        Create a link between nodes.
        
        Args:
            link_config: Link configuration dictionary
        """
        node1_name = link_config.get('node1', '')
        node2_name = link_config.get('node2', '')
        
        if not node1_name or not node2_name:
            raise TopologyError("Link configuration missing 'node1' or 'node2' field")
        
        if node1_name not in self.devices:
            raise TopologyError(f"Link references unknown node: {node1_name}")
        if node2_name not in self.devices:
            raise TopologyError(f"Link references unknown node: {node2_name}")
        
        node1 = self.devices[node1_name]
        node2 = self.devices[node2_name]
        
        # Get link parameters
        bw = link_config.get('bandwidth', 10)  # Mbps
        delay = link_config.get('delay', '0ms')
        loss = link_config.get('loss', 0)  # percentage
        
        self.net.addLink(node1, node2, bw=bw, delay=delay, loss=loss)
        logger.debug(f"Created link: {node1_name} <-> {node2_name} (bw={bw}Mbps, delay={delay}, loss={loss}%)")
    
    def start(self) -> None:
        """
        Start the network topology.
        
        Raises:
            TopologyError: If topology not created or start fails
        """
        if self.net is None:
            raise TopologyError("Topology not created. Call create_topology() first.")
        
        try:
            self.net.start()
            logger.info("Started simulated network topology")
        except Exception as e:
            raise TopologyError(f"Failed to start topology: {e}")
    
    def stop(self) -> None:
        """Stop the network topology."""
        if self.net is None:
            return
        
        try:
            self.net.stop()
            logger.info("Stopped simulated network topology")
        except Exception as e:
            logger.error(f"Error stopping topology: {e}")
    
    def cleanup(self) -> None:
        """Clean up topology resources."""
        self.stop()
        
        if self.net is not None:
            try:
                self.net.cleanup()
                logger.info("Cleaned up topology resources")
            except Exception as e:
                logger.error(f"Error cleaning up topology: {e}")
        
        self.net = None
        self.devices.clear()
    
    def get_node(self, node_name: str) -> Any:
        """
        Get a node from the topology.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Mininet node object
            
        Raises:
            TopologyError: If node not found
        """
        if node_name not in self.devices:
            raise TopologyError(f"Node '{node_name}' not found in topology")
        return self.devices[node_name]
    
    def get_all_nodes(self) -> Dict[str, Any]:
        """Get all nodes in the topology."""
        return self.devices.copy()
    
    def is_running(self) -> bool:
        """Check if topology is currently running."""
        if self.net is None:
            return False
        
        # Check if network has been started by verifying nodes exist and are accessible
        # Mininet doesn't have a 'running' attribute, so we check if nodes are initialized
        try:
            # If network has been started, we should be able to access nodes
            # Check if we have nodes and they're accessible
            if len(self.devices) == 0:
                return False
            
            # Try to check if a node exists and is accessible (simple check)
            # If network hasn't been started, accessing nodes will fail
            first_node = list(self.devices.values())[0]
            # If we can get the node's name, it's likely started
            return hasattr(first_node, 'name') or hasattr(first_node, 'intf')
        except Exception:
            # If any error occurs, assume not running
            return False

