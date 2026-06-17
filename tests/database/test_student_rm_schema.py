from pathlib import Path


def test_student_rm_has_no_forbidden_columns() -> None:
    """T18: student_rm schema must be structurally unable to store analytic fields."""
    from app.database.schema_checks import find_student_rm_forbidden_columns

    repo_root = Path(__file__).resolve().parents[2]
    migration_path = (
        repo_root / "backend" / "migrations" / "versions" / "0001_phase_1_walking_skeleton.py"
    )

    assert find_student_rm_forbidden_columns(migration_path) == []
