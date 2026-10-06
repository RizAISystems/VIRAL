from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viral import AuthorityLevel, EngineeringReviewPlanner, ViralEngine  # noqa: E402
from viral.models import to_dict  # noqa: E402
from viral.reporting import (  # noqa: E402
    key_events,
    render_engineering_review,
    render_json,
    render_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the V.I.R.A.L. Motorsport public engineering-intelligence demonstrator."
    )
    parser.add_argument(
        "--authority",
        choices=["A0", "A1", "A2", "A3"],
        default="A3",
        help="Maximum public demo authority level. A3 permits simulated preservation only.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the decision trace and engineering lifecycle review as JSON.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Print every frame rather than only the key decision events.",
    )
    parser.add_argument(
        "--ledger",
        default="artifacts/viral_ledger.jsonl",
        help="Path for the append-only hash-chained evidence ledger.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    level_map = {
        "A0": AuthorityLevel.A0_OBSERVE,
        "A1": AuthorityLevel.A1_ADVISE,
        "A2": AuthorityLevel.A2_REQUEST,
        "A3": AuthorityLevel.A3_SIMULATE,
    }

    ledger_path = ROOT / args.ledger
    engine = ViralEngine(authority_level=level_map[args.authority], ledger_path=ledger_path)
    results = engine.run_flagship()

    # A second run applies a synthetic engineering revision under the same duty
    # cycle. A1 prevents a preservation action from masking whether the
    # engineering change itself improved the underlying relationship.
    validation_engine = ViralEngine(authority_level=AuthorityLevel.A1_ADVISE)
    revised_results = validation_engine.run_flagship(engineering_revision=True)

    review = EngineeringReviewPlanner().build_review(results, revised_results)
    engine.ledger.append("engineering_review", to_dict(review))

    selected = results if args.all else key_events(results)

    if args.json:
        events = [json.loads(render_json(result)) for result in selected]
        payload = {
            "system": "V.I.R.A.L.™ Motorsport — Vehicle Intelligence Reference Architecture Lab™",
            "scope": "synthetic public engineering-intelligence demonstrator",
            "ledger_valid": engine.ledger.validate(),
            "ledger_path": str(ledger_path.relative_to(ROOT)),
            "events": events,
            "engineering_review": to_dict(review),
        }
        print(json.dumps(payload, indent=2))
        return 0

    print("V.I.R.A.L.™ Motorsport — Vehicle Intelligence Reference Architecture Lab™")
    print(
        "Synthetic public engineering-intelligence demonstrator. "
        "No production vehicle control logic is included.\n"
    )

    for result in selected:
        print(render_text(result))
        print("-" * 96)

    print()
    print(render_engineering_review(review))
    print("-" * 96)
    print(f"Ledger valid: {engine.ledger.validate()}")
    print(f"Ledger path: {ledger_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
