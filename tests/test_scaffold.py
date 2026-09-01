from pathlib import Path

from scripts.scaffold import create_project


def test_create_project_includes_ai_docs_and_specs_directory(tmp_path: Path) -> None:
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

    assert (tmp_path / "docs" / "ai-testing-workflow.md").is_file()
    assert (tmp_path / "docs" / "test-plan-template.md").is_file()
    assert (tmp_path / "specs" / ".gitkeep").is_file()