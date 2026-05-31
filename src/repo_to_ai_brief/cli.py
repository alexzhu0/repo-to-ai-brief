"""Compress a repository into an AI-friendly brief."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Sequence


SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "dist", "build"}
TEXT_EXTENSIONS = {".md", ".py", ".js", ".ts", ".tsx", ".json", ".toml", ".yaml", ".yml", ".txt"}


def ignored(path: Path, root: Path, ignore_patterns: Sequence[str]) -> bool:
    relative = path.relative_to(root).as_posix()
    return any(fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(path.name, pattern) for pattern in ignore_patterns)


def load_gitignore_patterns(root: Path) -> List[str]:
    path = root / ".gitignore"
    if not path.exists():
        return []
    patterns = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pattern = line.rstrip("/")
            patterns.append(pattern)
            if "*" not in pattern:
                patterns.append(f"{pattern}/*")
    return patterns


def changed_files(root: Path) -> List[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "status", "--short"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        relative = line[3:].strip()
        if " -> " in relative:
            relative = relative.split(" -> ", 1)[1]
        path = root / relative
        if path.is_file():
            files.append(path)
    return sorted(files)


def iter_files(
    root: Path,
    ignore_patterns: Sequence[str] = (),
    changed_only: bool = False,
) -> List[Path]:
    if changed_only:
        candidates = changed_files(root)
    else:
        candidates = [path for path in root.rglob("*") if path.is_file()]
    files = []
    for path in candidates:
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and not ignored(path, root, ignore_patterns):
            files.append(path)
    return sorted(files)


def read_headings(path: Path) -> List[str]:
    if not path.exists():
        return []
    headings = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("#"):
            headings.append(line.lstrip("#").strip())
    return headings[:12]


def build_tree(root: Path, files: Sequence[Path], limit: int = 80) -> List[str]:
    lines = []
    for path in files[:limit]:
        lines.append(path.relative_to(root).as_posix())
    if len(files) > limit:
        lines.append(f"... {len(files) - limit} more file(s)")
    return lines


def read_snippet(path: Path, char_budget: int) -> str:
    if path.suffix.lower() not in TEXT_EXTENSIONS or char_budget <= 0:
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore").strip()
    return text[:char_budget]


def build_brief(
    root_path: str,
    max_files: int = 20,
    max_chars: int = 800,
    ignore_patterns: Sequence[str] = (),
    use_gitignore: bool = True,
    changed_only: bool = False,
) -> Dict[str, Any]:
    root = Path(root_path)
    combined_ignores = list(ignore_patterns)
    if use_gitignore:
        combined_ignores.extend(load_gitignore_patterns(root))
    files = iter_files(root, combined_ignores, changed_only=changed_only)
    extensions: Dict[str, int] = {}
    for path in files:
        suffix = path.suffix or "(none)"
        extensions[suffix] = extensions.get(suffix, 0) + 1
    important = [name for name in ["README.md", "pyproject.toml", "package.json", "Cargo.toml"] if (root / name).exists()]
    selected = files[:max_files]
    per_file_budget = max(0, max_chars // max(1, len(selected)))
    snippets = {
        path.relative_to(root).as_posix(): read_snippet(path, per_file_budget)
        for path in selected
        if read_snippet(path, per_file_budget)
    }
    return {
        "root": str(root),
        "file_count": len(files),
        "char_budget": max_chars,
        "changed_only": changed_only,
        "ignore_patterns": combined_ignores,
        "extensions": dict(sorted(extensions.items())),
        "important_files": important,
        "readme_headings": read_headings(root / "README.md"),
        "tree": build_tree(root, files),
        "snippets": snippets,
        "prompt_template": (
            "Use this brief as repository context. First identify the likely edit surface, "
            "then propose the smallest safe change, then list tests to run."
        ),
    }


def format_text(brief: Dict[str, Any]) -> str:
    lines = [
        "# AI Repository Brief",
        "",
        f"Root: {brief['root']}",
        f"Files: {brief['file_count']}",
        f"Character budget: {brief['char_budget']}",
        f"Changed only: {brief['changed_only']}",
        "",
        "Important files:",
    ]
    lines.extend(f"- {name}" for name in brief["important_files"]) if brief["important_files"] else lines.append("- none")
    lines.extend(["", "Extensions:"])
    lines.extend(f"- {ext}: {count}" for ext, count in brief["extensions"].items())
    lines.extend(["", "README headings:"])
    lines.extend(f"- {heading}" for heading in brief["readme_headings"]) if brief["readme_headings"] else lines.append("- none")
    lines.extend(["", "Tree:"])
    lines.extend(f"- {item}" for item in brief["tree"]) if brief["tree"] else lines.append("- none")
    lines.extend(["", "Suggested coding-agent prompt:", "", brief["prompt_template"]])
    if brief["snippets"]:
        lines.extend(["", "Selected snippets:"])
        for name, snippet in brief["snippets"].items():
            lines.extend([f"## {name}", "", "```text", snippet, "```", ""])
    return "\n".join(lines)


def run(
    input_path: str,
    output_format: str = "text",
    max_files: int = 20,
    max_chars: int = 800,
    ignore_patterns: Sequence[str] = (),
    use_gitignore: bool = True,
    changed_only: bool = False,
) -> str:
    brief = build_brief(
        input_path,
        max_files=max_files,
        max_chars=max_chars,
        ignore_patterns=ignore_patterns,
        use_gitignore=use_gitignore,
        changed_only=changed_only,
    )
    if output_format == "json":
        return json.dumps(brief, indent=2, sort_keys=True)
    return format_text(brief)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compress a repository into an AI-friendly brief.")
    parser.add_argument("input", help="Repository directory")
    parser.add_argument("--format", choices=["text", "markdown", "json"], default="text")
    parser.add_argument("--max-files", type=int, default=20)
    parser.add_argument("--max-chars", type=int, default=800)
    parser.add_argument("--ignore", action="append", default=[], help="Glob pattern to skip; can be repeated")
    parser.add_argument("--no-gitignore", action="store_true", help="Do not load ignore patterns from .gitignore")
    parser.add_argument("--changed-only", action="store_true", help="Include only files reported by git status --short")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(
        run(
            args.input,
            args.format,
            max_files=args.max_files,
            max_chars=args.max_chars,
            ignore_patterns=args.ignore,
            use_gitignore=not args.no_gitignore,
            changed_only=args.changed_only,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
