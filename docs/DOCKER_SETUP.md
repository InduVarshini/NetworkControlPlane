# Docker Setup Guide for NetworkControlPlane

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# Enter the container
docker-compose exec network-control-plane bash

# Now you can run commands inside the container
python3 -m network_control_plane.cli deploy examples/topology.yaml
python3 -m network_control_plane.cli ping h1 h2
python3 examples/example_workflow.py

# Stop the container
docker-compose down
```

### Option 2: Using Docker Directly

```bash
# Build the image
docker build -t network-control-plane:latest .

# Run interactively
docker run -it --rm --privileged \
  -v $(pwd):/workspace \
  -w /workspace \
  network-control-plane:latest \
  /bin/bash

# Inside the container, run:
python3 -m network_control_plane.cli deploy examples/topology.yaml
```

### Option 3: Using the Helper Script

```bash
# Make script executable (if needed)
chmod +x scripts/docker-run.sh

# Run the script
./scripts/docker-run.sh
```

## Prerequisites

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop
   - Make sure Docker Desktop is running before proceeding

2. **Verify Docker is working:**
   ```bash
   docker --version
   docker ps
   ```

## Step-by-Step Setup

### 1. Build the Docker Image

```bash
cd /path/to/NetworkControlPlane
docker build -t network-control-plane:latest .
```

This will:
- Use Mininet's official image as base
- Install Python dependencies
- Copy your project files
- Set up the working environment

### 2. Run the Container

**Interactive mode (recommended for first-time use):**

```bash
docker run -it --rm --privileged \
  -v $(pwd):/workspace \
  -w /workspace \
  network-control-plane:latest \
  /bin/bash
```

**Using docker-compose:**

```bash
docker-compose up -d
docker-compose exec network-control-plane bash
```

### 3. Test the Installation

Inside the container:

```bash
# Check Python and dependencies
python3 --version
python3 -c "import mininet; print('Mininet OK')"

# Test YAML parsing
python3 -c "
from network_control_plane.desired_state import DesiredStateParser
p = DesiredStateParser()
state = p.load('examples/topology.yaml')
print('✓ YAML parsing works')
"

# Deploy a topology (requires root inside container)
sudo python3 -m network_control_plane.cli deploy examples/topology.yaml
```

## Running Commands

### Deploy Network Topology

```bash
sudo python3 -m network_control_plane.cli deploy examples/topology.yaml
```

**Note:** Commands that create network namespaces require `sudo` inside the container.

### Collect Telemetry

```bash
# Latency and packet loss
python3 -m network_control_plane.cli ping h1 h2

# Path visibility
python3 -m network_control_plane.cli trace h1 h2

# Validate network behavior
python3 -m network_control_plane.cli validate h1 h2
```

### Run Example Workflow

```bash
sudo python3 examples/example_workflow.py
```

### Start Web UI

```bash
# In one terminal (container)
python3 -m network_control_plane.ui

# In another terminal, access from host
# The UI will be available at http://localhost:5000
```

## Troubleshooting

### Docker Permission Errors

If you get permission errors:
```bash
# Make sure Docker Desktop is running
# Check Docker daemon status
docker info
```

### Container Can't Access Network

Make sure you're using `--privileged` flag:
```bash
docker run -it --rm --privileged ...
```

### Port Forwarding for Web UI

If running the web UI, you may need to expose ports:
```bash
docker run -it --rm --privileged \
  -v $(pwd):/workspace \
  -w /workspace \
  -p 5000:5000 \
  network-control-plane:latest \
  /bin/bash
```

### Mininet Requires Root

Remember: Mininet operations require `sudo` inside the container:
```bash
sudo python3 -m network_control_plane.cli deploy examples/topology.yaml
```

## Docker Compose Commands

```bash
# Start container in background
docker-compose up -d

# View logs
docker-compose logs

# Execute command in running container
docker-compose exec network-control-plane bash

# Stop container
docker-compose down

# Rebuild image
docker-compose build --no-cache
```

## File Persistence

Files in your project directory are mounted as a volume, so:
- Changes to code are immediately available in the container
- Results and logs persist on your host machine
- No need to rebuild the image for code changes

## Next Steps

1. Build the Docker image
2. Run the container interactively
3. Test with: `sudo python3 -m network_control_plane.cli deploy examples/topology.yaml`
4. Explore the CLI commands and web UI

For more information, see the main [README.md](README.md).

