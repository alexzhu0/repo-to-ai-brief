# Repo To AI Brief

Generate a reviewable coding-agent brief from a repository, with tree, manifests, snippets, ignore rules, and an optional changed-files view.

For developers using Codex, Claude Code, Cursor, Copilot, OpenCode, or Gemini CLI who want to give an agent just enough repo context before an edit.

```bash
PYTHONPATH=src python3 -m repo_to_ai_brief examples/sample_repo --max-files 8 --max-chars 1200
```

## Why

Coding agents work better when they start with a concise map of the repository. Full repo packers are useful when you want maximum context; this tool focuses on a smaller, auditable brief you can read before pasting into an agent.

Repo To AI Brief is dependency-light and local-first. It respects `.gitignore` by default, supports explicit ignore patterns, and can summarize only files changed in `git status`.

## Install

```bash
git clone https://github.com/alexzhu0/repo-to-ai-brief.git
cd repo-to-ai-brief
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Quickstart

```bash
PYTHONPATH=src python3 -m repo_to_ai_brief examples/sample_repo --max-files 8 --max-chars 1200
```

## Examples

Human-readable output:

```bash
PYTHONPATH=src python3 -m repo_to_ai_brief examples/sample_repo --max-files 8 --max-chars 1200
```

Changed files only:

```bash
PYTHONPATH=src python3 -m repo_to_ai_brief . --changed-only --max-files 12 --max-chars 2000
```

Machine-readable output:

```bash
PYTHONPATH=src python3 -m repo_to_ai_brief examples/sample_repo --format json
```

## CLI Reference

- `PYTHONPATH=src python3 -m repo_to_ai_brief --help`
- Main demo: `PYTHONPATH=src python3 -m repo_to_ai_brief examples/sample_repo --max-files 8 --max-chars 1200`
- Changed-only demo: `PYTHONPATH=src python3 -m repo_to_ai_brief . --changed-only --max-files 12 --max-chars 2000`
- CI gate: `PYTHONPATH=src python3 -m unittest discover -s tests`

## Features

- Repository tree summary
- Important manifest detection
- README heading extraction
- Extension counts
- Budgeted text snippets
- Repeatable ignore patterns
- `.gitignore` loading by default
- `--changed-only` for coding-agent review context
- Suggested coding-agent prompt template

## API

The public Python surface is intentionally small:

```python
from repo_to_ai_brief.cli import build_brief
```

Use the CLI first. Import the Python functions when you want to embed the same behavior in a larger tool.

## Why Star This

Star this if you want a small, inspectable repo-to-context bridge instead of a black-box context dump.

## Related Tools

- Pair with `agent-trace-summarizer` when an incident report needs repo context.
- Pair with `prompt-drift-watch` when instruction changes need a focused review.
- Use before asking a coding agent to edit a repo.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## FAQ

**Does this call external AI APIs?**

No. The current release uses the Python standard library only.

**Is this production-ready?**

Treat this as a focused utility. Run it in CI or local review first, then adapt thresholds and examples to your workflow.

**Can I contribute examples?**

Yes. The most useful issue or pull request includes a real input file, expected output, and the workflow where it helps.

## Contributing

Issues and pull requests are welcome when they include a concrete use case or failing example.

Run tests before opening a pull request:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## License

MIT
