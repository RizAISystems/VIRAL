from __future__ import annotations

import math
from collections import defaultdict

from .models import Evidence, Forecast, Hypothesis, ReasoningSnapshot


HYPOTHESIS_LABELS = {
    "thermal_management": "Developing thermal-management limitation",
    "air_charge_control": "Air-charge / performance-control deviation",
    "fuel_delivery": "Fuel-delivery support deviation",
    "sensor_integrity": "Sensor or signal-integrity issue",
    "transient_context": "Contextual transient with no persistent engineering fault",
}


class AdaptiveReasoningEngine:
    """Stateful probabilistic evidence-fusion demonstrator.

    This is intentionally transparent and synthetic. It demonstrates the
    decision architecture: competing explanations, evidence weighting,
    belief revision, uncertainty and abstention. It does not contain the
    proprietary intelligence planned for private RZ1 systems.
    """

    def __init__(self) -> None:
        self._beliefs = {
            "thermal_management": 0.24,
            "air_charge_control": 0.22,
            "fuel_delivery": 0.12,
            "sensor_integrity": 0.14,
            "transient_context": 0.28,
        }
        self._previous_top: str | None = None

    @property
    def beliefs(self) -> dict[str, float]:
        return dict(self._beliefs)

    def reason(self, timestamp_s: int, evidence: list[Evidence], forecast: Forecast) -> ReasoningSnapshot:
        log_scores = {k: math.log(max(v, 1e-6)) for k, v in self._beliefs.items()}

        by_source: dict[str, list[Evidence]] = defaultdict(list)
        for item in evidence:
            by_source[item.source].append(item)

        for item in evidence:
            sign = 1.0 if item.direction == "support" else -1.0
            s = item.strength * sign
            if item.source == "thermal":
                log_scores["thermal_management"] += 1.55 * s
                log_scores["transient_context"] -= 0.35 * max(s, 0.0)
            elif item.source == "air_charge":
                log_scores["air_charge_control"] += 1.75 * s
                log_scores["thermal_management"] += 0.18 * max(s, 0.0)
            elif item.source == "fuel_delivery":
                log_scores["fuel_delivery"] += 1.7 * s
            elif item.source == "system":
                log_scores["transient_context"] -= 0.55 * max(s, 0.0)

        # Coherence reduces the chance that one isolated sensor is driving the decision.
        support_sources = {e.source for e in evidence if e.direction == "support" and e.strength >= 0.45}
        if len(support_sources) >= 2:
            log_scores["sensor_integrity"] -= 0.6
        elif len(support_sources) == 1 and evidence:
            log_scores["sensor_integrity"] += 0.2

        # If evidence is sparse, retain a meaningful transient/abstention path.
        if len(evidence) <= 1:
            log_scores["transient_context"] += 0.5

        probabilities = self._softmax(log_scores)

        # Stateful smoothing allows beliefs to move, not jump, as new evidence arrives.
        alpha = 0.44
        updated = {
            k: (1 - alpha) * self._beliefs[k] + alpha * probabilities[k]
            for k in self._beliefs
        }
        total = sum(updated.values())
        normalized = {k: v / total for k, v in updated.items()}
        # Keep an explicit uncertainty floor. Even strong evidence does not make
        # a public synthetic hypothesis equivalent to engineering truth.
        uncertainty_mix = 0.08
        uniform = 1.0 / len(normalized)
        self._beliefs = {
            k: (1.0 - uncertainty_mix) * v + uncertainty_mix * uniform
            for k, v in normalized.items()
        }

        ordered = sorted(self._beliefs.items(), key=lambda kv: kv[1], reverse=True)
        top_key, top_p = ordered[0]
        second_p = ordered[1][1]
        separation = max(top_p - second_p, 0.0)
        evidence_strength = min(sum(e.strength for e in evidence) / 4.0, 1.0)
        confidence = min(max(0.48 * top_p + 0.34 * separation + 0.18 * evidence_strength, 0.0), 0.94)

        abstained = confidence < 0.34 or top_p < 0.38
        revision = None
        has_support = any(e.direction == "support" for e in evidence)
        trackable = top_key not in {"transient_context", "sensor_integrity"}
        if has_support and trackable and confidence >= 0.34 and top_p >= 0.4:
            if self._previous_top is not None and self._previous_top != top_key:
                revision = (
                    f"Primary explanation revised from '{HYPOTHESIS_LABELS[self._previous_top]}' "
                    f"to '{HYPOTHESIS_LABELS[top_key]}' as new evidence arrived."
                )
            self._previous_top = top_key

        hypotheses: list[Hypothesis] = []
        for key, prob in ordered:
            supporting = tuple(e.code for e in evidence if self._supports(key, e))
            conflicting = tuple(e.code for e in evidence if self._conflicts(key, e))
            hypotheses.append(Hypothesis(
                key=key,
                label=HYPOTHESIS_LABELS[key],
                probability=round(prob, 4),
                supporting=supporting,
                conflicting=conflicting,
            ))

        supporting_evidence = [e for e in evidence if e.direction == "support"]
        if not supporting_evidence:
            what = "Vehicle state remains conformant with the public synthetic operating model."
        elif forecast.projected_margin < 0.34:
            what = "Live data is no longer fully conformant with expected operation and available engineering margin is narrowing."
        else:
            what = "A developing non-conformance is present, but the vehicle remains inside the synthetic hard limits."

        plausible = tuple(HYPOTHESIS_LABELS[k] for k, p in ordered[:3] if p >= 0.12)

        if not supporting_evidence:
            best = "No abnormal engineering explanation is warranted by the current evidence."
            response = "No intervention justified; continue observation."
        elif abstained:
            best = "No engineering explanation currently has enough evidence to justify a confident diagnosis."
            response = "Continue monitoring and request engineering review if the evidence does not converge."
        else:
            best = HYPOTHESIS_LABELS[top_key]
            if forecast.urgency == "preserve":
                response = "Request a bounded preservation state and verify whether the vehicle returns toward its expected operating relationship."
            elif forecast.urgency == "watch":
                response = "Continue at current authority while monitoring for convergence, recovery or further margin loss."
            else:
                response = "No intervention justified; continue observation."

        next_text = forecast.consequence

        return ReasoningSnapshot(
            timestamp_s=timestamp_s,
            what_is_happening=what,
            why_might_it_be_happening=plausible,
            best_explanation=best,
            what_happens_next=next_text,
            confidence=round(confidence, 4),
            engineering_response=response,
            hypotheses=tuple(hypotheses),
            evidence=tuple(evidence),
            revision=revision,
            abstained=abstained,
        )

    @staticmethod
    def _softmax(scores: dict[str, float]) -> dict[str, float]:
        m = max(scores.values())
        exp = {k: math.exp(v - m) for k, v in scores.items()}
        s = sum(exp.values())
        return {k: v / s for k, v in exp.items()}

    @staticmethod
    def _supports(key: str, evidence: Evidence) -> bool:
        mapping = {
            "thermal_management": "thermal",
            "air_charge_control": "air_charge",
            "fuel_delivery": "fuel_delivery",
        }
        if key in mapping:
            return evidence.source == mapping[key] and evidence.direction == "support"
        if key == "sensor_integrity":
            return evidence.direction == "conflict" and evidence.strength > 0.7
        if key == "transient_context":
            return evidence.source == "system" and evidence.direction == "conflict"
        return False

    @staticmethod
    def _conflicts(key: str, evidence: Evidence) -> bool:
        mapping = {
            "thermal_management": "thermal",
            "air_charge_control": "air_charge",
            "fuel_delivery": "fuel_delivery",
        }
        if key in mapping:
            return evidence.source == mapping[key] and evidence.direction == "conflict"
        return False
