"""
Control Plane Web UI

Minimal web control surface for network control plane operations.
Provides visibility of telemetry and state with explicit control actions.
"""

from .app import create_app

__all__ = ["create_app"]

