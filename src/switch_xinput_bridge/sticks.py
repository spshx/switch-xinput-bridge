"""Stick calibration: centre from a resting sample, range learned while playing."""
from __future__ import annotations

from typing import Iterable, Sequence

DEFAULT_DEADZONE = 0.10
# Half-range assumed until the stick has been pushed further. Real controllers
# reach roughly 0x6000-0x7000 from centre, so full tilt arrives a bit early on
# the first push and then settles as the true range is learned.
INITIAL_HALF_RANGE = 0x5800
UINT16_CENTRE = 0x8000


class Axis:
    def __init__(self, centre: int, deadzone: float = DEFAULT_DEADZONE):
        if not 0.0 <= deadzone < 1.0:
            raise ValueError("deadzone must be in [0, 1)")
        self.centre = centre
        self.deadzone = deadzone
        self.neg_range = self.pos_range = INITIAL_HALF_RANGE

    def value(self, raw: int) -> float:
        """Map a raw reading to -1.0 .. 1.0 with a rescaled per-axis deadzone."""
        d = raw - self.centre
        if d >= 0:
            self.pos_range = max(self.pos_range, d)
            v = d / self.pos_range
        else:
            self.neg_range = max(self.neg_range, -d)
            v = d / self.neg_range
        if abs(v) < self.deadzone:
            return 0.0
        scaled = (abs(v) - self.deadzone) / (1.0 - self.deadzone)
        return min(1.0, scaled) * (1 if v > 0 else -1)


def calibrate(samples: Iterable[Sequence[int]], deadzone: float = DEFAULT_DEADZONE) -> list:
    """Build four axes centred on the average of resting samples."""
    samples = list(samples)
    if not samples:
        return [Axis(UINT16_CENTRE, deadzone) for _ in range(4)]
    return [Axis(sum(s[i] for s in samples) // len(samples), deadzone) for i in range(4)]
