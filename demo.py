from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viral import AuthorityLevel, ViralEngine  # noqa: E402
from viral.reporting import key_events, render_json, render_text  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the V.I.R.A.L. Motorsport public vehicle-intelligence reference demonstration."
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
        help="Print key events as JSON instead of the human-readable engineering trace.",
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
    selected = results if args.all else key_events(results)

    if args.json:
        events = [json.loads(render_json(result)) for result in selected]
        payload = {
            "system": "V.I.R.A.L.™ Motorsport — Vehicle Intelligence Reference Architecture Lab™",
            "scope": "synthetic public reference demonstration",
            "ledger_valid": engine.ledger.validate(),
            "ledger_path": str(ledger_path.relative_to(ROOT)),
            "events": events,
        }
        print(json.dumps(payload, indent=2))
        return 0

    print("V.I.R.A.L.™ Motorsport — Vehicle Intelligence Reference Architecture Lab™")
    print("Synthetic public reference demonstration. No production vehicle control logic is included.\n")

    for result in selected:
        print(render_text(result))
        print("-" * 96)

    print(f"Ledger valid: {engine.ledger.validate()}")
    print(f"Ledger path: {ledger_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
