from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class AuthorityLevel(str, Enum):
    A0_OBSERVE = "A0"
    A1_ADVISE = "A1"
    A2_REQUEST = "A2"
    A3_SIMULATE = "A3"


@dataclass(frozen=True)
class TelemetryFrame:
    """Canonical synthetic vehicle state used by the public demonstrator.

    The fields are intentionally generic. They represent relationships commonly
    present in performance-vehicle data: request, actuator effort, achieved
    state, correction state and resulting thermal/mechanical response.
    """

    timestamp_s: int
    speed_kph: float
    rpm: float
    gear: int

    # Requested state / driver intent.
    driver_demand_pct: float
    torque_request_norm: float

    # Actuator / achieved state.
    throttle_pct: float
    engine_load: float
    boost_target_bar: float
    boost_actual_bar: float
    wastegate_command_pct: float

    # Mixture / fuel support / correction state.
    lambda_target: float
    lambda_actual: float
    fuel_pressure_target_norm: float
    fuel_pressure_actual_norm: float
    ignition_correction_deg: float

    # Thermal / operating context.
    coolant_c: float
    oil_c: float
    intake_c: float
    ambient_c: float
    grade_pct: float
    lateral_g: float
    brake_temp_c: float

    driver_report: str | None = None


@dataclass(frozen=True)
class ExpectedState:
    throttle_pct: float
    engine_load: float
    boost_actual_bar: float
    wastegate_command_pct: float
    lambda_actual: float
    fuel_pressure_actual_norm: float
    coolant_c: float
    oil_c: float
    intake_c: float


@dataclass(frozen=True)
class DerivedState:
    throttle_residual_pct: float
    load_residual: float
    boost_tracking_error_bar: float
    control_effort_residual_pct: float
    lambda_tracking_error: float
    fuel_pressure_tracking_error_norm: float
    ignition_correction_deg: float

    coolant_residual_c: float
    oil_residual_c: float
    intake_residual_c: float

    coolant_rate_c_per_s: float
    intake_rate_c_per_s: float
    boost_error_rate_bar_per_s: float
    control_effort_rate_pct_per_s: float

    engineering_margin: float
    hard_limit_crossed: bool


@dataclass(frozen=True)
class Evidence:
    code: str
    description: str
    strength: float
    direction: str
    source: str


@dataclass(frozen=True)
class Hypothesis:
    key: str
    label: str
    probability: float
    supporting: tuple[str, ...] = ()
    conflicting: tuple[str, ...] = ()


@dataclass(frozen=True)
class Forecast:
    projected_margin: float
    horizon_s: int
    consequence: str
    urgency: str


@dataclass(frozen=True)
class ReasoningSnapshot:
    timestamp_s: int
    what_is_happening: str
    why_might_it_be_happening: tuple[str, ...]
    best_explanation: str
    what_happens_next: str
    confidence: float
    engineering_response: str
    hypotheses: tuple[Hypothesis, ...]
    evidence: tuple[Evidence, ...]
    revision: str | None
    abstained: bool = False


@dataclass(frozen=True)
class AuthorityDecision:
    requested_level: AuthorityLevel
    granted_level: AuthorityLevel
    allowed: bool
    reason: str


@dataclass(frozen=True)
class SimulatedAction:
    name: str
    demand_reduction_pct: float
    requested_at_s: int
    approved: bool
    reason: str


@dataclass(frozen=True)
class VerificationResult:
    timestamp_s: int
    status: str
    margin_before: float
    margin_after: float
    conclusion: str


@dataclass(frozen=True)
class MaintenanceAssessment:
    system: str
    recommendation: str
    confidence: float
    basis: tuple[str, ...]


@dataclass(frozen=True)
class EngineeringOption:
    rank: int
    name: str
    objective: str
    score: float
    predicted_margin_gain_pct: float
    tradeoffs: tuple[str, ...]


@dataclass(frozen=True)
class DesignRequirement:
    title: str
    trigger: str
    targets: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class ValidationAssessment:
    status: str
    baseline_peak_control_effort_pct: float
    revised_peak_control_effort_pct: float
    baseline_peak_tracking_error_bar: float
    revised_peak_tracking_error_bar: float
    baseline_min_margin: float
    revised_min_margin: float
    moved_bottleneck: bool
    conclusion: str


@dataclass(frozen=True)
class EngineeringReview:
    maintenance: MaintenanceAssessment
    options: tuple[EngineeringOption, ...]
    design_requirement: DesignRequirement | None
    validation: ValidationAssessment


@dataclass
class EngineState:
    previous_frame: TelemetryFrame | None = None
    previous_derived: DerivedState | None = None
    previous_top_hypothesis: str | None = None
    previous_margin: float = 1.0
    belief_state: dict[str, float] = field(default_factory=dict)
    active_action: SimulatedAction | None = None
    evidence_history: list[Evidence] = field(default_factory=list)
    reasoning_history: list[ReasoningSnapshot] = field(default_factory=list)


def to_dict(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "__dataclass_fields__"):
        raw = asdict(obj)
        return _enum_to_value(raw)
    raise TypeError(f"Unsupported object type: {type(obj)!r}")


def _enum_to_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: _enum_to_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_enum_to_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_enum_to_value(v) for v in value)
    return value
