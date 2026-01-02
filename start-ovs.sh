#!/bin/bash
# Startup script to initialize Open vSwitch in Docker container

set -e

echo "Initializing Open vSwitch..."

# Create necessary directories
mkdir -p /var/run/openvswitch
mkdir -p /var/log/openvswitch

# Check if OVS is already running
if ovs-vsctl show > /dev/null 2>&1; then
    echo "Open vSwitch is already running"
    exit 0
fi

# Start OVS database server
echo "Starting OVS database server..."
ovsdb-server --detach \
    --pidfile=/var/run/openvswitch/ovsdb-server.pid \
    --remote=punix:/var/run/openvswitch/db.sock \
    --log-file=/var/log/openvswitch/ovsdb-server.log

# Wait for database server to be ready
sleep 2

# Start OVS daemon
echo "Starting OVS daemon..."
ovs-vswitchd --detach \
    --pidfile=/var/run/openvswitch/ovs-vswitchd.pid \
    --log-file=/var/log/openvswitch/ovs-vswitchd.log

# Wait for daemon to be ready
sleep 2

# Verify OVS is running
if ovs-vsctl show > /dev/null 2>&1; then
    echo "✓ Open vSwitch started successfully"
else
    echo "✗ Failed to start Open vSwitch"
    exit 1
fi
