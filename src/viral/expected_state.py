from __future__ import annotations

from .models import ExpectedState, TelemetryFrame


class SyntheticExpectedStateModel:
    """Transparent public reference model.

    The coefficients are synthetic and intentionally simplified. The point is
    not to emulate a particular vehicle. It is to demonstrate how request,
    actuator effort, achieved state and correction state can be evaluated as a
    relationship instead of as isolated channels.
    """

    def predict(self, frame: TelemetryFrame) -> ExpectedState:
        airflow_factor = min(max(frame.speed_kph / 220.0, 0.15), 1.2)
        request = min(max(frame.torque_request_norm, 0.0), 1.15)
        demand = min(max(frame.driver_demand_pct / 100.0, 0.0), 1.0)
        grade = max(frame.grade_pct, 0.0)

        throttle = 10.0 + 77.0 * request + 4.0 * demand
        load = 0.12 + 0.84 * request
        boost = frame.boost_target_bar - (0.012 + 0.015 * max(request - 0.72, 0.0))

        # Synthetic control-effort expectation. A key public concept is that
        # control effort can drift before achieved performance visibly falls.
        wastegate = 24.0 + 34.0 * frame.boost_target_bar + 8.0 * request

        lambda_actual = frame.lambda_target
        fuel_pressure_actual = frame.fuel_pressure_target_norm

        coolant = (
            88.5
            + 13.0 * load
            + 0.22 * max(frame.ambient_c - 20.0, 0.0)
            + 0.25 * grade
            - 3.0 * airflow_factor
        )
        oil = (
            100.5
            + 18.5 * load
            + 0.15 * max(frame.ambient_c - 20.0, 0.0)
            + 0.17 * grade
            - 1.9 * airflow_factor
        )
        intake = frame.ambient_c + 7.0 + 14.5 * load - 4.3 * airflow_factor

        return ExpectedState(
            throttle_pct=round(throttle, 3),
            engine_load=round(load, 4),
            boost_actual_bar=round(boost, 4),
            wastegate_command_pct=round(wastegate, 3),
            lambda_actual=round(lambda_actual, 4),
            fuel_pressure_actual_norm=round(fuel_pressure_actual, 4),
            coolant_c=round(coolant, 3),
            oil_c=round(oil, 3),
            intake_c=round(intake, 3),
        )
