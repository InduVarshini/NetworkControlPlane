"""
Control Plane CLI Interface

Command-line interface for the network control plane.
Provides explicit control actions for deploying desired state, injecting
failures, and validating network behavior.
"""

from .main import main

__all__ = ["main"]

