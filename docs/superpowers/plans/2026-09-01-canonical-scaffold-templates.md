# Canonical Scaffold Templates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `scripts/_templates/` the sole source for generated test-project files, while retaining the root repository as the `pywright` CLI distribution project.

**Architecture:** Move the framework skeleton and generated-project metadata below `scripts/_templates/`. The CLI resolves that package-relative directory in every execution mode and copies only its contents, adding its own `scripts/scaffold.py` as the generated project's maintenance command. Hatchling includes the template tree as package data rather than copying separate root directories during wheel builds.

**Tech Stack:** Python 3.14, standard library, pytest, Hatchling, uv.

---

## File Structure

- Modify: `scripts/scaffold.py` — resolve the one canonical template directory; remove root-repository template discovery and template-specific exclusions that become unnecessary.
- Modify: `tests/test_scaffold.py` — verify the generated project has representative template files, the project README, no generated `docs/` directory, the generated scaffold script, and the package-relative template root.
- Modify: `pyproject.toml` — retain CLI wheel packaging and replace root-to-template force includes with recursive inclusion of the in-package template tree.
- Modify: `README.md` — document `pywright` as the distributed scaffold CLI only.
- Create: `scripts/_templates/README.md` — describe the generated test project and its operations.
- Move: `.env`, `.gitlab-ci.yml`, `.python-version`, `pyproject.toml`, `uv.lock`, `api/`, `auth/`, `config/`, `pages/`, `specs/`, `test_data/`, and `utils/` to `scripts/_templates/`.
- Keep: `docs/` and all of its contents at the repository root; generated projects do not receive a `docs/` directory.
- Move: generated-project test files under `tests/` to `scripts/_templates/tests/`; keep `tests/test_scaffold.py` at the root as the CLI-package test.
- Copy: `.gitignore` to `scripts/_templates/.gitignore` and keep the root copy for CLI repository ignores.
- Delete: root copies of all files and directories moved above.

### Task 1: Lock the canonical template contract with tests

**Files:**
- Modify: `tests/test_scaffold.py`
- Test: `tests/test_scaffold.py`

- [ ] **Step 1: Replace the existing scaffold test with generated-project assertions**

```python
from pathlib import Path

from scripts.scaffold import create_project, template_root


def test_create_project_copies_canonical_template_and_scaffold(tmp_path: Path) -> None:
    assert template_root().name == "_templates"

    create_project(
        tmp_path,
        {
            "name": "sample_project",
            "ui_url": "https://app.example.com",
            "api_url": "https://api.example.com",
            "auth_mode": "api_token",
            "token": "placeholder-token",
        },
        dry_run=False,
    )

    assert (tmp_path / "README.md").is_file()
    assert (tmp_path / "pyproject.toml").is_file()
    assert (tmp_path / "api" / "client.py").is_file()
    assert not (tmp_path / "docs").exists()
    assert (tmp_path / "specs" / ".gitkeep").is_file()
    assert (tmp_path / "scripts" / "scaffold.py").is_file()
    assert not (tmp_path / "scripts" / "_templates").exists()
```

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `uv run pytest tests/test_scaffold.py -m "not smoke or smoke" -q`

Expected: FAIL because `template_root()` currently resolves to the repository root in a source checkout.

- [ ] **Step 3: Commit the failing test**

```shell
 git add tests/test_scaffold.py
 git commit -m "test: define canonical scaffold template output"
```

### Task 2: Move the generated test-project skeleton into the package

**Files:**
- Create: `scripts/_templates/.env`
- Create: `scripts/_templates/.gitignore`
- Create: `scripts/_templates/.gitlab-ci.yml`
- Create: `scripts/_templates/.python-version`
- Create: `scripts/_templates/pyproject.toml`
- Create: `scripts/_templates/uv.lock`
- Create: `scripts/_templates/api/`
- Create: `scripts/_templates/auth/`
- Create: `scripts/_templates/config/`
- Create: `scripts/_templates/pages/`
- Create: `scripts/_templates/specs/`
- Create: `scripts/_templates/test_data/`
- Create: `scripts/_templates/tests/`
- Create: `scripts/_templates/utils/`
- Delete: root copies of each moved file and directory, except the root `.gitignore`, `docs/superpowers/`, and `tests/test_scaffold.py`.

- [ ] **Step 1: Move every generated-project file and directory without changing its contents**

Run:

```shell
$destination = 'scripts/_templates'
New-Item -ItemType Directory -Force $destination | Out-Null
Move-Item .env, .gitlab-ci.yml, .python-version, api, auth, config, pages, specs, test_data, utils $destination
Move-Item uv.lock "$destination/uv.lock"
Copy-Item .gitignore "$destination/.gitignore"
New-Item -ItemType Directory -Force "$destination/docs", "$destination/tests" | Out-Null
Move-Item docs/ai-testing-workflow.md, docs/design-decisions.md, docs/test-plan-template.md "$destination/docs"
Get-ChildItem tests -Force | Where-Object Name -ne 'test_scaffold.py' | Move-Item -Destination "$destination/tests"
```

Keep the root `.gitignore` after copying it because the distribution repository needs its own ignores, including `.worktrees/`. Retain the whole root `docs/` directory and root `tests/test_scaffold.py`, which are distribution-project documentation and development artifacts.

- [ ] **Step 2: Move the generated project configuration**

Run:

```shell
Move-Item pyproject.toml scripts/_templates/pyproject.toml
```

At this point the root package configuration is temporarily absent; it will be recreated in Task 4. Do not edit the moved template configuration except as needed to keep the generated project requirements intact.

- [ ] **Step 3: Verify Git recognizes the intended moves**

Run: `git status --short`

Expected: all framework files appear under `scripts/_templates/` and no root framework-directory copy remains.

### Task 3: Add a generated-project README

**Files:**
- Create: `scripts/_templates/README.md`

- [ ] **Step 1: Create the README for newly scaffolded test projects**

Write `scripts/_templates/README.md` with this content:

```markdown
# pywright test project

This project was created with `pywright`. It provides a pytest + Playwright testing skeleton with Page Objects, an HTTP API facade, environment-based settings, Allure results, and GitLab CI.

## Setup

```shell
uv sync --all-groups
uv run playwright install chromium
```

Update `.env` with the target UI and API endpoints. Keep real credentials out of env files and inject them through `TEST_*__*` environment variables or CI masked variables.

## Run tests

```shell
uv run pytest
uv run pytest -m regression
uv run pytest -m integration
uv run pytest --wip
```

Bare `pytest` runs smoke tests. To select a custom environment, copy `.env` to `.env.<name>` and run `uv run pytest --env <name>`.

## Project layout

- `pages/`: UI page objects and the application facade.
- `api/`: HTTP client, endpoint adapters, and API facade.
- `auth/`: authentication strategies.
- `config/`: typed settings loaded from environment files.
- `test_data/`: fixture data and builders.
- `tests/`: smoke, regression, and integration tests.
- `docs/`: design and AI-assisted testing guidance.
- `specs/`: human-reviewed test plans.

## Quality and reporting

```shell
uv run ruff check .
uv run ruff format --check .
allure generate artifacts/allure-results -o artifacts/allure-report --clean
allure open artifacts/allure-report
```

Use `python scripts/scaffold.py <target>` to create another project from the same installed template.
```

- [ ] **Step 2: Verify the document is present with the moved template files**

Run: `Test-Path scripts/_templates/README.md; Test-Path scripts/_templates/api/client.py; Test-Path scripts/_templates/tests/conftest.py`

Expected: three `True` values.

- [ ] **Step 3: Commit the moved skeleton and generated-project README**

```shell
 git add -A
 git commit -m "refactor: move scaffold project template"
```

### Task 4: Make the CLI and wheel package use the in-package template

**Files:**
- Modify: `scripts/scaffold.py`
- Create: `pyproject.toml`

- [ ] **Step 1: Simplify template-root resolution and exclusions in `scripts/scaffold.py`**

Replace the `EXCLUDE_DIRS` declaration, the `SCAFFOLD_REL` comment, and `template_root()` with:

```python
# scaffold.py itself is appended to the generated project; package templates contain no scripts/ tree.
SCAFFOLD_REL = Path("scripts") / "scaffold.py"


def template_root() -> Path:
    """Return the package-relative canonical test-project template directory."""
    return Path(__file__).resolve().parent / "_templates"
```

Then replace the body of `collect_template_files()` with:

```python
    files = [
        path.relative_to(template_root())
        for path in sorted(template_root().rglob("*"))
        if path.is_file() and path.name not in EXCLUDE_FILES
    ]
    files.append(SCAFFOLD_REL)
    return files
```

Update the module docstring and `_read_template()` docstring so they no longer describe self-replicating root templates or dual-mode lookup. Retain the explicit special case that reads the currently installed `scaffold.py` for `SCAFFOLD_REL`.

- [ ] **Step 2: Recreate root `pyproject.toml` for the distributable CLI**

Create this root file:

```toml
[project]
name = "pywright"
version = "0.1.2"
description = "Pytest + Playwright test-framework scaffold CLI"
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[project.scripts]
pywright = "scripts.scaffold:main"

[dependency-groups]
dev = ["pytest>=8.3", "ruff>=0.8"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["scripts"]

[tool.hatch.build.targets.wheel.force-include]
"scripts/_templates" = "scripts/_templates"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

This removes test-framework runtime dependencies from the CLI package while preserving them inside `scripts/_templates/pyproject.toml` for generated projects.

- [ ] **Step 3: Run the focused scaffold test to verify it passes**

Run: `uv run pytest tests/test_scaffold.py -m "not smoke or smoke" -q`

Expected: PASS with one test passed.

- [ ] **Step 4: Build a wheel and inspect the packaged templates**

Run:

```shell
uv build
$wheel = Get-ChildItem dist/pywright-0.1.2-py3-none-any.whl | Select-Object -First 1
uvx --from $wheel.FullName pywright --dry-run "$env:TEMP/pywright-template-preview"
```

Expected: build succeeds and dry-run lists `README.md`, `api/client.py`, and `scripts/scaffold.py`; it does not list files below `docs/`.

- [ ] **Step 5: Commit CLI and packaging changes**

```shell
 git add scripts/scaffold.py pyproject.toml
 git commit -m "refactor: package canonical scaffold templates"
```

### Task 5: Replace the distribution README and verify the migration

**Files:**
- Modify: `README.md`
- Test: `tests/test_scaffold.py`

- [ ] **Step 1: Replace the root README with CLI distribution documentation**

Write a concise root README containing:

```markdown
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
uv run pytest tests/test_scaffold.py -m "not smoke or smoke" -q
uv build
```
```

- [ ] **Step 2: Run the focused test and wheel smoke test**

Run:

```shell
uv run pytest tests/test_scaffold.py -m "not smoke or smoke" -q
Remove-Item -Recurse -Force "$env:TEMP/pywright-generated-smoke" -ErrorAction SilentlyContinue
uvx --from (Get-ChildItem dist/pywright-0.1.2-py3-none-any.whl | Select-Object -First 1).FullName pywright "$env:TEMP/pywright-generated-smoke"
Test-Path "$env:TEMP/pywright-generated-smoke/README.md"
Test-Path "$env:TEMP/pywright-generated-smoke/api/client.py"
Test-Path "$env:TEMP/pywright-generated-smoke/scripts/scaffold.py"
```

Expected: pytest passes; CLI exits successfully; each `Test-Path` command prints `True`.

- [ ] **Step 3: Run the complete CLI-project quality suite**

Run:

```shell
uv run ruff check scripts tests
uv run ruff format --check scripts tests
uv run pytest -m "not smoke or smoke" -q
```

Expected: ruff reports no violations and pytest reports no failures. The explicit marker expression prevents the old template test configuration's default smoke-only selection from hiding CLI tests.

- [ ] **Step 4: Review the complete diff**

Run: `git diff main...HEAD --check; git diff main...HEAD --stat; git status --short`

Expected: no whitespace errors; intended template moves, CLI updates, package metadata, README split, and test update only.

- [ ] **Step 5: Commit final documentation and verification changes**

```shell
 git add README.md tests/test_scaffold.py scripts/_templates
 git commit -m "docs: separate scaffold and project guidance"
```
