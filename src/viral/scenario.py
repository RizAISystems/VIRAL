from __future__ import annotations

import math
from dataclasses import dataclass

from .models import SimulatedAction, TelemetryFrame


@dataclass
class ScenarioState:
    preservation_active: bool = False
    preservation_started_s: int | None = None


class FlagshipRaceScenario:
    """Deterministic synthetic race sequence.

    The scenario is informed by the *structure* of real performance-vehicle
    logging: driver/request channels, actuator effort, achieved state,
    correction channels and thermal response. All values, coefficients and
    transitions are synthetic and intentionally non-vehicle-specific.
    """

    duration_s = 125

    def __init__(self, engineering_revision: bool = False) -> None:
        self.state = ScenarioState()
        self.engineering_revision = engineering_revision

    def apply_action(self, action: SimulatedAction) -> None:
        if action.approved and action.name == "bounded_preservation_state":
            self.state.preservation_active = True
            self.state.preservation_started_s = action.requested_at_s

    def frame(self, t: int) -> TelemetryFrame:
        ambient = 27.0
        speed = 208.0 + 8.0 * math.sin(t / 7.5)
        rpm = 5650.0 + 480.0 * math.sin(t / 5.2)
        gear = 5 if speed < 215 else 6
        grade = 0.7 + 0.45 * math.sin(t / 18.0)
        lateral_g = 0.45 + 0.45 * abs(math.sin(t / 4.4))
        brake = 405.0 + 65.0 * abs(math.sin(t / 6.3))

        preservation = 0.0
        if self.state.preservation_active and self.state.preservation_started_s is not None:
            elapsed = max(t - self.state.preservation_started_s, 0)
            preservation = min(elapsed / 8.0, 1.0) * 0.08

        driver_demand = 88.0 + 5.0 * math.sin(t / 8.0)
        torque_request = 0.86 + 0.035 * math.sin(t / 9.0) - preservation
        boost_target = 1.54 + 0.035 * math.sin(t / 6.7) - preservation * 0.72

        airflow = min(max(speed / 220.0, 0.15), 1.2)
        expected_throttle = 10.0 + 77.0 * torque_request + 4.0 * (driver_demand / 100.0)
        expected_load = 0.12 + 0.84 * torque_request
        expected_boost = boost_target - (0.012 + 0.015 * max(torque_request - 0.72, 0.0))
        expected_wastegate = 24.0 + 34.0 * boost_target + 8.0 * torque_request
        expected_coolant = 88.5 + 13.0 * expected_load + 0.22 * 7.0 + 0.25 * grade - 3.0 * airflow
        expected_oil = 100.5 + 18.5 * expected_load + 0.15 * 7.0 + 0.17 * grade - 1.9 * airflow
        expected_intake = ambient + 7.0 + 14.5 * expected_load - 4.3 * airflow

        throttle_offset = 0.25 * math.sin(t / 11.0)
        load_offset = 0.004 * math.sin(t / 12.0)
        wastegate_offset = 0.7 * math.sin(t / 10.0)
        boost_extra_error = 0.008 + 0.003 * abs(math.sin(t / 8.0))
        coolant_offset = 0.35 * math.sin(t / 10.0)
        oil_offset = 0.30 * math.sin(t / 13.0)
        intake_offset = 0.45 * math.sin(t / 8.5)
        lambda_offset = 0.003 * math.sin(t / 7.0)
        fuel_pressure_offset = 0.006 * abs(math.sin(t / 9.5))
        ignition_correction = -0.15 * abs(math.sin(t / 6.0))

        # Phase 1: an early thermal-shaped precursor appears while the car
        # remains fully operational. The reasoner should treat this as a
        # hypothesis, not as truth.
        if 24 <= t < 42:
            p = (t - 24) / 18.0
            coolant_offset += 4.2 * p
            intake_offset += 0.9 * p
            ignition_correction -= 0.25 * p

        # Phase 2: the achieved result can still look acceptable, but the
        # synthetic actuator effort required to maintain it begins climbing.
        # This new evidence should weaken the first explanation.
        elif 42 <= t < 58:
            p = (t - 42) / 16.0
            wastegate_offset += 8.5 * p
            coolant_offset += 4.2 * (1.0 - 0.40 * p)
            intake_offset += 0.9 + 1.2 * p
            ignition_correction -= 0.25 + 0.35 * p

        # Phase 3: requested-versus-achieved air-charge response now diverges
        # while the earlier coolant signal recovers. The reasoner is expected
        # to revise its preferred explanation as the evidence changes.
        elif 58 <= t < 88:
            p = (t - 58) / 30.0
            wastegate_offset += 8.5 + 7.0 * p
            boost_extra_error += 0.018 + 0.102 * p
            coolant_offset += 2.52 * (1.0 - p) + 0.65 * p
            intake_offset += 2.1 + 3.7 * p
            ignition_correction -= 0.60 + 1.0 * p

        # Phase 3: if nothing changes, the operating relationship continues to
        # deteriorate even though the demonstration still avoids a hard limit.
        elif t >= 88:
            wastegate_offset += 16.0
            boost_extra_error += 0.205
            coolant_offset += 0.9
            intake_offset += 9.0
            ignition_correction -= 1.8

        # A second synthetic run can apply an engineering revision to the same
        # duty cycle. This is not a production design model. It demonstrates the
        # validation contract: change the vehicle, repeat comparable conditions,
        # then measure whether the original limitation improved or moved.
        if self.engineering_revision and t >= 42:
            revision_ramp = min(max((t - 42) / 12.0, 0.0), 1.0)
            wastegate_offset *= 1.0 - 0.48 * revision_ramp
            boost_extra_error *= 1.0 - 0.38 * revision_ramp
            intake_offset *= 1.0 - 0.28 * revision_ramp
            ignition_correction *= 1.0 - 0.25 * revision_ramp

        # Public bounded preservation reduces synthetic requested demand only.
        # No production control law or calibration instruction exists here.
        if self.state.preservation_active and self.state.preservation_started_s is not None:
            elapsed = max(t - self.state.preservation_started_s, 0)
            recovery = min(elapsed / 18.0, 1.0)
            wastegate_offset *= 1.0 - 0.66 * recovery
            boost_extra_error *= 1.0 - 0.70 * recovery
            coolant_offset *= 1.0 - 0.52 * recovery
            intake_offset *= 1.0 - 0.60 * recovery
            ignition_correction *= 1.0 - 0.62 * recovery

        lambda_target = 0.82 + 0.004 * math.sin(t / 14.0)
        lambda_actual = lambda_target + lambda_offset
        fuel_pressure_target = 0.985
        fuel_pressure_actual = fuel_pressure_target - fuel_pressure_offset

        boost_actual = expected_boost - boost_extra_error

        return TelemetryFrame(
            timestamp_s=t,
            speed_kph=round(speed, 2),
            rpm=round(rpm, 1),
            gear=gear,
            driver_demand_pct=round(driver_demand, 2),
            torque_request_norm=round(max(torque_request, 0.0), 4),
            throttle_pct=round(expected_throttle + throttle_offset, 3),
            engine_load=round(expected_load + load_offset, 4),
            boost_target_bar=round(boost_target, 4),
            boost_actual_bar=round(boost_actual, 4),
            wastegate_command_pct=round(expected_wastegate + wastegate_offset, 3),
            lambda_target=round(lambda_target, 4),
            lambda_actual=round(lambda_actual, 4),
            fuel_pressure_target_norm=round(fuel_pressure_target, 4),
            fuel_pressure_actual_norm=round(fuel_pressure_actual, 4),
            ignition_correction_deg=round(ignition_correction, 3),
            coolant_c=round(expected_coolant + coolant_offset, 3),
            oil_c=round(expected_oil + oil_offset, 3),
            intake_c=round(expected_intake + intake_offset, 3),
            ambient_c=ambient,
            grade_pct=round(grade, 3),
            lateral_g=round(lateral_g, 3),
            brake_temp_c=round(brake, 2),
            driver_report=None,
        )
