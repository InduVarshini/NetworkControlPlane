"""
Configuration Renderer

Renders device configurations from Jinja2 templates based on desired state.
This implements the configuration rendering layer of the network control plane,
transforming declarative intent into device-specific configuration commands.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateError

logger = logging.getLogger(__name__)


class ConfigRenderingError(Exception):
    """Raised when configuration rendering fails."""
    pass


class ConfigRenderer:
    """
    Renders network device configurations from Jinja2 templates.
    
    Takes desired state and device-specific templates to generate configuration
    commands that can be deployed via the automation layer.
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the configuration renderer.
        
        Args:
            template_dir: Directory containing Jinja2 templates. If None, uses
                         default templates directory.
        """
        if template_dir is None:
            # Default to templates directory in package
            template_dir = str(Path(__file__).parent / "templates")
        
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        logger.info(f"Initialized configuration renderer with template directory: {self.template_dir}")
    
    def render(self, device_name: str, device_config: Dict[str, Any], 
               topology: Dict[str, Any]) -> str:
        """
        Render configuration for a device from templates.
        
        This performs configuration rendering based on the desired state,
        generating device-specific configuration commands.
        
        Args:
            device_name: Name of the device to render configuration for
            device_config: Device configuration from desired state
            topology: Network topology information
            
        Returns:
            Rendered configuration string
            
        Raises:
            ConfigRenderingError: If template not found or rendering fails
        """
        device_type = device_config.get('type', 'default')
        template_name = f"{device_type}.j2"
        
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            # Fallback to default template
            logger.warning(f"Template '{template_name}' not found, using default template")
            try:
                template = self.env.get_template("default.j2")
            except TemplateNotFound:
                raise ConfigRenderingError(
                    f"No template found for device type '{device_type}' and no default template available"
                )
        
        # Prepare template context
        context = {
            'device_name': device_name,
            'device_config': device_config,
            'topology': topology,
            'interfaces': device_config.get('interfaces', []),
            'routes': device_config.get('routes', []),
        }
        
        try:
            rendered_config = template.render(**context)
            logger.info(f"Successfully rendered configuration for device '{device_name}'")
            return rendered_config
        except TemplateError as e:
            raise ConfigRenderingError(f"Template rendering failed for '{device_name}': {e}")
        except Exception as e:
            raise ConfigRenderingError(f"Unexpected error rendering configuration for '{device_name}': {e}")
    
    def render_all(self, devices: Dict[str, Dict[str, Any]], 
                   topology: Dict[str, Any]) -> Dict[str, str]:
        """
        Render configurations for all devices.
        
        Args:
            devices: Dictionary mapping device names to their configurations
            topology: Network topology information
            
        Returns:
            Dictionary mapping device names to their rendered configurations
        """
        rendered_configs = {}
        
        for device_name, device_config in devices.items():
            try:
                rendered_configs[device_name] = self.render(device_name, device_config, topology)
            except ConfigRenderingError as e:
                logger.error(f"Failed to render configuration for '{device_name}': {e}")
                raise
        
        logger.info(f"Rendered configurations for {len(rendered_configs)} devices")
        return rendered_configs

