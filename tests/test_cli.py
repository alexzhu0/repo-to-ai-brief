import json
import subprocess
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

    def test_gitignore_patterns_are_loaded_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gitignore").write_text("private\n", encoding="utf-8")
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            (root / "private").mkdir()
            (root / "private" / "secret.txt").write_text("secret\n", encoding="utf-8")

            brief = build_brief(str(root))

        self.assertEqual(brief["tree"], [".gitignore", "README.md"])

    def test_changed_only_uses_git_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tracked.py").write_text("print('tracked')\n", encoding="utf-8")
            (root / "new.py").write_text("print('new')\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            subprocess.run(["git", "add", "tracked.py"], cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)

            brief = build_brief(str(root), changed_only=True)

        self.assertIn("new.py", brief["tree"])


if __name__ == "__main__":
    unittest.main()
