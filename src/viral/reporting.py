from __future__ import annotations

import json

from .engine import StepResult
from .models import EngineeringReview, to_dict


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
        f"tracking_error={result.derived.boost_tracking_error_bar:.3f}bar",
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


def render_engineering_review(review: EngineeringReview) -> str:
    lines = [
        "ENGINEERING LIFECYCLE REVIEW",
        "",
        "CONDITION-BASED MAINTENANCE",
        f"SYSTEM       {review.maintenance.system}",
        f"CONFIDENCE   {review.maintenance.confidence:.2f}",
        f"RECOMMEND    {review.maintenance.recommendation}",
    ]
    for basis in review.maintenance.basis:
        lines.append(f"BASIS        {basis}")

    lines.extend(["", "RANKED ENGINEERING RESPONSES"])
    for option in review.options:
        lines.append(
            f"{option.rank}. {option.name} | score={option.score:.3f} | "
            f"modeled_margin_gain=+{option.predicted_margin_gain_pct:.1f}%"
        )
        lines.append(f"   OBJECTIVE  {option.objective}")
        for tradeoff in option.tradeoffs:
            lines.append(f"   TRADEOFF   {tradeoff}")

    if review.design_requirement:
        lines.extend([
            "",
            "DESIGN REQUIREMENT",
            f"TITLE        {review.design_requirement.title}",
            f"TRIGGER      {review.design_requirement.trigger}",
        ])
        for target in review.design_requirement.targets:
            lines.append(f"TARGET       {target}")
        lines.append(f"RATIONALE    {review.design_requirement.rationale}")

    v = review.validation
    lines.extend([
        "",
        "MODIFICATION VALIDATION",
        f"STATUS       {v.status}",
        (
            f"CONTROL      baseline={v.baseline_peak_control_effort_pct:.2f}% "
            f"revised={v.revised_peak_control_effort_pct:.2f}%"
        ),
        (
            f"TRACKING     baseline={v.baseline_peak_tracking_error_bar:.3f}bar "
            f"revised={v.revised_peak_tracking_error_bar:.3f}bar"
        ),
        f"MARGIN       baseline_min={v.baseline_min_margin:.2f} revised_min={v.revised_min_margin:.2f}",
        f"BOTTLENECK   moved={v.moved_bottleneck}",
        f"CONCLUSION   {v.conclusion}",
    ])
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
