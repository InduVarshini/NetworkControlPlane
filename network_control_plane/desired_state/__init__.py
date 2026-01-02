"""
Desired State Management

Handles parsing and validation of YAML-based desired network configuration.
Implements the declarative desired state layer of the network control plane.
"""

from .parser import DesiredStateParser, DesiredStateError

__all__ = ["DesiredStateParser", "DesiredStateError"]

