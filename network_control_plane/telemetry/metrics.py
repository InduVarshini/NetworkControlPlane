"""
Telemetry Metrics

Data structures for network telemetry metrics.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class LatencyMetrics:
    """Latency and packet loss metrics from ping."""
    source: str
    destination: str
    min_latency_ms: float
    avg_latency_ms: float
    max_latency_ms: float
    packet_loss_percent: float
    timestamp: datetime


@dataclass
class PathHop:
    """Single hop in a network path."""
    hop_number: int
    hostname: Optional[str]
    ip_address: str
    latency_ms: Optional[float]


@dataclass
class PathMetrics:
    """Path visibility metrics from traceroute."""
    source: str
    destination: str
    hops: List[PathHop]
    total_hops: int
    timestamp: datetime


@dataclass
class InterfaceCounter:
    """Interface counter metrics."""
    interface_name: str
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    drops_sent: int
    drops_received: int
    timestamp: datetime


@dataclass
class ThroughputMetrics:
    """Throughput metrics from iperf3."""
    source: str
    destination: str
    bandwidth_mbps: float
    timestamp: datetime


@dataclass
class TelemetryMetrics:
    """
    Container for all telemetry metrics.
    
    Collects latency, packet loss, path visibility, interface counters,
    and throughput metrics for network observability.
    """
    latency: Optional[LatencyMetrics] = None
    path: Optional[PathMetrics] = None
    interfaces: List[InterfaceCounter] = None
    throughput: Optional[ThroughputMetrics] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.interfaces is None:
            self.interfaces = []

