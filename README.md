# pywright

`pywright` is a CLI that creates a ready-to-customize pytest + Playwright testing-project skeleton.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Install

```shell
uv tool install git+https://github.com/NetBT/pywright
```

## Create a project

```shell
pywright ./my-test-project
pywright ./my-test-project --name my_test_project --ui-url https://app.example.com --api-url https://api.example.com
pywright ./my-test-project --install --git
pywright ./my-test-project --dry-run
```

Use `pywright --help` for all options. The generated project's `README.md` covers configuration, test commands, reports, and its directory layout.

## Development

```shell
uv sync --all-groups
uv run pytest -q
uv build
```

The root [docs](docs) directory contains design decisions and workflow guidance for maintaining this scaffold; it is not copied into generated projects.
