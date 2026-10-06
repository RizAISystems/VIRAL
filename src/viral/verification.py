from __future__ import annotations

from collections import deque

from .models import VerificationResult


class OutcomeVerifier:
    def __init__(self, window: int = 8) -> None:
        self._post_action: deque[float] = deque(maxlen=window)
        self._baseline_margin: float | None = None

    def begin(self, margin: float) -> None:
        self._baseline_margin = margin
        self._post_action.clear()

    def observe(self, timestamp_s: int, margin: float) -> VerificationResult | None:
        if self._baseline_margin is None:
            return None
        self._post_action.append(margin)
        if len(self._post_action) < self._post_action.maxlen:
            return None

        avg_recent = sum(self._post_action) / len(self._post_action)
        delta = avg_recent - self._baseline_margin
        if delta >= 0.08:
            status = "stabilized"
            conclusion = "The synthetic vehicle state is recovering after the bounded preservation action."
        elif delta <= -0.04:
            status = "ineffective"
            conclusion = "The synthetic preservation action is not arresting the deterioration; engineering escalation is required."
        else:
            status = "inconclusive"
            conclusion = "The post-action response is not yet strong enough to justify a confident conclusion."

        result = VerificationResult(
            timestamp_s=timestamp_s,
            status=status,
            margin_before=round(self._baseline_margin, 4),
            margin_after=round(avg_recent, 4),
            conclusion=conclusion,
        )
        self._baseline_margin = None
        return result
