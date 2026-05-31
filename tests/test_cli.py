import json
import tempfile
import unittest
from pathlib import Path

from repo_to_ai_brief.cli import build_brief, run


class RepoToAiBriefTests(unittest.TestCase):
    def test_builds_brief_from_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Title\n## Install\n", encoding="utf-8")
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            brief = build_brief(str(root))
        self.assertEqual(brief["file_count"], 2)
        self.assertIn("README.md", brief["important_files"])

    def test_json_output_contains_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("print(1)\n", encoding="utf-8")
            payload = json.loads(run(str(root), "json"))
        self.assertEqual(payload["extensions"][".py"], 1)


if __name__ == "__main__":
    unittest.main()
