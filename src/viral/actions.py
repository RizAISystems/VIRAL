from __future__ import annotations

from .models import AuthorityDecision, SimulatedAction


class PreservationController:
    """Public demo actuator.

    It changes only the synthetic simulator's demand factor. It contains no
    production ECU commands, maps, timing values, boost tables or vehicle-
    specific control logic.
    """

    def request(self, timestamp_s: int, authority: AuthorityDecision) -> SimulatedAction:
        if not authority.allowed:
            return SimulatedAction(
                name="none",
                demand_reduction_pct=0.0,
                requested_at_s=timestamp_s,
                approved=False,
                reason=authority.reason,
            )
        return SimulatedAction(
            name="bounded_preservation_state",
            demand_reduction_pct=8.0,
            requested_at_s=timestamp_s,
            approved=True,
            reason="Synthetic demand reduction approved inside the demonstration authority envelope.",
        )
