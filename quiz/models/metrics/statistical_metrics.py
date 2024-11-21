"""
Statistical metrics for question analysis.
"""
from typing import List, Protocol, TypeVar
import numpy as np
from scipy import stats

class HasScore(Protocol):
    """Protocol for objects with a score attribute."""
    score: float

class HasTimeTaken(Protocol):
    """Protocol for objects with a time_taken attribute."""
    time_taken: float

T = TypeVar('T', bound=HasScore)

def calculate_discrimination(top_scores: List[T], bottom_scores: List[T]) -> float:
    """
    Calculate discrimination index between top and bottom scoring groups.
    Pure function using functional programming patterns.
    """
    if not (top_scores and bottom_scores):
        return 0.0
        
    top_mean = np.mean([attempt.score for attempt in top_scores])
    bottom_mean = np.mean([attempt.score for attempt in bottom_scores])
    total_std = np.std([attempt.score for attempt in top_scores + bottom_scores])
    
    if total_std == 0:
        return 0.0
        
    return (top_mean - bottom_mean) / total_std

def calculate_point_biserial(scores: List[float], correct: List[bool]) -> float:
    """
    Calculate point-biserial correlation coefficient.
    Pure function for statistical analysis.
    """
    if not scores or not correct or len(scores) != len(correct):
        return 0.0
        
    if len(set(correct)) < 2:  # All correct or all incorrect
        return 0.0
        
    try:
        return stats.pointbiserialr(scores, correct)[0]
    except:
        return 0.0
