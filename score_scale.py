from dataclasses import dataclass

@dataclass
class ScoreScale:
    """Defines the score scale for normalization and visualization."""
    score_min:         float = 0.0
    score_max:         float = 100.0
    passing_threshold: float = 35.0