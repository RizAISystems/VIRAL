from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class HashChainedLedger:
    """Small append-only evidence ledger used by the public demonstrator."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self.entries: list[dict[str, Any]] = []
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("", encoding="utf-8")

    def append(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        previous_hash = self.entries[-1]["hash"] if self.entries else "GENESIS"
        body = {
            "sequence": len(self.entries) + 1,
            "event_type": event_type,
            "previous_hash": previous_hash,
            "payload": payload,
        }
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        entry = {**body, "hash": digest}
        self.entries.append(entry)
        if self.path:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry

    def validate(self) -> bool:
        previous = "GENESIS"
        for index, entry in enumerate(self.entries, start=1):
            body = {
                "sequence": index,
                "event_type": entry["event_type"],
                "previous_hash": previous,
                "payload": entry["payload"],
            }
            canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
            expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if entry["hash"] != expected or entry["previous_hash"] != previous:
                return False
            previous = entry["hash"]
        return True
