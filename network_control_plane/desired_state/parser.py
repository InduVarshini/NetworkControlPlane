"""
YAML Desired State Parser

Parses and validates YAML files containing declarative network configuration.
This represents the centralized configuration intent for the network control plane.
"""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


class DesiredStateError(Exception):
    """Raised when desired state parsing or validation fails."""
    pass


class DesiredStateParser:
    """
    Parses YAML desired state files for network control plane configuration.
    
    The desired state defines the intended network topology, device configurations,
    and routing policies in a declarative format.
    """
    
    def __init__(self):
        """Initialize the desired state parser."""
        self._state: Optional[Dict[str, Any]] = None
    
    def load(self, yaml_path: str) -> Dict[str, Any]:
        """
        Load and parse a YAML desired state file.
        
        Args:
            yaml_path: Path to the YAML file containing desired network state
            
        Returns:
            Parsed desired state dictionary
            
        Raises:
            DesiredStateError: If parsing or validation fails
        """
        path = Path(yaml_path)
        
        if not path.exists():
            raise DesiredStateError(f"Desired state file not found: {yaml_path}")
        
        try:
            with open(path, 'r') as f:
                self._state = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise DesiredStateError(f"Invalid YAML syntax: {e}")
        except Exception as e:
            raise DesiredStateError(f"Failed to read desired state file: {e}")
        
        self._validate()
        return self._state
    
    def _validate(self) -> None:
        """
        Validate the desired state structure.
        
        Ensures required fields are present and have correct types.
        This enforces the schema for centralized network configuration.
        
        Raises:
            DesiredStateError: If validation fails
        """
        if self._state is None:
            raise DesiredStateError("No desired state loaded")
        
        # Validate top-level structure
        required_keys = ['topology', 'devices']
        for key in required_keys:
            if key not in self._state:
                raise DesiredStateError(f"Missing required key in desired state: {key}")
        
        # Validate topology structure
        topology = self._state['topology']
        if not isinstance(topology, dict):
            raise DesiredStateError("Topology must be a dictionary")
        
        if 'nodes' not in topology:
            raise DesiredStateError("Topology must contain 'nodes'")
        
        if 'links' not in topology:
            raise DesiredStateError("Topology must contain 'links'")
        
        # Validate devices structure
        devices = self._state['devices']
        if not isinstance(devices, dict):
            raise DesiredStateError("Devices must be a dictionary")
        
        # Validate each device has required fields
        for device_name, device_config in devices.items():
            if not isinstance(device_config, dict):
                raise DesiredStateError(f"Device '{device_name}' configuration must be a dictionary")
            
            if 'type' not in device_config:
                raise DesiredStateError(f"Device '{device_name}' missing required field: type")
    
    def get_topology(self) -> Dict[str, Any]:
        """
        Get the network topology definition from desired state.
        
        Returns:
            Topology configuration dictionary
            
        Raises:
            DesiredStateError: If no state is loaded
        """
        if self._state is None:
            raise DesiredStateError("No desired state loaded")
        return self._state.get('topology', {})
    
    def get_devices(self) -> Dict[str, Any]:
        """
        Get device configurations from desired state.
        
        Returns:
            Dictionary mapping device names to their configurations
            
        Raises:
            DesiredStateError: If no state is loaded
        """
        if self._state is None:
            raise DesiredStateError("No desired state loaded")
        return self._state.get('devices', {})
    
    def get_device_config(self, device_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific device.
        
        Args:
            device_name: Name of the device
            
        Returns:
            Device configuration dictionary
            
        Raises:
            DesiredStateError: If device not found or no state loaded
        """
        devices = self.get_devices()
        if device_name not in devices:
            raise DesiredStateError(f"Device '{device_name}' not found in desired state")
        return devices[device_name]

