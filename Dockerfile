# Dockerfile for NetworkControlPlane
# Builds Mininet from Ubuntu base

FROM ubuntu:22.04

# Set working directory
WORKDIR /workspace

# Install Mininet and dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    mininet \
    openvswitch-switch \
    python3-pip \
    python3-dev \
    iproute2 \
    iputils-ping \
    traceroute \
    net-tools \
    && pip3 install --no-cache-dir jinja2 pyyaml flask click python-dotenv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Start Open vSwitch service (needed for Mininet switches)
RUN mkdir -p /var/run/openvswitch && \
    ovsdb-tool create /etc/openvswitch/conf.db /usr/share/openvswitch/vswitch.ovsschema

# Copy project files
COPY . /workspace/

# Install the package in development mode
RUN pip3 install -e .

# Set Python path
ENV PYTHONPATH=/workspace:$PYTHONPATH

# Default command (can be overridden)
CMD ["/bin/bash"]

