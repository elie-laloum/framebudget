import math

from .errors import BudgetError


def sample_offsets(duration: float, count: int, seconds: float) -> tuple[list[float], float]:
    if (
        not isinstance(count, int)
        or isinstance(count, bool)
        or count < 1
        or not math.isfinite(seconds)
        or not math.isfinite(duration)
        or seconds <= 0
        or duration <= 0
    ):
        raise BudgetError("Sample count, length and duration must be positive")
    length = min(duration, seconds)
    span = max(0, duration - length)
    if count == 1 or span == 0:
        return [span / 2], length
    return [i * span / (count - 1) for i in range(count)], length
