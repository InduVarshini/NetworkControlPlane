#!/usr/bin/env python3
"""Test script to verify IP configuration and telemetry collection."""

import sys
sys.path.insert(0, "/workspace")
from network_control_plane.topology import TopologyManager
from network_control_plane.desired_state import DesiredStateParser
from network_control_plane.config_rendering import ConfigRenderer
from network_control_plane.automation import SimulatedDevice, DeviceSession
from network_control_plane.telemetry import TelemetryCollector
import subprocess

subprocess.run(["mn", "-c"], capture_output=True)

parser = DesiredStateParser()
state = parser.load("examples/topology.yaml")
topo_config = parser.get_topology()
devices_config = parser.get_devices()

tm = TopologyManager()
tm.create_topology(topo_config)
tm.start()

renderer = ConfigRenderer()
rendered_configs = renderer.render_all(devices_config, topo_config)

# Configure all devices (switches and hosts)
for device_name, device_config in devices_config.items():
    node = tm.get_node(device_name)
    device = SimulatedDevice(device_name=device_name, device_type=device_config.get("type", "switch"), node=node)
    with DeviceSession(device) as session:
        config = rendered_configs[device_name]
        session.deploy_config(config)

h1 = tm.get_node("h1")
h2 = tm.get_node("h2")
print("=== h1 IPs ===")
print(h1.cmd("ip addr show h1-eth0 | grep inet"))
print("\n=== h2 IPs ===")
print(h2.cmd("ip addr show h2-eth0 | grep inet"))
print("\n=== h1 routes ===")
print(h1.cmd("ip route show"))
print("\n=== h2 routes ===")
print(h2.cmd("ip route show"))

print("\n=== Testing ping ===")
# Get h2's IP address
h2_ip_output = h2.cmd("ip addr show h2-eth0 | grep 'inet ' | grep -v '127.0.0.1'")
h2_ip = h2_ip_output.split()[1].split('/')[0] if h2_ip_output else "10.0.2.10"
print(f"h2 IP: {h2_ip}")
result = h1.cmd(f"ping -c 5 -W 2 {h2_ip}")
print(result)

print("\n=== Telemetry Collection ===")
collector = TelemetryCollector(tm)
metrics = collector.collect_latency("h1", "h2", count=5)
print(f"Latency: avg={metrics.avg_latency_ms:.2f}ms, min={metrics.min_latency_ms:.2f}ms, max={metrics.max_latency_ms:.2f}ms")
print(f"Packet Loss: {metrics.packet_loss_percent:.2f}%")

path_metrics = collector.collect_path("h1", "h2")
print(f"\nPath: {path_metrics.total_hops} hops")
