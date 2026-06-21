from pathlib import Path


def test_mobile_reader_phrase_sheet_uses_reader_surface_and_student_api() -> None:
    component_path = Path("mobile/PhraseSelectionReaderSheet.tsx")

    assert component_path.exists()
    source = component_path.read_text(encoding="utf-8")
    assert "TextInput" in source
    assert "onSelectionChange" in source
    assert "/v1/student/offer-sets/phrase" in source
    assert "/v1/student/offer-sets/${offerSet.offer_set_id}/choices" in source
    assert "selection_surface" not in source


def test_mobile_reader_phrase_sheet_has_no_provider_credentials_or_in_node_selection() -> None:
    source = Path("mobile/PhraseSelectionReaderSheet.tsx").read_text(encoding="utf-8")
    forbidden_terms = ("anthropic", "claude", "openai", "apiKey", "providerKey", "in-node")

    assert not any(term in source.lower() for term in forbidden_terms)
