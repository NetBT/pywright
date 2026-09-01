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