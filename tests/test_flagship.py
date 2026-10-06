from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viral import AuthorityLevel, ViralEngine


class FlagshipScenarioTests(unittest.TestCase):
    def run_engine(self, level=AuthorityLevel.A3_SIMULATE):
        engine = ViralEngine(authority_level=level)
        results = engine.run_flagship()
        return engine, results

    def test_no_hard_limit_crossing_before_action(self):
        _, results = self.run_engine()
        action_index = next(i for i, r in enumerate(results) if r.action and r.action.approved)
        self.assertFalse(any(r.derived.hard_limit_crossed for r in results[: action_index + 1]))

    def test_detects_nonconformance_before_any_driver_report(self):
        _, results = self.run_engine()
        first_signal = next(
            r for r in results
            if any(e.direction == "support" for e in r.reasoning.evidence)
            and r.reasoning.confidence >= 0.34
        )
        self.assertIsNone(first_signal.frame.driver_report)
        self.assertLess(first_signal.frame.timestamp_s, 60)

    def test_control_effort_precursor_precedes_achieved_state_divergence(self):
        _, results = self.run_engine()
        first_effort = next(
            r for r in results
            if any(e.code == "rising_control_effort" for e in r.reasoning.evidence)
        )
        first_divergence = next(
            r for r in results
            if any(e.code == "requested_achieved_divergence" for e in r.reasoning.evidence)
        )
        self.assertLess(first_effort.frame.timestamp_s, first_divergence.frame.timestamp_s)
        self.assertIsNone(first_effort.frame.driver_report)
        self.assertFalse(first_effort.derived.hard_limit_crossed)
        self.assertLess(first_effort.derived.boost_tracking_error_bar, 0.055)

    def test_hypothesis_revision_occurs(self):
        _, results = self.run_engine()
        revisions = [r.reasoning.revision for r in results if r.reasoning.revision]
        self.assertTrue(revisions)
        self.assertTrue(any("Air-charge / performance-control deviation" in r for r in revisions))

    def test_bounded_preservation_action_occurs(self):
        _, results = self.run_engine()
        actions = [r.action for r in results if r.action and r.action.approved]
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].name, "bounded_preservation_state")
        self.assertEqual(actions[0].demand_reduction_pct, 8.0)

    def test_preservation_stabilizes_synthetic_state(self):
        _, results = self.run_engine()
        verifications = [r.verification for r in results if r.verification]
        self.assertEqual(len(verifications), 1)
        self.assertEqual(verifications[0].status, "stabilized")
        self.assertGreater(verifications[0].margin_after, verifications[0].margin_before)

    def test_lower_authority_blocks_action(self):
        _, results = self.run_engine(AuthorityLevel.A1_ADVISE)
        self.assertFalse(any(r.action and r.action.approved for r in results))
        self.assertTrue(any(r.forecast.urgency == "preserve" for r in results))

    def test_ledger_is_hash_valid(self):
        engine, _ = self.run_engine()
        self.assertTrue(engine.ledger.validate())
        self.assertGreater(len(engine.ledger.entries), 100)

    def test_system_is_not_waiting_for_threshold(self):
        _, results = self.run_engine()
        preservation = next(r for r in results if r.action and r.action.approved)
        self.assertFalse(preservation.derived.hard_limit_crossed)
        self.assertLess(preservation.forecast.projected_margin, preservation.derived.engineering_margin)


if __name__ == "__main__":
    unittest.main()
