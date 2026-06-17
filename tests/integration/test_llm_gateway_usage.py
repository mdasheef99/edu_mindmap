from uuid import uuid4


def test_fixture_classification_records_first_llm_usage_call() -> None:
    """Phase 1 DoD: llm_gateway usage counter records from the first call."""
    from app.llm_gateway.classification_fixture import classify_selected_option
    from app.llm_gateway.usage import InMemoryLLMUsageStore

    store = InMemoryLLMUsageStore()
    tenant_id = uuid4()

    result = classify_selected_option(
        "Why does roughness increase friction?",
        tenant_id=tenant_id,
        usage_store=store,
    )

    assert result["model_id"] == "stage-2-classification-fixture-model"
    assert len(store.records) == 1
    record = store.records[0]
    assert record.tenant_id == tenant_id
    assert record.purpose == "classification"
    assert record.model_id == result["model_id"]
    assert record.prompt_version == result["prompt_version"]
    assert record.prompt_tokens > 0
    assert record.completion_tokens > 0
