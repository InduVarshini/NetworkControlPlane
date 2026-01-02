# NetworkControlPlane

**Centralized Network Configuration, Automation, and Observability**

A local network control plane and observability system that simulates how modern production networks are configured centrally, automated via declarative intent, and monitored through real-time telemetry.

## Overview

NetworkControlPlane demonstrates core network control plane concepts through a complete implementation:

- **Declarative Desired State**: YAML-based configuration that defines network intent (topology, device configs, routing policies)
- **Configuration Rendering**: Jinja2 template engine transforms declarative state into device-specific configurations
- **Network Automation**: Netmiko-style device abstraction layer for idempotent configuration deployment
- **Network Simulation**: Mininet-based topology simulation using Linux network namespaces and virtual Ethernet pairs
- **Real-time Telemetry**: Collection of latency, packet loss, throughput, interface counters, and path visibility metrics
- **Validation Framework**: Baseline vs post-change comparison for deterministic network behavior validation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Control Plane Interface                   │
│              (CLI / Web UI / REST API)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Desired State Parser (YAML)                     │
│  • Validates YAML schema                                     │
│  • Extracts topology and device configurations               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         Configuration Renderer (Jinja2 Templates)           │
│  • Template-based config generation                          │
│  • Device-specific configuration rendering                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         Automation Layer (Device Abstraction)                │
│  • SimulatedDevice: Netmiko-style device interface           │
│  • DeviceSession: Configuration deployment                   │
│  • Idempotent config application                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         Topology Manager (Mininet)                           │
│  • Linux network namespaces (node isolation)                 │
│  • Virtual Ethernet pairs (veth) for links                   │
│  • Open vSwitch (OVS) for switching                          │
│  • Linux Traffic Control (TC) for link characteristics       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         Telemetry Collector                                  │
│  • Latency metrics (ping-based)                             │
│  • Path visibility (traceroute)                              │
│  • Interface counters (ifconfig/ip)                          │
│  • Throughput measurements                                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│         Validation Engine                                    │
│  • Baseline telemetry capture                                │
│  • Post-change comparison                                    │
│  • Deterministic pass/fail validation                        │
└─────────────────────────────────────────────────────────────┘
```

## Technical Components

### 1. Desired State Parser (`desired_state/parser.py`)

- **Purpose**: Parses and validates YAML files containing declarative network configuration
- **Key Features**:
  - YAML schema validation
  - Topology extraction (nodes, links with bandwidth/delay/loss characteristics)
  - Device configuration extraction (interfaces, routes, hostnames)
- **Output**: Structured Python dictionaries ready for downstream processing

### 2. Configuration Renderer (`config_rendering/renderer.py`)

- **Purpose**: Transforms declarative state into device-specific configuration commands
- **Technology**: Jinja2 template engine
- **Key Features**:
  - Template-based configuration generation
  - Device-specific template support
  - Extensible template system (default templates in `templates/default.j2`)
- **Output**: Rendered configuration strings per device

### 3. Automation Layer (`automation/`)

- **`device.py`**: `SimulatedDevice` class providing Netmiko-style device abstraction
- **`session.py`**: `DeviceSession` context manager for configuration deployment
- **Key Features**:
  - Idempotent configuration application
  - Session-based configuration management
  - Device type abstraction (host, switch, router)

### 4. Topology Manager (`topology/manager.py`)

- **Purpose**: Creates and manages simulated network topology using Mininet
- **Technology Stack**:
  - **Mininet**: Network emulation framework
  - **Linux Network Namespaces**: Isolated network stacks per node
  - **Virtual Ethernet Pairs (veth)**: Virtual links between nodes
  - **Open vSwitch (OVS)**: Virtual switching functionality
  - **Linux Traffic Control (TC)**: Enforces link characteristics (bandwidth, delay, packet loss)
- **Key Features**:
  - Dynamic topology creation from YAML
  - Link characteristic enforcement (bandwidth limits, latency, packet loss)
  - Node isolation via network namespaces
  - Topology lifecycle management (create, start, stop, cleanup)

### 5. Telemetry Collector (`telemetry/collector.py`)

- **Purpose**: Collects real-time network telemetry from simulated topology
- **Metrics Collected**:
  - **Latency Metrics**: RTT, min/max/avg latency, packet loss (via `ping`)
  - **Path Metrics**: Hop-by-hop path visibility (via `traceroute`)
  - **Interface Counters**: RX/TX packets, bytes, errors (via `ifconfig`/`ip`)
  - **Throughput Metrics**: Bandwidth utilization measurements
- **Technology**: Uses real system tools (`ping`, `traceroute`, `ifconfig`, `ip`) within network namespaces

### 6. Validation Engine (`validation/validator.py`)

- **Purpose**: Validates network behavior by comparing baseline vs post-change telemetry
- **Key Features**:
  - Baseline telemetry capture
  - Post-change telemetry collection
  - Deterministic comparison logic
  - Pass/fail/warning status determination
  - Detailed validation reports

### 7. Web UI (`ui/app.py`)

- **Technology**: Flask-based REST API with HTML frontend
- **Features**:
  - YAML file upload (multipart form data)
  - Topology deployment via web interface
  - Real-time telemetry collection
  - Network validation
  - Topology status monitoring
- **API Endpoints**:
  - `GET /api/topology/status` - Get current topology status
  - `POST /api/topology/deploy` - Deploy topology from uploaded YAML or file path
  - `POST /api/telemetry/collect` - Collect telemetry metrics
  - `POST /api/validation/validate` - Validate network behavior

## Technology Stack

- **Python 3.8+**: Core language
- **Mininet 2.3.0+**: Network emulation framework
- **Jinja2 3.1.0+**: Template engine for configuration rendering
- **PyYAML 6.0+**: YAML parsing and validation
- **Flask 2.3.0+**: Web framework for UI
- **Click 8.1.0+**: CLI framework
- **Paramiko 3.0.0+**: SSH/networking abstractions

## Quick Start

### Prerequisites

- Python 3.8+ (or use Docker)
- **Linux** (recommended) or macOS with Docker
- Mininet (install via: `sudo apt-get install mininet` on Linux)

**Note for macOS users:** Mininet requires Linux kernel features (network namespaces, veth pairs). Use Docker (recommended) - see [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md).

### Installation

**Option 1: Using Docker (Recommended)**

```bash
# Pull pre-built image from Docker Hub
docker pull varzzz/network-control-plane:latest

# Run the web UI
docker run -it --rm --privileged -p 5001:5001 \
  -v $(pwd):/workspace -w /workspace \
  varzzz/network-control-plane:latest \
  python3 -m network_control_plane.ui
```

Then open http://localhost:5001 in your browser.

**Option 2: Local Python Installation**

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

# Collect latency telemetry between nodes
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

**Web UI Features:**
- Upload YAML topology files directly through the web interface
- Deploy network topologies with a single click
- Collect real-time telemetry metrics
- Validate network behavior

### Docker Compose

**Quick Start:**
```bash
# Build and run with Docker Compose
docker-compose up

# Access web UI at http://localhost:5001
```

**Building from source:**
```bash
docker build -t network-control-plane:latest .
docker-compose up
```

See [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md) for detailed Docker instructions.

## Example Workflow

1. **Define desired state** in YAML (see `examples/topology.yaml`):
   ```yaml
   topology:
     nodes:
       - name: h1
         type: host
       - name: h2
         type: host
     links:
       - node1: h1
         node2: h2
         bandwidth: 100
         delay: 5ms
         loss: 0
   devices:
     h1:
       interfaces:
         - name: eth0
           ip: 10.0.0.1
   ```

2. **Deploy configuration** to create simulated topology
3. **Collect baseline telemetry** (latency, packet loss, path visibility)
4. **Inject failure** (link down, congestion, route changes)
5. **Collect post-change telemetry**
6. **Validate** network behavior against baseline

## YAML Desired State Format

The desired state YAML file defines:

- **Topology**: Nodes (hosts, switches, routers) and links with characteristics
- **Devices**: Per-device configuration (interfaces, routes, hostnames)

See `examples/topology.yaml` for a complete example.

**Key Fields:**
- `topology.nodes`: List of network nodes with names and types
- `topology.links`: Links between nodes with bandwidth (Mbps), delay (ms), and loss (%)
- `devices`: Device-specific configurations (interfaces with IP/netmask, static routes)

## Project Structure

```
NetworkControlPlane/
├── network_control_plane/    # Main package
│   ├── desired_state/       # YAML schema and parsing
│   │   └── parser.py        # DesiredStateParser class
│   ├── config_rendering/    # Jinja2 template rendering
│   │   ├── renderer.py      # ConfigRenderer class
│   │   └── templates/       # Jinja2 templates
│   │       └── default.j2   # Default device config template
│   ├── automation/          # Netmiko-style device management
│   │   ├── device.py        # SimulatedDevice class
│   │   └── session.py       # DeviceSession context manager
│   ├── topology/            # Mininet network simulation
│   │   └── manager.py       # TopologyManager class
│   ├── telemetry/           # Telemetry collection
│   │   ├── collector.py     # TelemetryCollector class
│   │   └── metrics.py       # Telemetry data structures
│   ├── validation/          # Validation logic
│   │   └── validator.py     # NetworkValidator class
│   ├── cli/                 # Command-line interface
│   │   └── main.py          # Click-based CLI commands
│   └── ui/                  # Web control surface
│       ├── app.py           # Flask application and REST API
│       └── templates/       # HTML templates
│           └── index.html   # Web UI frontend
├── docs/                     # Documentation
│   └── DOCKER_SETUP.md       # Docker setup instructions
├── scripts/                  # Utility scripts
│   ├── docker-run.sh         # Docker container runner
│   ├── push-to-dockerhub.sh  # Docker Hub publishing script
│   └── start-ovs.sh          # Open vSwitch startup script
├── tests/                    # Test files
├── examples/                 # Example topologies and workflows
│   ├── topology.yaml         # Example desired state
│   └── example_workflow.py   # Example usage script
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker Compose configuration
├── requirements.txt          # Python dependencies
└── setup.py                  # Package setup
```

## Technical Implementation Notes

### Network Simulation Details

- **Network Namespaces**: Each node runs in its own Linux network namespace, providing complete network stack isolation
- **Virtual Links**: Links are implemented using `veth` pairs with one end in each namespace
- **Link Characteristics**: Linux Traffic Control (TC) enforces bandwidth limits, delay, and packet loss on links
- **Switching**: Open vSwitch provides virtual switching functionality for multi-port switches

### Configuration Deployment

- **Idempotent Operations**: Configuration deployment is idempotent - repeated deployments produce the same result
- **Template-Based**: Device configurations are generated from Jinja2 templates, allowing customization per device type
- **Session Management**: Device sessions ensure atomic configuration changes

### Telemetry Collection

- **Real System Tools**: Uses actual `ping`, `traceroute`, and `ip` commands within network namespaces
- **Metrics**: Collects latency (RTT), packet loss, path visibility (hops), and interface statistics
- **Real-time**: Telemetry is collected on-demand via API calls

### Validation Framework

- **Baseline Capture**: Establishes baseline metrics before changes
- **Comparison Logic**: Compares post-change metrics against baseline with configurable thresholds
- **Deterministic**: Provides clear pass/fail results based on measurable differences

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
