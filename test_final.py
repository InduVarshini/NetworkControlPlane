#!/usr/bin/env python3
"""Final test with static ARP configuration."""

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

# Deploy configurations
for device_name, device_config in devices_config.items():
    node = tm.get_node(device_name)
    device = SimulatedDevice(device_name=device_name, device_type=device_config.get("type", "switch"), node=node)
    with DeviceSession(device) as session:
        config = rendered_configs[device_name]
        session.deploy_config(config)

# Post-deployment: Add static ARP entries
s1 = tm.get_node("s1")
s2 = tm.get_node("s2")
h1 = tm.get_node("h1")
h2 = tm.get_node("h2")

# Get switch MAC addresses and add static ARP entries
s1_mac_eth1 = s1.cmd("ip link show s1-eth1 | grep link/ether | awk '{print $2}'").strip()
s2_mac_eth1 = s2.cmd("ip link show s2-eth1 | grep link/ether | awk '{print $2}'").strip()

# Add static ARP entries on hosts
h1.cmd(f"ip neigh add 10.0.0.1 lladdr {s1_mac_eth1} dev h1-eth0 2>/dev/null || ip neigh replace 10.0.0.1 lladdr {s1_mac_eth1} dev h1-eth0 2>/dev/null || true")
h2.cmd(f"ip neigh add 10.0.2.1 lladdr {s2_mac_eth1} dev h2-eth0 2>/dev/null || ip neigh replace 10.0.2.1 lladdr {s2_mac_eth1} dev h2-eth0 2>/dev/null || true")

print("=== Testing connectivity ===")
print("\n1. h1 -> s1:")
result1 = h1.cmd("ping -c 3 -W 1 10.0.0.1")
print(result1)
works1 = "64 bytes" in result1

print("\n2. h1 -> h2:")
result2 = h1.cmd("ping -c 5 10.0.2.10")
print(result2)
works2 = "64 bytes" in result2

if works2:
    print("\n=== Telemetry Collection ===")
    collector = TelemetryCollector(tm)
    metrics = collector.collect_latency("h1", "h2", count=5)
    print(f"Latency: avg={metrics.avg_latency_ms:.2f}ms, min={metrics.min_latency_ms:.2f}ms, max={metrics.max_latency_ms:.2f}ms")
    print(f"Packet Loss: {metrics.packet_loss_percent:.2f}%")
    
    path_metrics = collector.collect_path("h1", "h2")
    print(f"Path: {path_metrics.total_hops} hops")
else:
    print("\n❌ Connectivity still failing - need to investigate further")

