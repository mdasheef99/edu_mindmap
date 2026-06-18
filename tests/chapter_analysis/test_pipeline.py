from pathlib import Path

import pytest

PDF_FIXTURE_PATH = Path(__file__).resolve().parents[2] / "docs" / "research" / "electricity.pdf"


def test_p0_segmentation_ids_are_deterministic() -> None:
    """SDD §9 T1: same chapter bytes must yield the same stable segment ids."""
    from app.chapter_analysis.segments import segment_chapter_text

    pages = ["Electric current flows through a circuit.\n\nWhy does the bulb glow?"]

    first = segment_chapter_text("ch_phys10_electricity", pages)
    second = segment_chapter_text("ch_phys10_electricity", pages)

    assert [segment["segment_id"] for segment in first] == [
        "ch_phys10_electricity_para_001",
        "ch_phys10_electricity_question_001",
    ]
    assert [segment["segment_id"] for segment in first] == [
        segment["segment_id"] for segment in second
    ]


def test_p0_segment_index_records_required_fields() -> None:
    """SDD §9 T2: P0 segments must record the required index fields."""
    from app.chapter_analysis.segments import segment_chapter_text

    pages = ["Electric current flows through a circuit.\n\nWhy does the bulb glow?"]
    segments = segment_chapter_text("ch_phys10_electricity", pages)

    para_segment = segments[0]
    question_segment = segments[1]

    assert set(para_segment) >= {"segment_id", "segment_type", "text", "page", "char_span"}
    assert para_segment["segment_type"] == "para"
    assert para_segment["page"] == 1
    assert para_segment["char_span"] == (0, len("Electric current flows through a circuit."))

    assert set(question_segment) >= {
        "segment_id",
        "segment_type",
        "text",
        "page",
        "char_span",
        "location",
    }
    assert question_segment["segment_type"] == "question"
    assert question_segment["location"] == "in_text"


def test_p0_pdf_page_extraction_is_deterministic_for_curriculum_inputs() -> None:
    """SDD §8 L1/L2: same PDF bytes must yield the same page-text inputs."""
    from app.chapter_analysis.segments import extract_pdf_pages

    pdf_bytes = PDF_FIXTURE_PATH.read_bytes()

    first = extract_pdf_pages(pdf_bytes)
    second = extract_pdf_pages(pdf_bytes)

    assert first == second
    assert first
    assert all(isinstance(page, str) for page in first)
    assert any(page.strip() for page in first)


def test_p0_pdf_segmentation_ids_are_deterministic() -> None:
    """SDD §8 L1 / §9 T1: same PDF bytes must yield the same stable segment ids."""
    from app.chapter_analysis.segments import segment_chapter_pdf_bytes

    pdf_bytes = PDF_FIXTURE_PATH.read_bytes()

    first = segment_chapter_pdf_bytes("ch_phys10_electricity", pdf_bytes)
    second = segment_chapter_pdf_bytes("ch_phys10_electricity", pdf_bytes)

    assert first
    assert [segment["segment_id"] for segment in first] == [
        segment["segment_id"] for segment in second
    ]
    assert all(str(segment["segment_id"]).startswith("ch_phys10_electricity_") for segment in first)


def test_p0_pdf_segment_index_records_required_fields() -> None:
    """SDD §8 L1 / §9 T2: PDF-backed P0 segments must record the required index fields."""
    from app.chapter_analysis.segments import segment_chapter_pdf_bytes

    segments = segment_chapter_pdf_bytes(
        "ch_phys10_electricity",
        PDF_FIXTURE_PATH.read_bytes(),
    )

    assert segments
    first_segment = segments[0]

    assert set(first_segment) >= {"segment_id", "segment_type", "text", "page", "char_span"}
    assert isinstance(first_segment["page"], int)
    assert isinstance(first_segment["char_span"], tuple)
    assert len(first_segment["char_span"]) == 2
    assert all(isinstance(value, int) for value in first_segment["char_span"])

    for segment in segments:
        assert segment["text"]
        assert isinstance(segment["char_span"], tuple)
        assert len(segment["char_span"]) == 2
        start, end = segment["char_span"]
        assert isinstance(start, int)
        assert isinstance(end, int)
        assert start <= end
        if segment["segment_type"] == "question":
            assert segment["location"] in {"in_text", "end_of_chapter"}


def test_p3_merge_keeps_named_label_and_unions_passage_refs() -> None:
    """SDD §9 T3: merge must keep the P1 label and union citations when labels normalize."""
    from app.chapter_analysis.merge import merge_concept_records

    named = {
        "concept_id": "electric_current",
        "label": "Electric current",
        "definition": "Rate of flow of charge in the chapter's wording.",
        "category_tag": "quantity",
        "extraction_pass": "P1",
        "passage_refs": {
            "definitional": ["ch_phys10_electricity_para_001"],
            "explanatory": ["ch_phys10_electricity_para_002"],
            "application": [],
        },
    }
    embedded = {
        "concept_id": "electric_currents",
        "label": "electric currents",
        "definition": "Movement of charge through a conducting path.",
        "category_tag": "quantity",
        "extraction_pass": "P2",
        "passage_refs": {
            "definitional": [],
            "explanatory": ["ch_phys10_electricity_para_003"],
            "application": ["ch_phys10_electricity_question_001"],
        },
    }

    merged = merge_concept_records([named], [embedded])

    assert len(merged) == 1
    assert merged[0]["concept_id"] == "electric_current"
    assert merged[0]["label"] == "Electric current"
    assert merged[0]["merged_from"] == ["electric_currents"]
    assert merged[0]["passage_refs"] == {
        "definitional": ["ch_phys10_electricity_para_001"],
        "explanatory": [
            "ch_phys10_electricity_para_002",
            "ch_phys10_electricity_para_003",
        ],
        "application": ["ch_phys10_electricity_question_001"],
    }


def test_p3_label_normalization_does_not_strip_non_plural_trailing_s_words() -> None:
    """SDD §9 T3: normalization must not turn s-ending labels into false matches."""
    from app.chapter_analysis.merge import merge_concept_records

    named = {
        "concept_id": "process",
        "label": "Process",
        "passage_refs": {"definitional": ["ch_para_001"], "explanatory": [], "application": []},
    }
    embedded = {
        "concept_id": "proce",
        "label": "Proce",
        "passage_refs": {"definitional": [], "explanatory": ["ch_para_002"], "application": []},
    }

    merged = merge_concept_records([named], [embedded])

    assert [concept["concept_id"] for concept in merged] == ["process", "proce"]


def test_p4_edge_ids_are_deterministic_and_typed() -> None:
    """SDD §9 T4: P4 edge ids must be deterministic and respect directional rules."""
    from app.chapter_analysis.edges import assign_edge_ids

    raw_edges = [
        {
            "from_concept": "resistance",
            "to_concept": "current",
            "type": "CONNECTS",
            "passage_support": ["ch_phys10_electricity_para_003"],
        },
        {
            "from_concept": "charge",
            "to_concept": "current",
            "type": "PREREQUISITE_OF",
            "passage_support": ["ch_phys10_electricity_para_001"],
        },
    ]

    first = assign_edge_ids(raw_edges)
    second = assign_edge_ids(raw_edges)

    assert first == second
    assert first[0]["edge_id"] == "edge_connects_current_resistance"
    assert first[0]["type"] == "CONNECTS"
    assert first[1]["edge_id"] == "edge_prerequisite_of_charge_current"
    assert first[1]["type"] == "PREREQUISITE_OF"


def test_verification_gate_rejects_uncited_segment_refs() -> None:
    """SDD §9 T5: verification must reject citations not present in the P0 index."""
    from app.chapter_analysis.segments import segment_chapter_text
    from app.chapter_analysis.verification import verify_cited_segment_ids

    segments = segment_chapter_text(
        "ch_phys10_electricity",
        ["Electric current flows through a circuit.\n\nWhy does the bulb glow?"],
    )

    with pytest.raises(ValueError, match="ch_phys10_electricity_para_999"):
        verify_cited_segment_ids(
            ["ch_phys10_electricity_para_001", "ch_phys10_electricity_para_999"],
            segments,
        )
