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
- `specs/`: human-reviewed test plans.

## Quality and reporting

```shell
uv run ruff check .
uv run ruff format --check .
allure generate artifacts/allure-results -o artifacts/allure-report --clean
allure open artifacts/allure-report
```

Use `python scripts/scaffold.py <target>` to create another project from the same installed template.
