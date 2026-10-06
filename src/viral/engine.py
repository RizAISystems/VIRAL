from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .actions import PreservationController
from .authority import AuthorityGate
from .evidence import EvidenceAssembler
from .expected_state import SyntheticExpectedStateModel
from .forecast import MarginForecaster
from .ledger import HashChainedLedger
from .models import (
    AuthorityDecision,
    AuthorityLevel,
    DerivedState,
    Forecast,
    ReasoningSnapshot,
    SimulatedAction,
    TelemetryFrame,
    VerificationResult,
    to_dict,
)
from .reasoning import AdaptiveReasoningEngine
from .scenario import FlagshipRaceScenario
from .state import StateInterpreter
from .verification import OutcomeVerifier


@dataclass(frozen=True)
class StepResult:
    frame: TelemetryFrame
    derived: DerivedState
    forecast: Forecast
    reasoning: ReasoningSnapshot
    authority: AuthorityDecision
    action: SimulatedAction | None
    verification: VerificationResult | None


class ViralEngine:
    def __init__(
        self,
        authority_level: AuthorityLevel = AuthorityLevel.A3_SIMULATE,
        ledger_path: str | Path | None = None,
    ) -> None:
        self.expected_model = SyntheticExpectedStateModel()
        self.interpreter = StateInterpreter()
        self.evidence_assembler = EvidenceAssembler()
        self.forecaster = MarginForecaster()
        self.reasoner = AdaptiveReasoningEngine()
        self.authority = AuthorityGate(authority_level)
        self.controller = PreservationController()
        self.verifier = OutcomeVerifier()
        self.ledger = HashChainedLedger(ledger_path)
        self.previous_frame: TelemetryFrame | None = None
        self.previous_expected = None
        self.action_taken = False
        self._last_reasoning: ReasoningSnapshot | None = None

    def step(self, frame: TelemetryFrame) -> StepResult:
        expected = self.expected_model.predict(frame)
        derived = self.interpreter.derive(frame, expected, self.previous_frame, self.previous_expected)
        evidence = self.evidence_assembler.assemble(frame, derived)
        forecast = self.forecaster.update(frame.timestamp_s, derived)
        reasoning = self.reasoner.reason(frame.timestamp_s, evidence, forecast)
        authority = self.authority.evaluate(reasoning, forecast)

        action: SimulatedAction | None = None
        if authority.allowed and not self.action_taken:
            action = self.controller.request(frame.timestamp_s, authority)
            if action.approved:
                self.action_taken = True
                self.verifier.begin(derived.engineering_margin)

        verification = self.verifier.observe(frame.timestamp_s, derived.engineering_margin)

        self.ledger.append("reasoning", {
            "timestamp_s": frame.timestamp_s,
            "engineering_margin": derived.engineering_margin,
            "projected_margin": forecast.projected_margin,
            "top_hypothesis": reasoning.hypotheses[0].key,
            "top_probability": reasoning.hypotheses[0].probability,
            "confidence": reasoning.confidence,
            "revision": reasoning.revision,
            "authority": to_dict(authority),
            "action": to_dict(action) if action else None,
        })
        if verification:
            self.ledger.append("verification", to_dict(verification))

        self.previous_frame = frame
        self.previous_expected = expected
        self._last_reasoning = reasoning

        return StepResult(
            frame=frame,
            derived=derived,
            forecast=forecast,
            reasoning=reasoning,
            authority=authority,
            action=action,
            verification=verification,
        )

    def run_flagship(self) -> list[StepResult]:
        scenario = FlagshipRaceScenario()
        results: list[StepResult] = []
        for t in range(scenario.duration_s + 1):
            frame = scenario.frame(t)
            result = self.step(frame)
            results.append(result)
            if result.action and result.action.approved:
                scenario.apply_action(result.action)
        return results
