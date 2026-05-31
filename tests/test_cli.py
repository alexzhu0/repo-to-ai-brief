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
        self.assertIn("README.md", brief["tree"])

    def test_json_output_contains_extensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("print(1)\n", encoding="utf-8")
            payload = json.loads(run(str(root), "json"))
        self.assertEqual(payload["extensions"][".py"], 1)

    def test_ignore_patterns_skip_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "keep.py").write_text("print(1)\n", encoding="utf-8")
            (root / "skip.log").write_text("noise\n", encoding="utf-8")

            brief = build_brief(str(root), ignore_patterns=["*.log"])

        self.assertEqual(brief["file_count"], 1)
        self.assertEqual(brief["tree"], ["keep.py"])

    def test_markdown_output_contains_snippets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            output = run(str(root), "markdown", max_chars=80)

        self.assertIn("# AI Repository Brief", output)
        self.assertIn("Selected snippets:", output)

    def test_max_files_limits_selected_snippets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("print('a')\n", encoding="utf-8")
            (root / "b.py").write_text("print('b')\n", encoding="utf-8")

            brief = build_brief(str(root), max_files=1, max_chars=80)

        self.assertEqual(len(brief["snippets"]), 1)

    def test_json_output_includes_budget_and_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            payload = json.loads(run(str(root), "json", max_chars=40))

        self.assertEqual(payload["char_budget"], 40)
        self.assertEqual(payload["tree"], ["README.md"])


if __name__ == "__main__":
    unittest.main()
