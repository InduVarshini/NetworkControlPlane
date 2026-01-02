"""
Control Plane CLI

Command-line interface for network control plane operations.
Provides commands for deploying desired state, collecting telemetry,
injecting failures, and validating network behavior.
"""

import logging
import sys
import click
from pathlib import Path

from ..desired_state import DesiredStateParser, DesiredStateError
from ..config_rendering import ConfigRenderer, ConfigRenderingError
from ..topology import TopologyManager, TopologyError
from ..automation import SimulatedDevice, DeviceSession, DeviceConnectionError
from ..telemetry import TelemetryCollector, TelemetryError
from ..validation import NetworkValidator, ValidationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """NetworkControlPlane - Centralized Network Configuration, Automation, and Observability"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
@click.argument('yaml_file', type=click.Path(exists=True))
def deploy(yaml_file):
    """Deploy desired network configuration from YAML file."""
    try:
        logger.info(f"Loading desired state from {yaml_file}")
        
        # Parse desired state
        parser = DesiredStateParser()
        desired_state = parser.load(yaml_file)
        topology_config = parser.get_topology()
        devices_config = parser.get_devices()
        
        logger.info("Applying desired network configuration")
        
        # Create topology
        topology = TopologyManager()
        topology.create_topology(topology_config)
        topology.start()
        
        logger.info("Simulated network topology started")
        
        # Render configurations
        renderer = ConfigRenderer()
        rendered_configs = renderer.render_all(devices_config, topology_config)
        
        # Deploy configurations
        device_instances = {}
        for device_name, device_config in devices_config.items():
            node = topology.get_node(device_name)
            device = SimulatedDevice(
                device_name=device_name,
                device_type=device_config.get('type', 'switch'),
                node=node
            )
            device_instances[device_name] = device
            
            # Deploy configuration
            with DeviceSession(device) as session:
                config = rendered_configs[device_name]
                session.deploy_config(config)
                logger.info(f"Applied desired network configuration to node {device_name}")
        
        click.echo(f"✓ Successfully deployed network configuration from {yaml_file}")
        click.echo(f"  Topology: {len(topology_config.get('nodes', []))} nodes, "
                  f"{len(topology_config.get('links', []))} links")
        click.echo(f"  Devices configured: {len(device_instances)}")
        
    except (DesiredStateError, ConfigRenderingError, TopologyError, 
            DeviceConnectionError) as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during deployment")
        click.echo(f"✗ Unexpected error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('source')
@click.argument('destination')
@click.option('--count', default=5, help='Number of ping packets')
def ping(source, destination, count):
    """Collect latency and packet loss telemetry."""
    try:
        collector = TelemetryCollector()
        metrics = collector.collect_latency(source, destination, count)
        
        click.echo(f"\nLatency metrics: {source} -> {destination}")
        click.echo(f"  Min: {metrics.min_latency_ms:.2f}ms")
        click.echo(f"  Avg: {metrics.avg_latency_ms:.2f}ms")
        click.echo(f"  Max: {metrics.max_latency_ms:.2f}ms")
        click.echo(f"  Packet Loss: {metrics.packet_loss_percent:.2f}%")
        
    except TelemetryError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('source')
@click.argument('destination')
@click.option('--max-hops', default=30, help='Maximum number of hops')
def trace(source, destination, max_hops):
    """Collect path visibility telemetry using traceroute."""
    try:
        collector = TelemetryCollector()
        metrics = collector.collect_path(source, destination, max_hops)
        
        click.echo(f"\nPath metrics: {source} -> {destination}")
        click.echo(f"  Total hops: {metrics.total_hops}")
        click.echo("\n  Path:")
        for hop in metrics.hops:
            hostname_str = hop.hostname or "*"
            latency_str = f"{hop.latency_ms:.2f}ms" if hop.latency_ms else "N/A"
            click.echo(f"    {hop.hop_number}. {hostname_str} ({hop.ip_address}) {latency_str}")
        
    except TelemetryError as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('source')
@click.argument('destination')
def validate(source, destination):
    """Validate network behavior by comparing baseline vs current state."""
    try:
        collector = TelemetryCollector()
        validator = NetworkValidator()
        
        click.echo("Collecting baseline telemetry...")
        baseline = collector.collect_all(source, destination)
        
        click.echo("Collecting current telemetry...")
        current = collector.collect_all(source, destination)
        
        click.echo("\nValidating network behavior...")
        result = validator.validate(baseline, current)
        
        if result.is_pass():
            click.echo(f"✓ {result.message}")
        else:
            click.echo(f"✗ {result.message}")
        
        if result.details:
            click.echo("\nDetails:")
            for detail in result.details:
                click.echo(f"  - {detail}")
        
        sys.exit(0 if result.is_pass() else 1)
        
    except (TelemetryError, ValidationError) as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()

