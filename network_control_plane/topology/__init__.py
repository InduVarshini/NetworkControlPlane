"""
Network Topology Management

Manages simulated network topology using Mininet.
Implements the simulated network topology layer that provides the foundation
for network control plane operations.
"""

from .manager import TopologyManager, TopologyError

__all__ = ["TopologyManager", "TopologyError"]

