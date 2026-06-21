import os
import shutil
import site
import subprocess
import sys
import sysconfig
from pathlib import Path


def _resolve_lint_imports() -> str:
    lint_imports = shutil.which("lint-imports")
    if lint_imports is not None:
        return lint_imports

    script_name = "lint-imports.exe" if os.name == "nt" else "lint-imports"
    user_scripts = (
        Path(site.getuserbase())
        / f"Python{sys.version_info.major}{sys.version_info.minor}"
        / "Scripts"
    )
    for candidate in [
        Path(sysconfig.get_path("scripts")) / script_name,
        user_scripts / script_name,
    ]:
        if candidate.exists():
            return str(candidate)

    raise AssertionError("lint-imports executable must be available for architecture tests")


def _write_minimal_import_linter_package_tree(tmp_path: Path) -> Path:
    package_root = tmp_path / "app"
    for package in [
        package_root,
        package_root / "analytic",
        package_root / "api",
        package_root / "api" / "generation",
        package_root / "api" / "student",
        package_root / "chapter_analysis",
        package_root / "classification",
        package_root / "domain",
        package_root / "domain" / "analytic",
        package_root / "generation",
        package_root / "projections",
    ]:
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
    return package_root


def test_chapter_analysis_cannot_import_classification_or_generation(tmp_path: Path) -> None:
    """SDD §9 T12: chapter_analysis must stay isolated from generation/classification."""
    repo_root = Path(__file__).resolve().parents[2]
    config_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")

    assert "Chapter analysis must not import generation or classification" in config_text
    assert "app.chapter_analysis" in config_text
    assert "app.classification" in config_text
    assert "app.generation" in config_text

    package_root = _write_minimal_import_linter_package_tree(tmp_path)

    (package_root / "classification" / "forbidden_marker.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    (package_root / "chapter_analysis" / "violating_pipeline.py").write_text(
        "from app.classification import forbidden_marker\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(config_text, encoding="utf-8")

    result = subprocess.run(
        [_resolve_lint_imports(), "--config", str(tmp_path / "pyproject.toml"), "--no-cache"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True,
        text=True,
        check=False,
    )

    output = f"{result.stdout}\n{result.stderr}"
    assert result.returncode != 0, output
    assert "Chapter analysis must not import generation or classification" in output


def test_chapter_analysis_cannot_import_api(tmp_path: Path) -> None:
    """SDD §9 T13: chapter_analysis must not import request-driven API modules."""
    repo_root = Path(__file__).resolve().parents[2]
    config_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")

    assert "Chapter analysis must not import API modules" in config_text
    assert "app.chapter_analysis" in config_text
    assert "app.api" in config_text

    package_root = _write_minimal_import_linter_package_tree(tmp_path)

    (package_root / "api" / "student" / "forbidden_marker.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    (package_root / "chapter_analysis" / "violating_pipeline.py").write_text(
        "from app.api.student import forbidden_marker\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(config_text, encoding="utf-8")

    result = subprocess.run(
        [_resolve_lint_imports(), "--config", str(tmp_path / "pyproject.toml"), "--no-cache"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True,
        text=True,
        check=False,
    )

    output = f"{result.stdout}\n{result.stderr}"
    assert result.returncode != 0, output
    assert "Chapter analysis must not import API modules" in output
