from pathlib import Path


def test_model_configuration_uses_stage_roles_not_hardcoded_provider_names() -> None:
    """Architecture docs/config should be model-role agnostic for Phase 1."""
    repo_root = Path(__file__).resolve().parents[2]
    paths = [
        repo_root / "docs" / "architecture" / "backend-architecture.md",
        repo_root / "docs" / "architecture" / "llm-pipeline.md",
        repo_root / "docs" / "planning" / "sdd" / "phase-1-walking-skeleton-sdd.md",
        repo_root / "docs" / "configuration-reference.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    assert "LLM_STAGE1_MODEL_ID" in combined
    assert "LLM_STAGE2_MODEL_ID" in combined
    assert "Stage 1 Generation Model" in combined
    assert "Stage 2 Classification Model" in combined
    assert "claude-" not in combined.lower()
    assert "Claude Haiku" not in combined
    assert "Claude Sonnet" not in combined
