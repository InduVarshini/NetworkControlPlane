"""
Network Telemetry Collection

Collects real-time network telemetry including latency, packet loss, throughput,
interface counters, and routing/path visibility. Implements the telemetry collection
layer that provides observability feedback to the control plane.
"""

from .collector import TelemetryCollector, TelemetryError
from .metrics import TelemetryMetrics

__all__ = ["TelemetryCollector", "TelemetryError", "TelemetryMetrics"]

