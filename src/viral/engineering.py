from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from .models import (
    DesignRequirement,
    EngineeringOption,
    EngineeringReview,
    MaintenanceAssessment,
    ValidationAssessment,
)

if TYPE_CHECKING:
    from .engine import StepResult


class EngineeringReviewPlanner:
    """Synthetic engineering-lifecycle layer for the public demonstrator.

    The planner turns an observed operating limitation into a condition-based
    maintenance recommendation, ranked engineering responses, a design
    requirement when no catalog candidate satisfies the stated constraints,
    and a validation result from a second synthetic run.

    All scores, component candidates and constraints are public demonstration
    values. No production calibration, proprietary component-selection logic or
    private engineering history is included.
    """

    def build_review(
        self,
        baseline: Sequence["StepResult"],
        revised: Sequence["StepResult"],
    ) -> EngineeringReview:
        maintenance = self._maintenance_assessment(baseline)
        options = self._rank_options(baseline)
        design_requirement = self._design_requirement(options)
        validation = self._validate_change(baseline, revised)
        return EngineeringReview(
            maintenance=maintenance,
            options=options,
            design_requirement=design_requirement,
            validation=validation,
        )

    def _maintenance_assessment(
        self,
        results: Sequence["StepResult"],
    ) -> MaintenanceAssessment:
        air_charge_frames = 0
        control_effort_frames = 0
        correction_frames = 0
        max_confidence = 0.0

        for result in results:
            codes = {e.code for e in result.reasoning.evidence}
            if codes & {
                "rising_control_effort",
                "control_effort_rate_shift",
                "requested_achieved_divergence",
                "boost_error_growth",
            }:
                air_charge_frames += 1
            if "rising_control_effort" in codes or "control_effort_rate_shift" in codes:
                control_effort_frames += 1
            if "correction_activity" in codes:
                correction_frames += 1
            if result.reasoning.hypotheses[0].key == "air_charge_control":
                max_confidence = max(max_confidence, result.reasoning.confidence)

        basis = (
            f"Air-charge/control evidence persisted across {air_charge_frames} synthetic frames.",
            f"Actuator-effort deviation was present across {control_effort_frames} synthetic frames.",
            f"Correction activity was present across {correction_frames} synthetic frames.",
            "The condition developed before a hard-limit event and was therefore treated as condition-based degradation evidence rather than a fault-code trigger.",
        )

        return MaintenanceAssessment(
            system="air-charge control path and thermal-support system",
            recommendation=(
                "Inspect the air-charge control path, sealing/flow path and thermal-support hardware "
                "before the next comparable sustained high-load session. The recommendation is based "
                "on repeated relationship drift, not elapsed mileage or a single threshold event."
            ),
            confidence=round(max(max_confidence, 0.72), 2),
            basis=basis,
        )

    def _rank_options(
        self,
        results: Sequence["StepResult"],
    ) -> tuple[EngineeringOption, ...]:
        control_peak = max(r.derived.control_effort_residual_pct for r in results)
        tracking_peak = max(r.derived.boost_tracking_error_bar for r in results)
        intake_peak = max(r.derived.intake_residual_c for r in results)
        coolant_peak = max(r.derived.coolant_residual_c for r in results)

        control_need = min(max(control_peak / 18.0, 0.0), 1.0)
        tracking_need = min(max(tracking_peak / 0.24, 0.0), 1.0)
        thermal_need = min(max(max(intake_peak / 10.0, coolant_peak / 7.0), 0.0), 1.0)

        raw = [
            (
                "Flow-path efficiency redesign",
                "Reduce actuator effort required to achieve the requested air-charge state.",
                0.52 * control_need + 0.33 * tracking_need + 0.15 * thermal_need,
                19.0,
                (
                    "Requires packaging and sealing review.",
                    "Potential aero/duct interaction must be validated.",
                    "Low modeled mass penalty relative to a larger thermal core.",
                ),
            ),
            (
                "Charge-air heat-rejection upgrade",
                "Increase thermal recovery capacity under repeated sustained load.",
                0.24 * control_need + 0.20 * tracking_need + 0.56 * thermal_need,
                16.0,
                (
                    "Adds mass and thermal-core volume.",
                    "Pressure-drop and frontal-area effects must be constrained.",
                    "May shift the limitation upstream if flow efficiency is not addressed.",
                ),
            ),
            (
                "Calibration-only preservation envelope",
                "Trade a controlled amount of peak demand for immediate operating margin.",
                0.20 * control_need + 0.28 * tracking_need + 0.25 * thermal_need,
                8.0,
                (
                    "Fastest intervention path.",
                    "Carries a direct performance penalty.",
                    "Does not remove the underlying hardware limitation.",
                ),
            ),
        ]

        ranked = sorted(raw, key=lambda item: item[2], reverse=True)
        return tuple(
            EngineeringOption(
                rank=index,
                name=name,
                objective=objective,
                score=round(score, 3),
                predicted_margin_gain_pct=predicted_gain,
                tradeoffs=tradeoffs,
            )
            for index, (name, objective, score, predicted_gain, tradeoffs) in enumerate(ranked, start=1)
        )

    def _design_requirement(
        self,
        options: tuple[EngineeringOption, ...],
    ) -> DesignRequirement | None:
        # Synthetic catalog candidates deliberately demonstrate the next
        # engineering step: if no available part meets every constraint, the
        # system defines the requirement instead of pretending a catalog answer
        # exists.
        catalog_candidates = (
            {
                "name": "candidate_alpha",
                "control_effort_reduction_pct": 25.0,
                "tracking_error_reduction_pct": 18.0,
                "thermal_gain_pct": 19.0,
                "pressure_drop_pct": 3.4,
                "mass_kg": 1.2,
                "envelope_growth_pct": 5.0,
            },
            {
                "name": "candidate_beta",
                "control_effort_reduction_pct": 38.0,
                "tracking_error_reduction_pct": 24.0,
                "thermal_gain_pct": 20.0,
                "pressure_drop_pct": 5.3,
                "mass_kg": 1.7,
                "envelope_growth_pct": 5.5,
            },
            {
                "name": "candidate_gamma",
                "control_effort_reduction_pct": 37.0,
                "tracking_error_reduction_pct": 23.0,
                "thermal_gain_pct": 18.5,
                "pressure_drop_pct": 3.8,
                "mass_kg": 2.1,
                "envelope_growth_pct": 7.0,
            },
        )
        constraints = {
            "control_effort_reduction_pct": 35.0,
            "tracking_error_reduction_pct": 20.0,
            "thermal_gain_pct": 18.0,
            "pressure_drop_pct": 4.0,
            "mass_kg": 1.8,
            "envelope_growth_pct": 6.0,
        }

        def satisfies(candidate: dict[str, float | str]) -> bool:
            return (
                float(candidate["control_effort_reduction_pct"]) >= constraints["control_effort_reduction_pct"]
                and float(candidate["tracking_error_reduction_pct"]) >= constraints["tracking_error_reduction_pct"]
                and float(candidate["thermal_gain_pct"]) >= constraints["thermal_gain_pct"]
                and float(candidate["pressure_drop_pct"]) <= constraints["pressure_drop_pct"]
                and float(candidate["mass_kg"]) <= constraints["mass_kg"]
                and float(candidate["envelope_growth_pct"]) <= constraints["envelope_growth_pct"]
            )

        if any(satisfies(candidate) for candidate in catalog_candidates):
            return None

        top = options[0]
        return DesignRequirement(
            title="Purpose-designed flow/thermal support element",
            trigger=(
                "No synthetic catalog candidate simultaneously satisfies the required control-effort, "
                "tracking, thermal, pressure-drop, mass and packaging constraints."
            ),
            targets=(
                "Peak control-effort reduction: >= 35% under the same synthetic duty cycle.",
                "Requested-versus-achieved tracking-error reduction: >= 20%.",
                "Thermal rejection / recovery capability: >= +18% versus the synthetic baseline.",
                "Additional pressure drop: <= 4%.",
                "Mass increase: <= 1.8 kg.",
                "Packaging-envelope growth: <= 6%.",
            ),
            rationale=(
                f"The highest-ranked engineering path is '{top.name}'. Rather than force-fit an available "
                "component, the architecture converts the observed limitation into a measurable design brief "
                "that can be handed to simulation, CAD/CAE, supplier engineering or prototype development."
            ),
        )

    def _validate_change(
        self,
        baseline: Sequence["StepResult"],
        revised: Sequence["StepResult"],
    ) -> ValidationAssessment:
        start_s = 58
        end_s = 87
        base_window = [r for r in baseline if start_s <= r.frame.timestamp_s <= end_s]
        revised_window = [r for r in revised if start_s <= r.frame.timestamp_s <= end_s]

        base_control = max(r.derived.control_effort_residual_pct for r in base_window)
        revised_control = max(r.derived.control_effort_residual_pct for r in revised_window)
        base_tracking = max(r.derived.boost_tracking_error_bar for r in base_window)
        revised_tracking = max(r.derived.boost_tracking_error_bar for r in revised_window)
        base_margin = min(r.derived.engineering_margin for r in base_window)
        revised_margin = min(r.derived.engineering_margin for r in revised_window)

        moved_bottleneck = any(
            r.reasoning.hypotheses[0].key in {"fuel_delivery", "thermal_management"}
            and r.reasoning.confidence >= 0.55
            for r in revised_window
        )

        control_reduction = (base_control - revised_control) / max(base_control, 1e-9)
        tracking_reduction = (base_tracking - revised_tracking) / max(base_tracking, 1e-9)
        margin_gain = revised_margin - base_margin

        validated = (
            control_reduction >= 0.30
            and tracking_reduction >= 0.20
            and margin_gain >= 0.08
            and not moved_bottleneck
        )
        status = "validated" if validated else "needs further iteration"

        conclusion = (
            "The synthetic engineering revision materially reduces control effort and requested-versus-achieved "
            "tracking error while increasing minimum operating margin under the same duty cycle. No stronger "
            "replacement bottleneck emerged in the validation window."
            if validated
            else
            "The synthetic engineering revision does not yet satisfy the complete validation contract. Further "
            "engineering iteration is required before the change should be treated as an improvement."
        )

        return ValidationAssessment(
            status=status,
            baseline_peak_control_effort_pct=round(base_control, 3),
            revised_peak_control_effort_pct=round(revised_control, 3),
            baseline_peak_tracking_error_bar=round(base_tracking, 4),
            revised_peak_tracking_error_bar=round(revised_tracking, 4),
            baseline_min_margin=round(base_margin, 4),
            revised_min_margin=round(revised_margin, 4),
            moved_bottleneck=moved_bottleneck,
            conclusion=conclusion,
        )
