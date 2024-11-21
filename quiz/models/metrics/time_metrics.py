"""
Time-based metrics for tracking attempt durations.
"""
from dataclasses import dataclass
from typing import Dict, Any, List
from statistics import mean, median

@dataclass(frozen=True)
class TimeDistribution:
    """Immutable time distribution metrics."""
    min_time: float = 0.0
    max_time: float = 0.0
    avg_time: float = 0.0
    median_time: float = 0.0
    
    @staticmethod
    def from_times(times: List[float]) -> 'TimeDistribution':
        """Factory method to create time distribution from a list of times."""
        if not times:
            return TimeDistribution()
            
        return TimeDistribution(
            min_time=min(times),
            max_time=max(times),
            avg_time=mean(times),
            median_time=median(times)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert time distribution to dictionary."""
        return {
            'min': self.min_time,
            'max': self.max_time,
            'avg': self.avg_time,
            'median': self.median_time
        }
