#!/usr/bin/env python3
"""
Example NetworkControlPlane Workflow

Demonstrates the complete workflow:
1. Load desired state from YAML
2. Deploy network configuration
3. Collect baseline telemetry
4. Validate network behavior
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from network_control_plane.desired_state import DesiredStateParser
from network_control_plane.config_rendering import ConfigRenderer
from network_control_plane.topology import TopologyManager
from network_control_plane.automation import SimulatedDevice, DeviceSession
from network_control_plane.telemetry import TelemetryCollector
from network_control_plane.validation import NetworkValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run example workflow."""
    yaml_file = Path(__file__).parent / "topology.yaml"
    
    try:
        # Step 1: Load desired state
        logger.info("Step 1: Loading desired state from YAML")
        parser = DesiredStateParser()
        desired_state = parser.load(str(yaml_file))
        topology_config = parser.get_topology()
        devices_config = parser.get_devices()
        
        # Step 2: Create topology
        logger.info("Step 2: Creating simulated network topology")
        topology = TopologyManager()
        topology.create_topology(topology_config)
        topology.start()
        
        # Step 3: Render configurations
        logger.info("Step 3: Rendering device configurations")
        renderer = ConfigRenderer()
        rendered_configs = renderer.render_all(devices_config, topology_config)
        
        # Step 4: Deploy configurations
        logger.info("Step 4: Deploying configurations to devices")
        device_instances = {}
        for device_name, device_config in devices_config.items():
            node = topology.get_node(device_name)
            device = SimulatedDevice(
                device_name=device_name,
                device_type=device_config.get('type', 'switch'),
                node=node
            )
            device_instances[device_name] = device
            
            with DeviceSession(device) as session:
                config = rendered_configs[device_name]
                session.deploy_config(config)
                logger.info(f"Applied desired network configuration to node {device_name}")
        
        # Step 5: Collect baseline telemetry
        logger.info("Step 5: Collecting baseline telemetry")
        collector = TelemetryCollector(topology)
        
        # Find host nodes for testing
        hosts = [name for name, config in devices_config.items() 
                if config.get('type') == 'host']
        
        if len(hosts) >= 2:
            source = hosts[0]
            destination = hosts[1]
            
            baseline = collector.collect_all(source, destination)
            
            if baseline.latency:
                logger.info(f"Baseline latency: {baseline.latency.avg_latency_ms:.2f}ms")
                logger.info(f"Baseline packet loss: {baseline.latency.packet_loss_percent:.2f}%")
            
            if baseline.path:
                logger.info(f"Baseline path: {baseline.path.total_hops} hops")
            
            # Step 6: Validate connectivity
            logger.info("Step 6: Validating network connectivity")
            validator = NetworkValidator()
            connectivity_result = validator.validate_connectivity(baseline)
            
            if connectivity_result.is_pass():
                logger.info(f"✓ Connectivity validation passed: {connectivity_result.message}")
            else:
                logger.warning(f"✗ Connectivity validation failed: {connectivity_result.message}")
        
        logger.info("\nExample workflow completed successfully!")
        logger.info("Network topology is running. Press Ctrl+C to stop.")
        
        # Keep topology running
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nShutting down...")
        
    except Exception as e:
        logger.exception("Error in example workflow")
        sys.exit(1)
    finally:
        # Cleanup
        if 'topology' in locals():
            topology.cleanup()


if __name__ == '__main__':
    main()

