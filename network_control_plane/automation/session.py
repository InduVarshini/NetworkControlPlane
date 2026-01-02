"""
Device Session Management

Manages device connections and configuration deployment sessions.
Provides a context manager interface for Netmiko-style device automation.
"""

import logging
from typing import Optional
from contextlib import contextmanager

from .device import NetworkDevice, DeviceConnectionError

logger = logging.getLogger(__name__)


class DeviceSession:
    """
    Manages a device connection session for configuration deployment.
    
    Provides a context manager interface that ensures proper connection
    lifecycle management, similar to Netmiko's device session handling.
    """
    
    def __init__(self, device: NetworkDevice):
        """
        Initialize device session.
        
        Args:
            device: NetworkDevice instance to manage
        """
        self.device = device
        self._connected = False
    
    def __enter__(self):
        """Enter context manager - connect to device."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - disconnect from device."""
        self.disconnect()
        return False
    
    def connect(self) -> None:
        """
        Connect to the device.
        
        Raises:
            DeviceConnectionError: If connection fails
        """
        if self._connected:
            logger.warning(f"Session already connected to device '{self.device.device_name}'")
            return
        
        try:
            self.device.connect()
            self._connected = True
            logger.info(f"Established session with device '{self.device.device_name}'")
        except Exception as e:
            raise DeviceConnectionError(f"Failed to connect to device '{self.device.device_name}': {e}")
    
    def disconnect(self) -> None:
        """Disconnect from the device."""
        if not self._connected:
            return
        
        try:
            self.device.disconnect()
            self._connected = False
            logger.info(f"Closed session with device '{self.device.device_name}'")
        except Exception as e:
            logger.error(f"Error disconnecting from device '{self.device.device_name}': {e}")
    
    def deploy_config(self, config: str, commit: bool = True) -> None:
        """
        Deploy configuration to the device.
        
        This implements the idempotent deployment workflow:
        1. Send configuration commands
        2. Optionally commit changes
        
        Args:
            config: Configuration string to deploy
            commit: Whether to commit changes after sending config
            
        Raises:
            DeviceConnectionError: If deployment fails
        """
        if not self._connected:
            raise DeviceConnectionError(f"Session not connected to device '{self.device.device_name}'")
        
        try:
            logger.info(f"Deploying configuration to device '{self.device.device_name}'")
            self.device.send_config(config)
            
            if commit:
                self.device.commit()
                logger.info(f"Configuration deployed and committed to device '{self.device.device_name}'")
            else:
                logger.info(f"Configuration sent to device '{self.device.device_name}' (pending commit)")
        except Exception as e:
            raise DeviceConnectionError(f"Failed to deploy configuration to device '{self.device.device_name}': {e}")

