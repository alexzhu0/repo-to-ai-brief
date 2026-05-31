"""Compress a repository into an AI-friendly brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence


SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "dist", "build"}


def iter_files(root: Path) -> List[Path]:
    files = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
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


def build_brief(root_path: str) -> Dict[str, Any]:
    root = Path(root_path)
    files = iter_files(root)
    extensions: Dict[str, int] = {}
    for path in files:
        suffix = path.suffix or "(none)"
        extensions[suffix] = extensions.get(suffix, 0) + 1
    important = [name for name in ["README.md", "pyproject.toml", "package.json", "Cargo.toml"] if (root / name).exists()]
    return {
        "root": str(root),
        "file_count": len(files),
        "extensions": dict(sorted(extensions.items())),
        "important_files": important,
        "readme_headings": read_headings(root / "README.md"),
    }


def format_text(brief: Dict[str, Any]) -> str:
    lines = [f"Root: {brief['root']}", f"Files: {brief['file_count']}", "", "Important files:"]
    lines.extend(f"- {name}" for name in brief["important_files"]) if brief["important_files"] else lines.append("- none")
    lines.extend(["", "Extensions:"])
    lines.extend(f"- {ext}: {count}" for ext, count in brief["extensions"].items())
    lines.extend(["", "README headings:"])
    lines.extend(f"- {heading}" for heading in brief["readme_headings"]) if brief["readme_headings"] else lines.append("- none")
    return "\n".join(lines)


def run(input_path: str, output_format: str = "text") -> str:
    brief = build_brief(input_path)
    if output_format == "json":
        return json.dumps(brief, indent=2, sort_keys=True)
    return format_text(brief)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compress a repository into an AI-friendly brief.")
    parser.add_argument("input", help="Repository directory")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(run(args.input, args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
