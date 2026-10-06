from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RuntimeBoundaryTests(unittest.TestCase):
    def test_public_runtime_uses_standard_library_only(self):
        allowed_top_level = {
            "__future__", "argparse", "collections", "dataclasses", "enum",
            "hashlib", "json", "math", "pathlib", "sys", "typing", "viral",
        }
        files = list((ROOT / "src" / "viral").glob("*.py")) + [ROOT / "demo.py"]
        for path in files:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module.split(".")[0]]
                else:
                    continue
                for name in names:
                    self.assertIn(name, allowed_top_level, f"Unexpected external import {name!r} in {path}")

    def test_no_network_or_vehicle_io_modules(self):
        forbidden = {"socket", "requests", "httpx", "can", "obd", "serial", "subprocess"}
        files = list((ROOT / "src" / "viral").glob("*.py")) + [ROOT / "demo.py"]
        for path in files:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text)
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
            self.assertTrue(imports.isdisjoint(forbidden), f"Forbidden runtime I/O module in {path}")


if __name__ == "__main__":
    unittest.main()
