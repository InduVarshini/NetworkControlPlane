# Quick Start with Docker

## Step 1: Start Docker Desktop

Make sure Docker Desktop is running on your Mac. You should see the Docker icon in your menu bar.

## Step 2: Build the Image

```bash
cd /Users/indu/cursor-projects/NetworkControlPlane
docker build -t network-control-plane:latest .
```

This will take a few minutes the first time as it downloads the base Mininet image.

## Step 3: Run the Container

**Option A: Using the helper script (easiest)**

```bash
./docker-run.sh
```

**Option B: Using docker-compose**

```bash
docker-compose up -d
docker-compose exec network-control-plane bash
```

**Option C: Using docker directly**

```bash
docker run -it --rm --privileged \
  -v $(pwd):/workspace \
  -w /workspace \
  network-control-plane:latest \
  /bin/bash
```

## Step 4: Inside the Container

Once you're inside the container, you can run:

```bash
# Deploy the network topology
sudo python3 -m network_control_plane.cli deploy examples/topology.yaml

# Test connectivity
sudo python3 -m network_control_plane.cli ping h1 h2

# Run the example workflow
sudo python3 examples/example_workflow.py
```

**Important:** Commands that create network topologies require `sudo` inside the container.

## Troubleshooting

### "Cannot connect to Docker daemon"
- Make sure Docker Desktop is running
- Check: `docker ps` should work without errors

### "Permission denied" 
- Make sure you're using `--privileged` flag
- Use `sudo` for Mininet commands inside the container

### Port forwarding for Web UI
If you want to access the web UI from your Mac:

```bash
docker run -it --rm --privileged \
  -v $(pwd):/workspace \
  -w /workspace \
  -p 5000:5000 \
  network-control-plane:latest \
  /bin/bash
```

Then inside: `python3 -m network_control_plane.ui`
And access from Mac: `http://localhost:5000`

## Next Steps

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed documentation.

