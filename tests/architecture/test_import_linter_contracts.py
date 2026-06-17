import os
import shutil
import site
import subprocess
import sys
import sysconfig
from pathlib import Path


def test_api_student_import_linter_blocks_analytic_imports(tmp_path: Path) -> None:
    """T13: import-linter must reject app.api.student -> app.analytic imports."""
    repo_root = Path(__file__).resolve().parents[2]
    config_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")

    assert "Student API must not import analytic internals" in config_text
    assert "app.api.student" in config_text
    assert "app.analytic" in config_text

    package_root = tmp_path / "app"
    for package in [
        package_root,
        package_root / "api",
        package_root / "api" / "generation",
        package_root / "api" / "student",
        package_root / "analytic",
        package_root / "classification",
        package_root / "domain",
        package_root / "domain" / "analytic",
        package_root / "generation",
        package_root / "projections",
    ]:
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    (package_root / "analytic" / "forbidden_marker.py").write_text("VALUE = 1\n", encoding="utf-8")
    (package_root / "api" / "student" / "violating_router.py").write_text(
        "from app.analytic import forbidden_marker\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(config_text, encoding="utf-8")

    lint_imports = shutil.which("lint-imports")
    if lint_imports is None:
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
                lint_imports = str(candidate)
                break

    assert lint_imports is not None, (
        "lint-imports executable must be available for architecture tests"
    )

    result = subprocess.run(
        [lint_imports, "--config", str(tmp_path / "pyproject.toml"), "--no-cache"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True,
        text=True,
        check=False,
    )

    output = f"{result.stdout}\n{result.stderr}"
    assert result.returncode != 0, output
    assert "Student API must not import analytic internals" in output


def test_generation_cannot_import_classification_or_analytic(tmp_path: Path) -> None:
    """T21: generation must not import classification or analytic internals."""
    repo_root = Path(__file__).resolve().parents[2]
    config_text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")

    assert "Generation must not import classification or analytic internals" in config_text
    assert "app.generation" in config_text
    assert "app.classification" in config_text

    package_root = tmp_path / "app"
    for package in [
        package_root,
        package_root / "api",
        package_root / "api" / "generation",
        package_root / "api" / "student",
        package_root / "analytic",
        package_root / "classification",
        package_root / "domain",
        package_root / "domain" / "analytic",
        package_root / "generation",
        package_root / "projections",
    ]:
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    (package_root / "classification" / "forbidden_marker.py").write_text(
        "VALUE = 1\n",
        encoding="utf-8",
    )
    (package_root / "generation" / "violating_runtime.py").write_text(
        "from app.classification import forbidden_marker\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(config_text, encoding="utf-8")

    lint_imports = shutil.which("lint-imports")
    if lint_imports is None:
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
                lint_imports = str(candidate)
                break

    assert lint_imports is not None, (
        "lint-imports executable must be available for architecture tests"
    )

    result = subprocess.run(
        [lint_imports, "--config", str(tmp_path / "pyproject.toml"), "--no-cache"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True,
        text=True,
        check=False,
    )

    output = f"{result.stdout}\n{result.stderr}"
    assert result.returncode != 0, output
    assert "Generation must not import classification or analytic internals" in output
