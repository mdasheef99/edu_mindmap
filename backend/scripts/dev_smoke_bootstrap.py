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
SESSION_ID = UUID("00000000-0000-4000-8000-000000000030")
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


def _seed_canvas_session(runtime: any) -> None:
    from datetime import datetime, timezone
    from uuid import uuid4
    from app.domain.student.sessions import build_session_started, SessionStartRequest, SessionContext

    # 1. Start Session
    start_req = SessionStartRequest(
        exam_id=EXAM_ID,
        subject_id=SUBJECT_ID,
        chapter_id=CHAPTER_ID,
        concept_entry_id=CONCEPT_ENTRY_ID,
        chapter_analysis_id=CHAPTER_ANALYSIS_ID,
    )
    ctx = SessionContext(tenant_id=TENANT_ID, student_user_id=STUDENT_USER_ID)
    evt, session_row, _ = build_session_started(
        context=ctx,
        request=start_req,
        session_id=SESSION_ID,
    )
    runtime.event_store.append(evt, producer="server")
    runtime.student_sessions.upsert(session_row)  # session_row has tenant_id; session_model does not

    def _evt(etype: str, payload: dict):
        evt = {
            "event_id": uuid4(),
            "event_type": etype,
            "event_version": 1,
            "tenant_id": TENANT_ID,
            "actor_user_id": STUDENT_USER_ID,
            "student_id": STUDENT_USER_ID,
            "session_id": SESSION_ID,
            "occurred_at": datetime.now(timezone.utc),
            "payload": payload,
        }
        # Lift top-level fields required by registry
        for k in ["node_id", "edge_id", "exam_id", "subject_id", "chapter_id", "chapter_analysis_id", "concept_entry_id"]:
            if k in payload:
                evt[k] = payload[k]
        return evt

    node_a_id = str(uuid4())
    node_b_id = str(uuid4())
    edge_id = str(uuid4())
    thread_id = str(uuid4())

    dummy = "00000000-0000-0000-0000-000000000000"

    # 2. Nodes
    runtime.event_store.append(_evt("node_created", {
        "session_id": str(SESSION_ID),
        "student_user_id": str(STUDENT_USER_ID),
        "node_id": node_a_id,
        "node_type": "concept",
        "content": "Electric current",
        "source_node_id": dummy,
        "source_offer_set_id": dummy,
        "source_option_id": dummy,
        "source_option_text": "ROOT",
        "thread_context_id": thread_id,
    }), producer="server")

    runtime.event_store.append(_evt("node_created", {
        "session_id": str(SESSION_ID),
        "student_user_id": str(STUDENT_USER_ID),
        "node_id": node_b_id,
        "node_type": "concept",
        "content": "Ohm's Law",
        "source_node_id": node_a_id,
        "source_offer_set_id": dummy,
        "source_option_id": dummy,
        "source_option_text": "Manual",
        "thread_context_id": thread_id,
    }), producer="server")

    # 3. Edge
    runtime.event_store.append(_evt("edge_created", {
        "edge_id": edge_id,
        "session_id": str(SESSION_ID),
        "node_id": node_a_id,
        "source_node_id": node_a_id,
        "target_node_id": node_b_id,
        "edge_kind": "manual_reference",
        "label": "relates to",
        "created_by": "server",
    }), producer="server")

    # 4. Positions
    runtime.event_store.append(_evt("node_position_updated", {
        "node_id": node_a_id,
        "session_id": str(SESSION_ID),
        "position_x": 100.0,
        "position_y": 100.0,
    }), producer="client")

    runtime.event_store.append(_evt("node_position_updated", {
        "node_id": node_b_id,
        "session_id": str(SESSION_ID),
        "position_x": 300.0,
        "position_y": 150.0,
    }), producer="client")

    # 5. Extra nodes. The initial canvas is 390x844 at scale 1 with 280x180 chips, so the
    # on-screen board box (with cull padding) is roughly x in [-140, 530], y in [-90, 934].
    # The first three sit inside that box (visible on load → exercise the edge-`+`/toolbar/
    # banner layouts); the last two sit outside it (off-screen → exercise viewport culling).
    # Each extra node is connected to a parent (node_a/node_b) by a manual_reference edge so
    # the seeded graph is fully connected — no orphan nodes (every node has ≥1 connection).
    extra_nodes = [
        ("Resistance", 130.0, 340.0, node_a_id, "depends on"),
        ("Voltage", 320.0, 540.0, node_a_id, "drives"),
        ("Short circuit", 150.0, 740.0, node_b_id, "violates"),
        ("Series circuit", 760.0, 220.0, node_b_id, "applies to"),
        ("Parallel circuit", -320.0, 500.0, node_a_id, "splits"),
    ]
    for label, px, py, parent_id, edge_label in extra_nodes:
        nid = str(uuid4())
        runtime.event_store.append(_evt("node_created", {
            "session_id": str(SESSION_ID),
            "student_user_id": str(STUDENT_USER_ID),
            "node_id": nid,
            "node_type": "concept",
            "content": label,
            "source_node_id": parent_id,
            "source_offer_set_id": dummy,
            "source_option_id": dummy,
            "source_option_text": "Manual",
            "thread_context_id": thread_id,
        }), producer="server")
        runtime.event_store.append(_evt("node_position_updated", {
            "node_id": nid,
            "session_id": str(SESSION_ID),
            "position_x": px,
            "position_y": py,
        }), producer="client")
        runtime.event_store.append(_evt("edge_created", {
            "edge_id": str(uuid4()),
            "session_id": str(SESSION_ID),
            "node_id": parent_id,
            "source_node_id": parent_id,
            "target_node_id": nid,
            "edge_kind": "manual_reference",
            "label": edge_label,
            "created_by": "server",
        }), producer="server")


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
    _seed_canvas_session(runtime)
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
