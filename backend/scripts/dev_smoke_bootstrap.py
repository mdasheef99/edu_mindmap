"""Dev-smoke bootstrap — NEVER run in production.

Usage:
    python backend/scripts/dev_smoke_bootstrap.py --dev-smoke [--port 8000]

Guards:
- Refuses without --dev-smoke flag.
- Refuses if APP_ENV or MINDMAP_ENV == 'production'.
- Uses a hardcoded dev-only JWT secret ('dev-smoke-secret'); never touches real credentials.
- Binds to 0.0.0.0 for LAN reachability; trusted-network-only.

Traceability: docs/planning/sdd/phase-3-phrase-selection-sdd.md §12
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
from pathlib import Path
from uuid import UUID

# --- Python path: make 'app.*' importable from backend/ ---
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_BACKEND = _REPO_ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

# ---- Fixed deterministic IDs (match Phase1WalkingSkeletonScreen.tsx) ----
EXAM_ID = UUID("00000000-0000-4000-8000-000000000001")
SUBJECT_ID = UUID("00000000-0000-4000-8000-000000000002")
CHAPTER_ID = UUID("00000000-0000-4000-8000-000000000003")
CONCEPT_ENTRY_ID = UUID("00000000-0000-4000-8000-000000000004")
CHAPTER_ANALYSIS_ID = UUID("00000000-0000-4000-8000-000000000005")
TENANT_ID = UUID("00000000-0000-4000-8000-000000000010")
STUDENT_USER_ID = UUID("00000000-0000-4000-8000-000000000020")
CONCEPT_ID = UUID("00000000-0000-4000-8000-000000000006")

DEV_JWT_SECRET = "dev-smoke-secret"  # Never a production value.

READER_PASSAGE = (
    "Electric current flows through a closed circuit.\n\n"
    "When resistance increases, current decreases according to Ohm's Law.\n\n"
    "A short circuit occurs when current bypasses the intended load."
)

CHAPTER_PAGES = [READER_PASSAGE]


def _refuse_production() -> None:
    for var in ("APP_ENV", "MINDMAP_ENV"):
        if os.environ.get(var, "").lower() == "production":
            sys.exit(
                f"[dev-smoke] REFUSED: {var}=production. "
                "This script must never run in a production environment."
            )


def _lan_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def _mint_token() -> str:
    import jwt  # PyJWT

    return jwt.encode({"sub": str(STUDENT_USER_ID)}, DEV_JWT_SECRET, algorithm="HS256")


def _build_runtime():  # type: ignore[return]
    from app.main import InMemoryMembershipStore, SessionRuntime
    from app.projections.curriculum import CurriculumIngestInput, build_curriculum_rows

    curriculum_input = CurriculumIngestInput(
        tenant_id=TENANT_ID,
        exam_id=EXAM_ID,
        subject_id=SUBJECT_ID,
        chapter_id=CHAPTER_ID,
        title="Electricity — Dev Smoke Chapter",
        chapter_analysis_id=CHAPTER_ANALYSIS_ID,
        segment_index_version="dev-smoke-v1",
        pipeline_version="dev-smoke-v1",
        prompt_version="dev-smoke-v1",
        model_id="dev-smoke-fixture",
        pages=CHAPTER_PAGES,
        named_concepts=[
            {
                "concept_id": str(CONCEPT_ID),
                "label": "Electric current",
                "definition": "Rate of flow of electric charge.",
                "category_tag": "quantity",
                "passage_refs": {
                    "definitional": [f"{CHAPTER_ID}_para_001"],
                    "explanatory": [],
                    "application": [],
                },
            }
        ],
        embedded_concepts=[],
        edges=[],
    )

    memberships = InMemoryMembershipStore()
    memberships.add_membership(user_id=STUDENT_USER_ID, tenant_id=TENANT_ID, role="student")

    runtime = SessionRuntime.for_testing(
        tenant_id=TENANT_ID,
        student_user_id=STUDENT_USER_ID,
        jwt_secret=DEV_JWT_SECRET,
        memberships=memberships,
    )
    runtime.curriculum.ingest(build_curriculum_rows(curriculum_input))
    return runtime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev-smoke",
        action="store_true",
        required=True,
        help="Required safety flag. Do not use in production.",
    )
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    _refuse_production()

    runtime = _build_runtime()
    token = _mint_token()
    lan_ip = _lan_ip()
    api_base_url = f"http://{lan_ip}:{args.port}"

    print("\n" + "=" * 60)
    print("  M2 DEV SMOKE BOOTSTRAP — TRUSTED LAN ONLY")
    print("=" * 60)
    print(f"  apiBaseUrl : {api_base_url}")
    print("  authToken  : [printed below — do not share]")
    print(f"  Exam ID    : {EXAM_ID}")
    print(f"  Subject ID : {SUBJECT_ID}")
    print(f"  Chapter ID : {CHAPTER_ID}")
    print(f"  Concept ID : {CONCEPT_ID}")
    print("=" * 60)
    print(token)
    print("=" * 60 + "\n")

    import uvicorn
    from app.main import create_app

    app = create_app(runtime=runtime)
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
