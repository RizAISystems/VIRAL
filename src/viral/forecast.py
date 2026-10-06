from __future__ import annotations

from collections import deque

from .models import DerivedState, Forecast


class MarginForecaster:
    def __init__(self, horizon_s: int = 20, window: int = 8) -> None:
        self.horizon_s = horizon_s
        self._margins: deque[tuple[int, float]] = deque(maxlen=window)

    def update(self, timestamp_s: int, state: DerivedState) -> Forecast:
        self._margins.append((timestamp_s, state.engineering_margin))
        slope = self._slope()
        projected = min(max(state.engineering_margin + slope * self.horizon_s, 0.0), 1.0)

        if state.hard_limit_crossed:
            urgency = "escalate"
            consequence = "A synthetic hard-limit event is already present; autonomous continuation should not be assumed."
        elif projected < 0.24 and slope < -0.002:
            urgency = "preserve"
            consequence = (
                "If the current trend persists, the synthetic operating margin is projected to become critically narrow "
                f"within the next ~{self.horizon_s} seconds."
            )
        elif projected < 0.45 or state.engineering_margin < 0.48:
            urgency = "watch"
            consequence = (
                "The vehicle remains operational, but the current trend is reducing available synthetic engineering margin."
            )
        else:
            urgency = "normal"
            consequence = "No near-term synthetic operating constraint is projected from the current trend."

        return Forecast(
            projected_margin=round(projected, 4),
            horizon_s=self.horizon_s,
            consequence=consequence,
            urgency=urgency,
        )

    def _slope(self) -> float:
        if len(self._margins) < 3:
            return 0.0
        x0, _ = self._margins[0]
        xs = [x - x0 for x, _ in self._margins]
        ys = [y for _, y in self._margins]
        n = len(xs)
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n
        denom = sum((x - x_mean) ** 2 for x in xs)
        if denom == 0:
            return 0.0
        return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom
