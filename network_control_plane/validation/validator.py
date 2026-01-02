"""
Network Validator

Validates network behavior by comparing baseline vs post-change telemetry.
Implements deterministic validation logic that compares network state before
and after changes to detect meaningful behavioral changes.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from ..telemetry.metrics import TelemetryMetrics, LatencyMetrics, PathMetrics

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation result status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


@dataclass
class ValidationResult:
    """
    Result of network validation.
    
    Provides structured pass/fail results from comparing baseline vs
    post-change network state.
    """
    status: ValidationStatus
    message: str
    baseline_metrics: Optional[TelemetryMetrics] = None
    current_metrics: Optional[TelemetryMetrics] = None
    details: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.details is None:
            self.details = []
    
    def is_pass(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.PASS


class NetworkValidator:
    """
    Validates network behavior under different scenarios.
    
    Compares baseline vs post-change state to detect meaningful behavioral
    changes. Provides deterministic validation results for failure and
    congestion scenarios.
    """
    
    def __init__(self, latency_threshold_ms: float = 50.0,
                 packet_loss_threshold_percent: float = 5.0,
                 path_change_allowed: bool = False):
        """
        Initialize network validator.
        
        Args:
            latency_threshold_ms: Maximum acceptable latency increase (ms)
            packet_loss_threshold_percent: Maximum acceptable packet loss (%)
            path_change_allowed: Whether path changes are acceptable
        """
        self.latency_threshold_ms = latency_threshold_ms
        self.packet_loss_threshold_percent = packet_loss_threshold_percent
        self.path_change_allowed = path_change_allowed
        logger.info("Initialized network validator")
    
    def validate(self, baseline: TelemetryMetrics, 
                current: TelemetryMetrics) -> ValidationResult:
        """
        Validate current state against baseline.
        
        Performs routing/path validation and connectivity validation by
        comparing baseline vs post-change telemetry metrics.
        
        Args:
            baseline: Baseline telemetry metrics
            current: Current telemetry metrics after change
            
        Returns:
            ValidationResult with pass/fail status and details
        """
        details = []
        status = ValidationStatus.PASS
        
        # Validate latency
        if baseline.latency and current.latency:
            latency_result = self._validate_latency(baseline.latency, current.latency)
            if not latency_result.is_pass():
                status = ValidationStatus.FAIL
            details.extend(latency_result.details)
        
        # Validate packet loss
        if baseline.latency and current.latency:
            loss_result = self._validate_packet_loss(baseline.latency, current.latency)
            if not loss_result.is_pass():
                status = ValidationStatus.FAIL
            details.extend(loss_result.details)
        
        # Validate path
        if baseline.path and current.path:
            path_result = self._validate_path(baseline.path, current.path)
            if not path_result.is_pass() and not self.path_change_allowed:
                status = ValidationStatus.FAIL
            details.extend(path_result.details)
        
        # Determine overall message
        if status == ValidationStatus.PASS:
            message = "Network validation passed: all metrics within acceptable thresholds"
        else:
            message = "Network validation failed: metrics exceeded acceptable thresholds"
        
        result = ValidationResult(
            status=status,
            message=message,
            baseline_metrics=baseline,
            current_metrics=current,
            details=details
        )
        
        logger.info(f"Validation completed: {status.value.upper()} - {message}")
        return result
    
    def _validate_latency(self, baseline: LatencyMetrics, 
                          current: LatencyMetrics) -> ValidationResult:
        """
        Validate latency metrics.
        
        Checks if latency exceeded baseline during congestion scenario
        or failure scenario.
        
        Args:
            baseline: Baseline latency metrics
            current: Current latency metrics
            
        Returns:
            ValidationResult for latency
        """
        details = []
        status = ValidationStatus.PASS
        
        latency_increase = current.avg_latency_ms - baseline.avg_latency_ms
        
        if latency_increase > self.latency_threshold_ms:
            status = ValidationStatus.FAIL
            details.append(
                f"Latency exceeded baseline: {latency_increase:.2f}ms increase "
                f"(baseline: {baseline.avg_latency_ms:.2f}ms, "
                f"current: {current.avg_latency_ms:.2f}ms)"
            )
        else:
            details.append(
                f"Latency within threshold: {current.avg_latency_ms:.2f}ms "
                f"(baseline: {baseline.avg_latency_ms:.2f}ms)"
            )
        
        return ValidationResult(
            status=status,
            message=f"Latency validation: {status.value}",
            details=details
        )
    
    def _validate_packet_loss(self, baseline: LatencyMetrics,
                              current: LatencyMetrics) -> ValidationResult:
        """
        Validate packet loss metrics.
        
        Checks if packet loss exceeded baseline during failure scenario.
        
        Args:
            baseline: Baseline latency metrics (includes packet loss)
            current: Current latency metrics
            
        Returns:
            ValidationResult for packet loss
        """
        details = []
        status = ValidationStatus.PASS
        
        loss_increase = current.packet_loss_percent - baseline.packet_loss_percent
        
        if loss_increase > self.packet_loss_threshold_percent:
            status = ValidationStatus.FAIL
            details.append(
                f"Packet loss exceeded threshold: {loss_increase:.2f}% increase "
                f"(baseline: {baseline.packet_loss_percent:.2f}%, "
                f"current: {current.packet_loss_percent:.2f}%)"
            )
        else:
            details.append(
                f"Packet loss within threshold: {current.packet_loss_percent:.2f}% "
                f"(baseline: {baseline.packet_loss_percent:.2f}%)"
            )
        
        return ValidationResult(
            status=status,
            message=f"Packet loss validation: {status.value}",
            details=details
        )
    
    def _validate_path(self, baseline: PathMetrics,
                      current: PathMetrics) -> ValidationResult:
        """
        Validate routing path.
        
        Detects path changes after link failure to validate routing behavior.
        
        Args:
            baseline: Baseline path metrics
            current: Current path metrics
            
        Returns:
            ValidationResult for path
        """
        details = []
        status = ValidationStatus.PASS
        
        baseline_hops = [hop.ip_address for hop in baseline.hops]
        current_hops = [hop.ip_address for hop in current.hops]
        
        if baseline_hops != current_hops:
            status = ValidationStatus.WARNING
            details.append(
                f"Path change detected: {len(baseline_hops)} hops -> {len(current_hops)} hops"
            )
            details.append(f"Baseline path: {' -> '.join(baseline_hops)}")
            details.append(f"Current path: {' -> '.join(current_hops)}")
        else:
            details.append("Path unchanged: routing behavior consistent")
        
        return ValidationResult(
            status=status,
            message=f"Path validation: {status.value}",
            details=details
        )
    
    def validate_connectivity(self, metrics: TelemetryMetrics) -> ValidationResult:
        """
        Validate basic connectivity.
        
        Performs baseline connectivity validation to ensure network
        is functioning correctly.
        
        Args:
            metrics: Telemetry metrics to validate
            
        Returns:
            ValidationResult for connectivity
        """
        details = []
        status = ValidationStatus.PASS
        
        if metrics.latency:
            if metrics.latency.packet_loss_percent >= 100.0:
                status = ValidationStatus.FAIL
                details.append("Connectivity failed: 100% packet loss")
            elif metrics.latency.packet_loss_percent > 50.0:
                status = ValidationStatus.FAIL
                details.append(f"Connectivity degraded: {metrics.latency.packet_loss_percent:.2f}% packet loss")
            else:
                details.append(
                    f"Connectivity OK: {metrics.latency.packet_loss_percent:.2f}% packet loss, "
                    f"{metrics.latency.avg_latency_ms:.2f}ms latency"
                )
        else:
            status = ValidationStatus.FAIL
            details.append("Connectivity validation failed: no latency metrics available")
        
        return ValidationResult(
            status=status,
            message=f"Connectivity validation: {status.value}",
            details=details
        )

