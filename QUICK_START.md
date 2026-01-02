# Quick Start Guide

## 🚀 Fastest Way to Get Started

### Option 1: Docker (Recommended)

```bash
# Pull from Docker Hub (replace YOUR_USERNAME)
docker pull YOUR_USERNAME/network-control-plane:latest

# Run the web UI
docker run -it --rm --privileged \
  -p 5001:5001 \
  -v $(pwd):/workspace \
  -w /workspace \
  YOUR_USERNAME/network-control-plane:latest \
  python3 -m network_control_plane.ui

# Open http://localhost:5001 in your browser
```

### Option 2: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Start web UI
python -m network_control_plane.ui

# Open http://localhost:5001 in your browser
```

## 📤 Upload and Deploy Topology

1. **Open the Web UI**: http://localhost:5001
2. **Click "Choose File"** and select a YAML topology file
3. **Click "Deploy"** to create the network topology
4. **Collect Telemetry** by entering source and destination nodes
5. **Validate** network behavior

## 📝 Example YAML File

See `examples/topology.yaml` for a complete example.

## 🐳 Publishing Your Own Docker Image

```bash
# Login to Docker Hub
docker login

# Build and push
./push-to-dockerhub.sh YOUR_DOCKERHUB_USERNAME

# Or manually
docker build -t YOUR_USERNAME/network-control-plane:latest .
docker push YOUR_USERNAME/network-control-plane:latest
```

See [DOCKERHUB.md](DOCKERHUB.md) for detailed instructions.

## 📚 More Information

- **Full Documentation**: [README.md](README.md)
- **Docker Setup**: [QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)
- **Docker Hub Publishing**: [DOCKERHUB.md](DOCKERHUB.md)
- **GitHub Setup**: [GITHUB_SETUP.md](GITHUB_SETUP.md)

