from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viral import AuthorityLevel, EngineeringReviewPlanner, ViralEngine


class EngineeringLifecycleTests(unittest.TestCase):
    def build_review(self):
        baseline_engine = ViralEngine(authority_level=AuthorityLevel.A3_SIMULATE)
        baseline = baseline_engine.run_flagship()

        revised_engine = ViralEngine(authority_level=AuthorityLevel.A1_ADVISE)
        revised = revised_engine.run_flagship(engineering_revision=True)

        return EngineeringReviewPlanner().build_review(baseline, revised)

    def test_condition_based_maintenance_is_generated(self):
        review = self.build_review()
        self.assertIn("Inspect", review.maintenance.recommendation)
        self.assertGreaterEqual(review.maintenance.confidence, 0.70)
        self.assertGreaterEqual(len(review.maintenance.basis), 3)

    def test_engineering_options_are_ranked(self):
        review = self.build_review()
        self.assertEqual(review.options[0].rank, 1)
        self.assertEqual(review.options[0].name, "Flow-path efficiency redesign")
        self.assertGreater(review.options[0].score, review.options[-1].score)

    def test_design_requirement_is_generated_when_catalog_fails_constraints(self):
        review = self.build_review()
        self.assertIsNotNone(review.design_requirement)
        self.assertGreaterEqual(len(review.design_requirement.targets), 5)
        self.assertIn("No synthetic catalog candidate", review.design_requirement.trigger)

    def test_engineering_revision_is_measurably_validated(self):
        review = self.build_review()
        v = review.validation
        self.assertEqual(v.status, "validated")
        self.assertLess(v.revised_peak_control_effort_pct, v.baseline_peak_control_effort_pct)
        self.assertLess(v.revised_peak_tracking_error_bar, v.baseline_peak_tracking_error_bar)
        self.assertGreater(v.revised_min_margin, v.baseline_min_margin)
        self.assertFalse(v.moved_bottleneck)


if __name__ == "__main__":
    unittest.main()
