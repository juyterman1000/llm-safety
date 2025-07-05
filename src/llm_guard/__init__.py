"""
LLM Guard - Lightweight safety toolkit for LLM applications
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.safety_guard import SafetyGuard, SafetyResult, SafetyMetrics

__all__ = [
    "SafetyGuard",
    "SafetyResult", 
    "SafetyMetrics",
]

# Convenience function
def create_guard(**kwargs):
    """
    Create a SafetyGuard instance with optional configuration
    
    Example:
        guard = create_guard(thresholds={'toxicity': 0.8})
    """
    return SafetyGuard(**kwargs)
