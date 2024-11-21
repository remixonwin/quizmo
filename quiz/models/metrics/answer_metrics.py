"""
Answer metrics module for tracking user responses.
"""
from dataclasses import dataclass
from typing import Dict, Any

def calculate_success_rate(correct: int, total: int) -> float:
    """Pure function to calculate success rate."""
    return (correct / total * 100) if total else 0.0

def calculate_error_rate(incorrect: int, total: int) -> float:
    """Pure function to calculate error rate."""
    return (incorrect / total * 100) if total else 0.0

@dataclass(frozen=True)
class AnswerMetrics:
    """Immutable answer metrics tracking correct and incorrect responses."""
    total: int = 0
    correct: int = 0
    incorrect: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return calculate_success_rate(self.correct, self.total)
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        return calculate_error_rate(self.incorrect, self.total)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total': self.total,
            'correct': self.correct,
            'incorrect': self.incorrect,
            'success_rate': self.success_rate,
            'error_rate': self.error_rate
        }
