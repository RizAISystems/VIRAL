from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viral.authority import AuthorityGate
from viral.models import AuthorityLevel, Forecast, ReasoningSnapshot


class AuthorityTests(unittest.TestCase):
    def snapshot(self, confidence=0.8, abstained=False):
        return ReasoningSnapshot(
            timestamp_s=1,
            what_is_happening="test",
            why_might_it_be_happening=("test",),
            best_explanation="test",
            what_happens_next="test",
            confidence=confidence,
            engineering_response="test",
            hypotheses=(),
            evidence=(),
            revision=None,
            abstained=abstained,
        )

    def test_abstention_blocks_action(self):
        gate = AuthorityGate(AuthorityLevel.A3_SIMULATE)
        decision = gate.evaluate(self.snapshot(abstained=True), Forecast(0.1, 20, "test", "preserve"))
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.requested_level, AuthorityLevel.A1_ADVISE)

    def test_a3_allows_simulated_preservation(self):
        gate = AuthorityGate(AuthorityLevel.A3_SIMULATE)
        decision = gate.evaluate(self.snapshot(), Forecast(0.1, 20, "test", "preserve"))
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.requested_level, AuthorityLevel.A3_SIMULATE)


if __name__ == "__main__":
    unittest.main()
