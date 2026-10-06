from __future__ import annotations

import json

from .engine import StepResult
from .models import to_dict


def key_events(results: list[StepResult]) -> list[StepResult]:
    events: list[StepResult] = []
    last_top = None
    last_urgency = None
    for r in results:
        top = r.reasoning.hypotheses[0].key
        if (
            r.reasoning.revision
            or r.action is not None
            or r.verification is not None
            or (r.forecast.urgency != last_urgency and r.forecast.urgency != "normal")
            or (
                top != last_top
                and r.reasoning.confidence >= 0.34
                and any(e.direction == "support" for e in r.reasoning.evidence)
                and top not in {"transient_context", "sensor_integrity"}
            )
        ):
            events.append(r)
        last_top = top
        last_urgency = r.forecast.urgency

    if results and results[0] not in events:
        events.insert(0, results[0])
    if results and results[-1] not in events:
        events.append(results[-1])
    return events


def render_text(result: StepResult) -> str:
    r = result.reasoning
    top = r.hypotheses[0]
    lines = [
        f"T+{result.frame.timestamp_s:03d}s",
        f"STATE        {r.what_is_happening}",
        f"BEST FIT     {r.best_explanation}",
        f"CONFIDENCE   {r.confidence:.2f}",
        f"MARGIN       current={result.derived.engineering_margin:.2f} projected={result.forecast.projected_margin:.2f}",
        f"RELATIONSHIP control_effort={result.derived.control_effort_residual_pct:+.2f}% "
        f"boost_error={result.derived.boost_tracking_error_bar:.3f}bar",
        f"FORECAST     {r.what_happens_next}",
        f"RESPONSE     {r.engineering_response}",
        f"AUTHORITY    requested={result.authority.requested_level.value} granted={result.authority.granted_level.value}",
    ]
    if r.revision:
        lines.append(f"REVISION     {r.revision}")
    if r.evidence:
        codes = ", ".join(e.code for e in r.evidence[:5])
        lines.append(f"EVIDENCE     {codes}")
    if result.action:
        lines.append(
            f"ACTION       {result.action.name} approved={result.action.approved} "
            f"demand_reduction={result.action.demand_reduction_pct:.1f}%"
        )
    if result.verification:
        lines.append(f"VERIFICATION {result.verification.status}: {result.verification.conclusion}")
    lines.append(f"TOP BELIEF   {top.key}={top.probability:.2f}")
    return "\n".join(lines)


def render_json(result: StepResult) -> str:
    payload = {
        "frame": to_dict(result.frame),
        "derived": to_dict(result.derived),
        "forecast": to_dict(result.forecast),
        "reasoning": to_dict(result.reasoning),
        "authority": to_dict(result.authority),
        "action": to_dict(result.action) if result.action else None,
        "verification": to_dict(result.verification) if result.verification else None,
    }
    return json.dumps(payload, indent=2)
