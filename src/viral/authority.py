from __future__ import annotations

from .models import AuthorityDecision, AuthorityLevel, Forecast, ReasoningSnapshot


class AuthorityGate:
    """Deterministic boundary around probabilistic reasoning."""

    def __init__(self, configured_level: AuthorityLevel = AuthorityLevel.A3_SIMULATE) -> None:
        self.configured_level = configured_level

    def evaluate(self, reasoning: ReasoningSnapshot, forecast: Forecast) -> AuthorityDecision:
        if reasoning.abstained:
            return AuthorityDecision(
                requested_level=AuthorityLevel.A1_ADVISE,
                granted_level=min_level(self.configured_level, AuthorityLevel.A1_ADVISE),
                allowed=False,
                reason="Reasoning confidence is insufficient for preservation action.",
            )

        if forecast.urgency == "escalate":
            return AuthorityDecision(
                requested_level=AuthorityLevel.A1_ADVISE,
                granted_level=min_level(self.configured_level, AuthorityLevel.A1_ADVISE),
                allowed=False,
                reason="A hard-limit event requires engineering escalation; no simulated autonomous continuation is authorized.",
            )

        if forecast.urgency == "preserve" and reasoning.confidence >= 0.52:
            requested = AuthorityLevel.A3_SIMULATE
            allowed = level_rank(self.configured_level) >= level_rank(requested)
            return AuthorityDecision(
                requested_level=requested,
                granted_level=self.configured_level,
                allowed=allowed,
                reason=(
                    "Bounded simulated preservation is permitted by the public demonstration policy."
                    if allowed
                    else "Configured authority is below the level required for simulated preservation."
                ),
            )

        return AuthorityDecision(
            requested_level=AuthorityLevel.A1_ADVISE,
            granted_level=min_level(self.configured_level, AuthorityLevel.A1_ADVISE),
            allowed=False,
            reason="Observation/advisory state remains sufficient.",
        )


def level_rank(level: AuthorityLevel) -> int:
    return {
        AuthorityLevel.A0_OBSERVE: 0,
        AuthorityLevel.A1_ADVISE: 1,
        AuthorityLevel.A2_REQUEST: 2,
        AuthorityLevel.A3_SIMULATE: 3,
    }[level]


def min_level(a: AuthorityLevel, b: AuthorityLevel) -> AuthorityLevel:
    return a if level_rank(a) <= level_rank(b) else b
