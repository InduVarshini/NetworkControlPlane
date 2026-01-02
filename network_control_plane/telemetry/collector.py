"""
Telemetry Collector

Collects real-time network telemetry from the simulated topology.
Implements telemetry collection using real system signals (ping, traceroute,
interface counters) to provide observability feedback to the control plane.
"""

import logging
import subprocess
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from .metrics import (
    TelemetryMetrics, LatencyMetrics, PathMetrics, PathHop,
    InterfaceCounter, ThroughputMetrics
)

logger = logging.getLogger(__name__)


class TelemetryError(Exception):
    """Raised when telemetry collection fails."""
    pass


class TelemetryCollector:
    """
    Collects network telemetry from the simulated topology.
    
    Performs telemetry collection using real system tools (ping, traceroute)
    to gather latency, packet loss, path visibility, and interface counters.
    This provides the observability feedback loop for the control plane.
    """
    
    def __init__(self, topology_manager=None):
        """
        Initialize telemetry collector.
        
        Args:
            topology_manager: TopologyManager instance for accessing nodes
        """
        self.topology_manager = topology_manager
        logger.info("Initialized telemetry collector")
    
    def collect_latency(self, source: str, destination: str, 
                       count: int = 5) -> LatencyMetrics:
        """
        Collect latency and packet loss metrics using ping.
        
        This performs telemetry collection to measure network latency
        and packet loss between two nodes.
        
        Args:
            source: Source node name or IP
            destination: Destination node name or IP
            count: Number of ping packets to send
            
        Returns:
            LatencyMetrics object with latency and packet loss data
            
        Raises:
            TelemetryError: If ping fails or output cannot be parsed
        """
        try:
            # Get node object if using topology manager
            if self.topology_manager:
                source_node = self.topology_manager.get_node(source)
                # Try to resolve destination to IP if it's a node name
                dest_ip = destination
                try:
                    dest_node = self.topology_manager.get_node(destination)
                    # Get the first interface IP of the destination node
                    ip_output = dest_node.cmd('ip addr show | grep "inet " | grep -v "127.0.0.1" | head -1')
                    if ip_output:
                        # Extract IP from output (format: inet 10.0.0.10/24 ...)
                        ip_match = re.search(r'inet\s+([\d.]+)', ip_output)
                        if ip_match:
                            dest_ip = ip_match.group(1)
                except Exception:
                    # If we can't resolve, use destination as-is (might already be an IP)
                    pass
                
                cmd = f"ping -c {count} -W 2 {dest_ip}"
                result = source_node.cmd(cmd)
            else:
                # Fallback to system ping
                cmd = ["ping", "-c", str(count), destination]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                result = result.stdout
            
            # Parse ping output
            metrics = self._parse_ping_output(result, source, destination)
            logger.info(f"Collected latency metrics: {source} -> {destination} "
                       f"(avg={metrics.avg_latency_ms:.2f}ms, loss={metrics.packet_loss_percent:.1f}%)")
            return metrics
            
        except Exception as e:
            raise TelemetryError(f"Failed to collect latency metrics: {e}")
    
    def _parse_ping_output(self, output: str, source: str, 
                          destination: str) -> LatencyMetrics:
        """
        Parse ping command output.
        
        Args:
            output: Ping command output
            source: Source node name
            destination: Destination node name
            
        Returns:
            Parsed LatencyMetrics object
        """
        # Extract packet loss percentage
        loss_match = re.search(r'(\d+(?:\.\d+)?)% packet loss', output)
        packet_loss = float(loss_match.group(1)) if loss_match else 0.0
        
        # Extract latency statistics
        # Format: min/avg/max/mdev = X.X/X.X/X.X/X.X ms
        latency_match = re.search(r'min/avg/max[^=]*=\s*([\d.]+)/([\d.]+)/([\d.]+)', output)
        
        if latency_match:
            min_latency = float(latency_match.group(1))
            avg_latency = float(latency_match.group(2))
            max_latency = float(latency_match.group(3))
        else:
            # Fallback if format differs
            min_latency = avg_latency = max_latency = 0.0
        
        return LatencyMetrics(
            source=source,
            destination=destination,
            min_latency_ms=min_latency,
            avg_latency_ms=avg_latency,
            max_latency_ms=max_latency,
            packet_loss_percent=packet_loss,
            timestamp=datetime.now()
        )
    
    def collect_path(self, source: str, destination: str, 
                    max_hops: int = 30) -> PathMetrics:
        """
        Collect path visibility metrics using traceroute.
        
        This performs telemetry collection to determine the routing path
        between two nodes, providing routing/path validation data.
        
        Args:
            source: Source node name or IP
            destination: Destination node name or IP
            max_hops: Maximum number of hops to trace
            
        Returns:
            PathMetrics object with path visibility data
            
        Raises:
            TelemetryError: If traceroute fails or output cannot be parsed
        """
        try:
            # Get node object if using topology manager
            if self.topology_manager:
                source_node = self.topology_manager.get_node(source)
                cmd = f"traceroute -m {max_hops} {destination}"
                result = source_node.cmd(cmd)
            else:
                # Fallback to system traceroute
                cmd = ["traceroute", "-m", str(max_hops), destination]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                result = result.stdout
            
            # Parse traceroute output
            metrics = self._parse_traceroute_output(result, source, destination)
            logger.info(f"Collected path metrics: {source} -> {destination} "
                       f"({metrics.total_hops} hops)")
            return metrics
            
        except Exception as e:
            raise TelemetryError(f"Failed to collect path metrics: {e}")
    
    def _parse_traceroute_output(self, output: str, source: str,
                                 destination: str) -> PathMetrics:
        """
        Parse traceroute command output.
        
        Args:
            output: Traceroute command output
            source: Source node name
            destination: Destination node name
            
        Returns:
            Parsed PathMetrics object
        """
        hops = []
        hop_number = 1
        
        for line in output.split('\n'):
            line = line.strip()
            if not line or line.startswith('traceroute'):
                continue
            
            # Match traceroute line format
            # Format:  1  hostname (ip)  X.X ms
            hop_match = re.match(r'^\s*(\d+)\s+([^\s(]+)\s*\(([^)]+)\)\s+([\d.]+)\s*ms', line)
            if hop_match:
                hop_num = int(hop_match.group(1))
                hostname = hop_match.group(2)
                ip_address = hop_match.group(3)
                latency = float(hop_match.group(4))
                
                hops.append(PathHop(
                    hop_number=hop_num,
                    hostname=hostname if hostname != '*' else None,
                    ip_address=ip_address,
                    latency_ms=latency
                ))
                hop_number = hop_num + 1
        
        return PathMetrics(
            source=source,
            destination=destination,
            hops=hops,
            total_hops=len(hops),
            timestamp=datetime.now()
        )
    
    def collect_interface_counters(self, node_name: str) -> List[InterfaceCounter]:
        """
        Collect interface counter metrics.
        
        This performs telemetry collection to gather interface statistics
        including bytes sent/received, packets sent/received, and drops.
        
        Args:
            node_name: Name of the node to collect counters from
            
        Returns:
            List of InterfaceCounter objects
            
        Raises:
            TelemetryError: If counter collection fails
        """
        try:
            counters = []
            
            if self.topology_manager:
                node = self.topology_manager.get_node(node_name)
                # Get interface statistics
                result = node.cmd("cat /proc/net/dev")
            else:
                # Fallback to system /proc/net/dev
                result = subprocess.run(
                    ["cat", "/proc/net/dev"],
                    capture_output=True,
                    text=True
                ).stdout
            
            # Parse /proc/net/dev output
            counters = self._parse_proc_net_dev(result, node_name)
            
            logger.info(f"Collected interface counters for node '{node_name}': {len(counters)} interfaces")
            return counters
            
        except Exception as e:
            raise TelemetryError(f"Failed to collect interface counters: {e}")
    
    def _parse_proc_net_dev(self, output: str, node_name: str) -> List[InterfaceCounter]:
        """
        Parse /proc/net/dev output.
        
        Args:
            output: Contents of /proc/net/dev
            node_name: Name of the node
            
        Returns:
            List of InterfaceCounter objects
        """
        counters = []
        timestamp = datetime.now()
        
        for line in output.split('\n'):
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            # Format: interface: bytes packets errs drops ...
            parts = line.split(':')
            if len(parts) != 2:
                continue
            
            interface_name = parts[0].strip()
            stats = parts[1].split()
            
            if len(stats) < 16:
                continue
            
            # /proc/net/dev format:
            # Receive: bytes packets errs drop fifo frame compressed multicast
            # Transmit: bytes packets errs drop fifo colls carrier compressed
            bytes_received = int(stats[0])
            packets_received = int(stats[1])
            drops_received = int(stats[3])
            
            bytes_sent = int(stats[8])
            packets_sent = int(stats[9])
            drops_sent = int(stats[11])
            
            counters.append(InterfaceCounter(
                interface_name=interface_name,
                bytes_sent=bytes_sent,
                bytes_received=bytes_received,
                packets_sent=packets_sent,
                packets_received=packets_received,
                drops_sent=drops_sent,
                drops_received=drops_received,
                timestamp=timestamp
            ))
        
        return counters
    
    def collect_all(self, source: str, destination: str) -> TelemetryMetrics:
        """
        Collect all available telemetry metrics.
        
        Performs comprehensive telemetry collection including latency,
        packet loss, path visibility, and interface counters.
        
        Args:
            source: Source node name
            destination: Destination node name
            
        Returns:
            TelemetryMetrics object with all collected metrics
        """
        metrics = TelemetryMetrics()
        
        try:
            metrics.latency = self.collect_latency(source, destination)
        except Exception as e:
            logger.warning(f"Failed to collect latency metrics: {e}")
        
        try:
            metrics.path = self.collect_path(source, destination)
        except Exception as e:
            logger.warning(f"Failed to collect path metrics: {e}")
        
        try:
            if self.topology_manager:
                # Collect interface counters for source node
                metrics.interfaces = self.collect_interface_counters(source)
        except Exception as e:
            logger.warning(f"Failed to collect interface counters: {e}")
        
        logger.info(f"Completed telemetry collection: {source} -> {destination}")
        return metrics

