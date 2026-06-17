"""Static schema checks that preserve Category Invisibility."""

from __future__ import annotations

from pathlib import Path

FORBIDDEN_STUDENT_RM_COLUMN_PATTERNS = (
    "dimension",
    "dimensional",
    "classification",
    "classified",
    "coverage",
    "gap",
    "score",
    "confidence",
    "entropy",
    "dispersion",
    "vector",
    "profile",
    "weight",
    "propensity",
    "probe",
    "steer_reason",
    "teacher_followup",
    "teacher_suggestion",
)


def find_student_rm_forbidden_columns(migration_path: Path) -> list[str]:
    """Return forbidden student_rm column names declared in a migration file."""
    migration_text = migration_path.read_text(encoding="utf-8")
    columns: list[str] = []
    in_student_table = False

    for raw_line in migration_text.splitlines():
        line = raw_line.strip()
        lower_line = line.lower()
        if lower_line.startswith("create table student_rm."):
            in_student_table = True
            continue
        if in_student_table and lower_line.startswith(");"):
            in_student_table = False
            continue
        if not in_student_table or not line or line.startswith("--"):
            continue
        column_name = line.split()[0].strip('"').lower()
        if column_name in {"primary", "foreign", "unique", "check", "constraint"}:
            continue
        if any(pattern in column_name for pattern in FORBIDDEN_STUDENT_RM_COLUMN_PATTERNS):
            columns.append(column_name)

    return sorted(columns)
