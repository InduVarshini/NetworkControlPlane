"""
Network Validation Logic

Validates network behavior by comparing baseline vs post-change state.
Implements validation logic that answers "Did the network behave as expected
under this scenario?" through deterministic comparison.
"""

from .validator import NetworkValidator, ValidationResult, ValidationError

__all__ = ["NetworkValidator", "ValidationResult", "ValidationError"]

