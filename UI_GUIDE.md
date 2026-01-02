# Web UI Guide - Viewing Metrics

## Quick Start

### 1. Start the Web UI

**In Docker:**
```bash
./docker-run.sh
# Inside container:
python3 -m network_control_plane.ui
```

**Or directly:**
```bash
docker run --rm --privileged -p 5000:5000 \
  -v $(pwd):/workspace -w /workspace \
  network-control-plane:latest \
  python3 -m network_control_plane.ui
```

### 2. Access the UI

Open your browser to: **http://localhost:5000**

## UI Features

### Main Dashboard

The UI provides:

1. **Topology Status Section**
   - Shows current topology state
   - Displays number of nodes
   - Status indicator (running/stopped)

2. **Telemetry Collection Section**
   - Input fields for source and destination
   - "Collect Telemetry" button
   - Displays metrics in JSON format:
     - Latency (min/avg/max)
     - Packet loss percentage
     - Path visibility (hops)

3. **Network Validation Section**
   - Input fields for source and destination
   - "Validate" button
   - Shows validation results:
     - Status (PASS/FAIL)
     - Detailed validation messages

### Using the UI

#### Step 1: Deploy Topology

1. Enter YAML file path: `examples/topology.yaml`
2. Click "Deploy" button
3. Wait for success message

#### Step 2: Collect Telemetry

1. Enter source node: `h1`
2. Enter destination node: `h2`
3. Click "Collect Telemetry"
4. View metrics in the results area

#### Step 3: Validate Network

1. Enter source node: `h1`
2. Enter destination node: `h2`
3. Click "Validate"
4. View validation results

## API Endpoints

The UI uses these REST API endpoints:

- `GET /api/topology/status` - Get topology status
- `POST /api/topology/deploy` - Deploy topology from YAML
- `POST /api/telemetry/collect` - Collect telemetry metrics
- `POST /api/validation/validate` - Validate network behavior

## Example Workflow

1. **Start UI:**
   ```bash
   python3 -m network_control_plane.ui
   ```

2. **Open browser:** http://localhost:5000

3. **Deploy topology:**
   - Enter: `examples/topology.yaml`
   - Click: "Deploy"
   - Wait for: "Success" message

4. **Collect telemetry:**
   - Source: `h1`
   - Destination: `h2`
   - Click: "Collect Telemetry"
   - View: Latency and path metrics

5. **Validate network:**
   - Source: `h1`
   - Destination: `h2`
   - Click: "Validate"
   - View: Validation results

## Troubleshooting

### UI Not Loading
- Check Flask is running: Look for "Running on http://0.0.0.0:5000"
- Check port 5000 is accessible
- Try: `curl http://localhost:5000`

### Topology Not Deploying
- Make sure Docker container has `--privileged` flag
- Check OVS is started (for switches)
- Check YAML file path is correct

### Telemetry Not Collecting
- Ensure topology is deployed first
- Check node names match topology
- Verify network connectivity

### Port Already in Use
- Change port: `app.run(port=5001)`
- Or kill existing process: `lsof -ti:5000 | xargs kill`

## UI Screenshots Description

The UI has a clean, minimal design with:

- **Top Section:** Topology deployment controls
- **Middle Section:** Telemetry collection interface
- **Bottom Section:** Network validation interface
- **Status Indicators:** Green for success, red for errors
- **JSON Display:** Formatted metrics output

## Next Steps

- Customize templates in `network_control_plane/ui/templates/`
- Add more visualization (charts, graphs)
- Enhance error handling
- Add topology visualization

The UI is ready to use! Start it and begin viewing your network metrics.

