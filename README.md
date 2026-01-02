# NetworkControlPlane

**Centralized Network Configuration, Automation, and Observability**

A local network control plane and observability system that simulates how modern production networks are configured centrally, automated via declarative intent, and monitored through real-time telemetry.

## Overview

NetworkControlPlane demonstrates:

- **Control Plane Concepts**: Declarative desired state (YAML), separation of intent/deployment/observation, centralized configuration logic
- **Network Automation**: Config generation via templates, idempotent deployment, Netmiko-style device abstraction
- **Network Observability**: Live telemetry collection (latency, packet loss, throughput, interface counters, routing/path visibility)
- **Validation**: Baseline vs post-change comparison under failure and congestion scenarios

## Architecture

```
YAML Desired State
        ↓
Configuration Rendering (Jinja2)
        ↓
Automation / Deployment Layer
        ↓
Simulated Network Topology
        ↓
Telemetry Collection
        ↓
Validation Logic
        ↓
Control Plane Interface (CLI / UI)
```

## Quick Start

### Prerequisites

- Python 3.8+
- **Linux** (recommended) or macOS with Docker/Linux VM
- Mininet (install via: `sudo apt-get install mininet` on Linux)
- Network tools: ping, traceroute (usually pre-installed)

**Note for macOS users:** Mininet requires Linux kernel features. See [DOCKER_SETUP.md](DOCKER_SETUP.md) for Docker setup (recommended) or [MACOS_SETUP.md](MACOS_SETUP.md) for other options.

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Usage

#### Command Line Interface

```bash
# Deploy network configuration from YAML
python -m network_control_plane.cli deploy examples/topology.yaml

# Collect latency telemetry
python -m network_control_plane.cli ping h1 h2

# Collect path visibility telemetry
python -m network_control_plane.cli trace h1 h2

# Validate network behavior
python -m network_control_plane.cli validate h1 h2
```

#### Web UI

```bash
# Start the web control surface
python -m network_control_plane.ui

# Then open http://localhost:5001 in your browser
```

**Features:**
- Upload YAML topology files directly through the web interface
- Deploy network topologies with a single click
- Collect real-time telemetry metrics
- Validate network behavior

### Docker

#### Using Pre-built Image from Docker Hub

```bash
# Pull the image
docker pull YOUR_DOCKERHUB_USERNAME/network-control-plane:latest

# Run the container
docker run -it --rm --privileged \
  -p 5001:5001 \
  -v $(pwd):/workspace \
  -w /workspace \
  YOUR_DOCKERHUB_USERNAME/network-control-plane:latest \
  python3 -m network_control_plane.ui
```

Then open http://localhost:5001 in your browser.

#### Building from Source

```bash
# Build the Docker image
docker build -t network-control-plane:latest .

# Run with docker-compose
docker-compose up

# Or run directly
docker run -it --rm --privileged \
  -p 5001:5001 \
  -v $(pwd):/workspace \
  -w /workspace \
  network-control-plane:latest \
  /bin/bash
```

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker instructions.

### Example Workflow

1. **Define desired state** in YAML (see `examples/topology.yaml`)
2. **Deploy configuration** to create simulated topology
3. **Collect baseline telemetry** (latency, packet loss, path visibility)
4. **Inject failure** (link down, congestion)
5. **Collect post-change telemetry**
6. **Validate** network behavior against baseline

## Project Structure

```
network_control_plane/
├── desired_state/      # YAML schema and parsing
├── config_rendering/   # Jinja2 template rendering
├── automation/         # Netmiko-style device management
├── topology/           # Mininet network simulation
├── telemetry/          # Telemetry collection
├── validation/         # Validation logic
├── cli/                # Command-line interface
└── ui/                 # Web control surface
```

## Docker Hub

Pre-built Docker images are available on Docker Hub:

```bash
docker pull YOUR_DOCKERHUB_USERNAME/network-control-plane:latest
```

See [DOCKERHUB.md](DOCKERHUB.md) for instructions on publishing your own image.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT

