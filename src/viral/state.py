from __future__ import annotations

from .models import DerivedState, ExpectedState, TelemetryFrame


class StateInterpreter:
    """Converts synthetic raw telemetry into relationship residuals and margin."""

    COOLANT_HARD_C = 116.0
    OIL_HARD_C = 136.0
    INTAKE_HARD_C = 72.0
    BOOST_ERROR_HARD_BAR = 0.28
    LAMBDA_ERROR_HARD = 0.10
    FUEL_PRESSURE_ERROR_HARD = 0.18

    def derive(
        self,
        frame: TelemetryFrame,
        expected: ExpectedState,
        previous_frame: TelemetryFrame | None,
        previous_expected: ExpectedState | None,
    ) -> DerivedState:
        throttle_residual = frame.throttle_pct - expected.throttle_pct
        load_residual = frame.engine_load - expected.engine_load
        boost_error = frame.boost_target_bar - frame.boost_actual_bar
        control_effort = frame.wastegate_command_pct - expected.wastegate_command_pct
        lambda_error = frame.lambda_actual - frame.lambda_target
        fuel_pressure_error = frame.fuel_pressure_target_norm - frame.fuel_pressure_actual_norm

        coolant_residual = frame.coolant_c - expected.coolant_c
        oil_residual = frame.oil_c - expected.oil_c
        intake_residual = frame.intake_c - expected.intake_c

        if previous_frame is None or previous_expected is None:
            coolant_rate = 0.0
            intake_rate = 0.0
            boost_error_rate = 0.0
            control_effort_rate = 0.0
        else:
            dt = max(frame.timestamp_s - previous_frame.timestamp_s, 1)
            coolant_rate = (frame.coolant_c - previous_frame.coolant_c) / dt
            intake_rate = (frame.intake_c - previous_frame.intake_c) / dt
            previous_boost_error = previous_frame.boost_target_bar - previous_frame.boost_actual_bar
            boost_error_rate = (boost_error - previous_boost_error) / dt
            previous_effort = previous_frame.wastegate_command_pct - previous_expected.wastegate_command_pct
            control_effort_rate = (control_effort - previous_effort) / dt

        # Synthetic public margin. It deliberately combines relationship
        # residuals, not only absolute channel values.
        control_stress = max(control_effort - 2.0, 0.0) / 18.0
        boost_stress = max(boost_error - 0.025, 0.0) / 0.22
        intake_stress = max(intake_residual, 0.0) / 10.0
        coolant_stress = max(coolant_residual, 0.0) / 9.0
        load_stress = abs(load_residual) / 0.12
        mixture_stress = abs(lambda_error) / 0.07
        fuel_stress = max(fuel_pressure_error, 0.0) / 0.14
        correction_stress = max(-frame.ignition_correction_deg, 0.0) / 4.5
        rate_stress = (
            max(boost_error_rate, 0.0) / 0.015
            + max(control_effort_rate, 0.0) / 1.2
        )

        composite = (
            0.24 * control_stress
            + 0.22 * boost_stress
            + 0.13 * intake_stress
            + 0.10 * coolant_stress
            + 0.08 * load_stress
            + 0.07 * mixture_stress
            + 0.06 * fuel_stress
            + 0.06 * correction_stress
            + 0.04 * min(rate_stress, 1.5)
        )
        margin = min(max(1.0 - composite, 0.0), 1.0)

        hard_crossed = (
            frame.coolant_c >= self.COOLANT_HARD_C
            or frame.oil_c >= self.OIL_HARD_C
            or frame.intake_c >= self.INTAKE_HARD_C
            or boost_error >= self.BOOST_ERROR_HARD_BAR
            or abs(lambda_error) >= self.LAMBDA_ERROR_HARD
            or fuel_pressure_error >= self.FUEL_PRESSURE_ERROR_HARD
        )

        return DerivedState(
            throttle_residual_pct=round(throttle_residual, 4),
            load_residual=round(load_residual, 5),
            boost_tracking_error_bar=round(boost_error, 5),
            control_effort_residual_pct=round(control_effort, 4),
            lambda_tracking_error=round(lambda_error, 5),
            fuel_pressure_tracking_error_norm=round(fuel_pressure_error, 5),
            ignition_correction_deg=round(frame.ignition_correction_deg, 4),
            coolant_residual_c=round(coolant_residual, 4),
            oil_residual_c=round(oil_residual, 4),
            intake_residual_c=round(intake_residual, 4),
            coolant_rate_c_per_s=round(coolant_rate, 5),
            intake_rate_c_per_s=round(intake_rate, 5),
            boost_error_rate_bar_per_s=round(boost_error_rate, 6),
            control_effort_rate_pct_per_s=round(control_effort_rate, 5),
            engineering_margin=round(margin, 4),
            hard_limit_crossed=hard_crossed,
        )
