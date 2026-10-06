from __future__ import annotations

from .models import DerivedState, Evidence, TelemetryFrame


class EvidenceAssembler:
    """Turns relationship residuals into explainable public evidence.

    All thresholds and weights are synthetic demonstration values.
    """

    def assemble(self, frame: TelemetryFrame, state: DerivedState) -> list[Evidence]:
        evidence: list[Evidence] = []

        # Pre-performance precursor: greater actuator effort is required while
        # the achieved state can still appear acceptable.
        if state.control_effort_residual_pct > 4.0 and state.boost_tracking_error_bar < 0.055:
            evidence.append(Evidence(
                "rising_control_effort",
                "Actuator effort is increasing beyond the synthetic expected relationship while achieved boost remains near target.",
                min((state.control_effort_residual_pct - 2.0) / 14.0, 1.0),
                "support",
                "air_charge",
            ))
        if state.control_effort_rate_pct_per_s > 0.22:
            evidence.append(Evidence(
                "control_effort_rate_shift",
                "The control effort required to maintain the requested state is increasing over time.",
                min(state.control_effort_rate_pct_per_s / 0.9, 1.0),
                "support",
                "air_charge",
            ))
        if state.boost_tracking_error_bar > 0.065:
            evidence.append(Evidence(
                "requested_achieved_divergence",
                "The achieved air-charge state is beginning to diverge from the requested synthetic target.",
                min((state.boost_tracking_error_bar - 0.035) / 0.16, 1.0),
                "support",
                "air_charge",
            ))
        if state.boost_error_rate_bar_per_s > 0.0035:
            evidence.append(Evidence(
                "boost_error_growth",
                "Requested-versus-achieved air-charge error is growing rather than remaining stationary.",
                min(state.boost_error_rate_bar_per_s / 0.012, 1.0),
                "support",
                "air_charge",
            ))
        if state.intake_residual_c > 2.6:
            evidence.append(Evidence(
                "intake_nonconformance",
                "Charge/intake temperature is no longer conforming to the synthetic expected state for current load and airflow.",
                min(state.intake_residual_c / 8.5, 1.0),
                "support",
                "air_charge",
            ))

        if state.coolant_residual_c > 2.4:
            evidence.append(Evidence(
                "coolant_nonconformance",
                "Coolant behavior is above the synthetic expected-state model for the current operating context.",
                min(state.coolant_residual_c / 7.0, 1.0),
                "support",
                "thermal",
            ))
        if state.coolant_rate_c_per_s > 0.075:
            evidence.append(Evidence(
                "coolant_rate_shift",
                "Coolant rate-of-change is moving away from the recent operating pattern.",
                min(state.coolant_rate_c_per_s / 0.18, 1.0),
                "support",
                "thermal",
            ))
        if state.oil_residual_c < 1.4 and state.coolant_residual_c > 2.5:
            evidence.append(Evidence(
                "thermal_crosscheck_conflict",
                "Oil temperature remains comparatively conformant while coolant behavior diverges.",
                0.58,
                "conflict",
                "thermal",
            ))

        # Conformant fuel/mixture relationships actively weaken a fuel-delivery
        # explanation instead of being ignored.
        if abs(state.lambda_tracking_error) < 0.018:
            evidence.append(Evidence(
                "mixture_tracking_conformant",
                "Measured mixture remains close to the synthetic requested relationship.",
                0.42,
                "conflict",
                "fuel_delivery",
            ))
        if state.fuel_pressure_tracking_error_norm < 0.025:
            evidence.append(Evidence(
                "fuel_pressure_tracking_conformant",
                "Fuel-pressure support remains close to its synthetic requested relationship.",
                0.52,
                "conflict",
                "fuel_delivery",
            ))
        elif state.fuel_pressure_tracking_error_norm > 0.07:
            evidence.append(Evidence(
                "fuel_pressure_deviation",
                "Fuel-pressure support is falling away from its synthetic requested relationship.",
                min((state.fuel_pressure_tracking_error_norm - 0.04) / 0.12, 1.0),
                "support",
                "fuel_delivery",
            ))

        if state.ignition_correction_deg < -1.2:
            evidence.append(Evidence(
                "correction_activity",
                "The synthetic correction channel is intervening more strongly than during the conformant baseline.",
                min(abs(state.ignition_correction_deg) / 4.0, 1.0),
                "support",
                "system",
            ))

        if state.engineering_margin < 0.52:
            evidence.append(Evidence(
                "margin_narrowing",
                "Composite synthetic engineering margin is narrowing even though no hard-limit event is required.",
                min((0.62 - state.engineering_margin) / 0.45, 1.0),
                "support",
                "system",
            ))
        if not state.hard_limit_crossed and state.engineering_margin < 0.44:
            evidence.append(Evidence(
                "pre_threshold_state",
                "The concern is emerging from relationship non-conformance and projected margin, not a hard threshold crossing.",
                0.84,
                "support",
                "system",
            ))

        return evidence
