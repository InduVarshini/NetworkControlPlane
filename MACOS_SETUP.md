# macOS Setup Guide

## Overview

NetworkControlPlane uses Mininet for network simulation, which requires Linux kernel features. On macOS, you have several options to run the system.

## Option 1: Docker (Recommended)

Use Mininet's official Docker image:

```bash
# Pull the Mininet Docker image
docker pull opennetworking/mn

# Run NetworkControlPlane inside Docker
docker run -it --privileged \
  -v $(pwd):/workspace \
  -w /workspace \
  opennetworking/mn \
  python3 -m network_control_plane.cli deploy examples/topology.yaml
```

## Option 2: Linux VM

1. Install VirtualBox or VMware
2. Create a Linux VM (Ubuntu recommended)
3. Install dependencies in the VM:
   ```bash
   sudo apt-get update
   sudo apt-get install mininet python3-pip
   pip3 install -r requirements.txt
   ```
4. Copy the project to the VM and run it there

## Option 3: Linux Subsystem/Container

- Use WSL2 (if on Windows) or similar Linux environment
- Use a Linux container/VM on macOS

## Testing Without Full Topology

You can test most components without Mininet:

```bash
# Test YAML parsing and config rendering
python3 -c "
from network_control_plane.desired_state import DesiredStateParser
from network_control_plane.config_rendering import ConfigRenderer

parser = DesiredStateParser()
state = parser.load('examples/topology.yaml')
renderer = ConfigRenderer()
configs = renderer.render_all(parser.get_devices(), parser.get_topology())
print('✓ Configuration rendering works')
"

# Test validation logic
python3 -c "
from network_control_plane.validation import NetworkValidator
from network_control_plane.telemetry.metrics import TelemetryMetrics, LatencyMetrics
from datetime import datetime

validator = NetworkValidator()
baseline = TelemetryMetrics()
baseline.latency = LatencyMetrics('h1', 'h2', 10.0, 12.5, 15.0, 0.0, datetime.now())
current = TelemetryMetrics()
current.latency = LatencyMetrics('h1', 'h2', 10.0, 13.0, 16.0, 1.0, datetime.now())
result = validator.validate(baseline, current)
print(f'✓ Validation: {result.status.value}')
"
```

## Error Messages

If you see `lsmod: No such file or directory`, this is expected on macOS. Mininet is trying to use Linux kernel module commands that don't exist on macOS.

The system will provide clear error messages guiding you to use Docker or a Linux environment.

