# Repo To AI Brief

Compress a repository into an AI-friendly brief.

## Why

Coding agents work better when they start with a concise map of files, manifests, README headings, and snippets.

This is a flagship HighStar AI developer tool: dependency-light, local-first, and built around one quick command.

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

Machine-readable output:

```bash
PYTHONPATH=src python3 -m repo_to_ai_brief examples/sample_repo --format json
```

## CLI Reference

- `PYTHONPATH=src python3 -m repo_to_ai_brief --help`
- Main demo: `PYTHONPATH=src python3 -m repo_to_ai_brief examples/sample_repo --max-files 8 --max-chars 1200`
- CI gate: `PYTHONPATH=src python3 -m unittest discover -s tests`

## Features

- Repository tree summary
- Important manifest detection
- README heading extraction
- Extension counts
- Budgeted text snippets
- Repeatable ignore patterns

## API

The public Python surface is intentionally small:

```python
from repo_to_ai_brief.cli import build_brief
```

Use the CLI first. Import the Python functions when you want to embed the same behavior in a larger tool.

## Why Star This

It is a simple bridge between raw repositories and coding-agent context windows.

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
