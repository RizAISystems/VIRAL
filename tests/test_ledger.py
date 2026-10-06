from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from viral.ledger import HashChainedLedger


class LedgerTests(unittest.TestCase):
    def test_tamper_detection(self):
        ledger = HashChainedLedger()
        ledger.append("a", {"x": 1})
        ledger.append("b", {"x": 2})
        self.assertTrue(ledger.validate())
        ledger.entries[0]["payload"]["x"] = 99
        self.assertFalse(ledger.validate())


if __name__ == "__main__":
    unittest.main()
