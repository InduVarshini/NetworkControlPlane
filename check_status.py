#!/usr/bin/env python3
"""Check current network status."""

import sys
sys.path.insert(0, "/workspace")
from network_control_plane.topology import TopologyManager
from network_control_plane.desired_state import DesiredStateParser
from network_control_plane.config_rendering import ConfigRenderer
from network_control_plane.automation import SimulatedDevice, DeviceSession
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

for device_name, device_config in devices_config.items():
    node = tm.get_node(device_name)
    device = SimulatedDevice(device_name=device_name, device_type=device_config.get("type", "switch"), node=node)
    with DeviceSession(device) as session:
        config = rendered_configs[device_name]
        session.deploy_config(config)

h1 = tm.get_node("h1")
h2 = tm.get_node("h2")
s1 = tm.get_node("s1")
s2 = tm.get_node("s2")

print("=== IP Configuration Status ===")
h1_ip = h1.cmd("ip addr show h1-eth0 | grep 'inet ' | grep -v 127 | awk '{print $2}' | cut -d/ -f1").strip()
h2_ip = h2.cmd("ip addr show h2-eth0 | grep 'inet ' | grep -v 127 | awk '{print $2}' | cut -d/ -f1").strip()
s1_ip = s1.cmd("ip addr show s1-eth1 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1").strip()
s2_ip = s2.cmd("ip addr show s2-eth1 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1").strip()

print(f"h1: {h1_ip}")
print(f"h2: {h2_ip}")
print(f"s1-eth1: {s1_ip}")
print(f"s2-eth1: {s2_ip}")

print("\n=== Connectivity Tests ===")
s1_to_s2 = s1.cmd("ping -c 1 -W 1 10.0.1.2")
print(f"s1 -> s2: {'✓ WORKS' if '64 bytes' in s1_to_s2 else '✗ FAILS'}")

h1_to_s1 = h1.cmd("ping -c 1 -W 1 10.0.0.1")
print(f"h1 -> s1: {'✓ WORKS' if '64 bytes' in h1_to_s1 else '✗ FAILS'}")

h1_to_h2 = h1.cmd("ping -c 1 -W 1 10.0.2.10")
print(f"h1 -> h2: {'✓ WORKS' if '64 bytes' in h1_to_h2 else '✗ FAILS'}")

print("\n=== Issue Summary ===")
if '64 bytes' not in h1_to_s1:
    print("PROBLEM: Hosts cannot reach switches on same subnet (ARP issue)")
if '64 bytes' not in h1_to_h2:
    print("PROBLEM: End-to-end connectivity failing (routing issue)")
