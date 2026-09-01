# Canonical Scaffold Templates Design

## Goal

Make `scripts/_templates/` the single source of generated test-project files. Keep the repository root as the distributable `pywright` CLI project.

## Repository Layout

The root keeps the package metadata, CLI implementation, CLI-focused tests, license, and package README. The package README documents installing and using `pywright`; it no longer describes the generated test project as though it were the root repository.

Move these generated-project directories to `scripts/_templates/`:

- `api/`
- `auth/`
- `config/`
- `pages/`
- `specs/`
- `test_data/`
- `tests/`
- `utils/`

Move generated-project root files there as well: `.env`, `.gitignore`, `.gitlab-ci.yml`, `.python-version`, `pyproject.toml`, and `uv.lock`.

Keep `docs/` at the repository root. It documents the distributed scaffold rather than generated projects, so it is not copied to newly created projects.

Create `scripts/_templates/README.md` for the generated test project's framework overview, configuration, testing workflow, and directory layout. The root `README.md` remains the CLI distribution guide.

## Scaffold Behavior

`scripts.scaffold.template_root()` always resolves to its adjacent `_templates` directory, whether invoked from the source checkout or an installed wheel. `collect_template_files()` copies all template files without repository-specific exclusion rules. Generated projects do not contain a `scripts/` directory: the installed `pywright` CLI remains the only scaffold command.

## Packaging

The wheel contains only the `scripts` package. Since templates now live below that package, remove root-to-template `force-include` mappings and rely on Hatchling's normal recursive inclusion of package files so source and installed CLI behavior use identical files.

## Validation

Extend scaffold tests to assert a generated project contains the template README and representative source files, but no `docs/` or `scripts/` directory. Build a wheel and invoke its installed CLI in a temporary tool environment or isolated directory to verify package-data inclusion and generated output.

## Out of Scope

Do not change the generated framework's test behavior, dependencies, page/API implementations, or scaffold CLI options. Do not retain a root-directory template fallback or a synchronization process; the templates are edited directly under `scripts/_templates/`.
