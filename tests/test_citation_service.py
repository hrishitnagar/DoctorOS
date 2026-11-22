
import pytest

from app.services.citation_service import (
    validate_citations,
    CitationValidationError,
    MissingCitationError,
)


@pytest.fixture
def sample_sources():
    return [
        {
            "source_id": "S1",
            "chunk_id": 101,
            "document_id": 10,
            "patient_id": 5,
            "chunk_index": 0,
            "page_no": 2,
            "document_date": "2026-10-15",
        },
        {
            "source_id": "S2",
            "chunk_id": 102,
            "document_id": 10,
            "patient_id": 5,
            "chunk_index": 1,
            "page_no": 3,
            "document_date": "2026-10-15",
        },
    ]


def test_validate_valid_citations(sample_sources):

    answer = (
        "Haemoglobin is 12.5 g/dL [S1]. "
        "WBC count is 7500 cells/mcL [S2]."
    )

    result = validate_citations(answer, sample_sources)

    assert len(result) == 2
    assert result[0]["source_id"] == "S1"
    assert result[1]["source_id"] == "S2"


def test_validate_repeated_citations_only_once(sample_sources):

    answer = "The result is 12.5 g/dL [S1]. "
    answer += "The same result appears in [S1]."

    result = validate_citations(answer, sample_sources)

    assert len(result) == 1
    assert result[0]["source_id"] == "S1"


def test_validate_unknown_citation(sample_sources):

    answer = "The result is 12.5 g/dL [S9]."

    with pytest.raises(
        CitationValidationError,
        match="unknown citations",
    ):
        validate_citations(answer, sample_sources)


def test_validate_missing_citations(sample_sources):

    answer = "The recorded haemoglobin is 12.5 g/dL."

    with pytest.raises(MissingCitationError):
        validate_citations(answer, sample_sources)


def test_allow_missing_citations_when_not_required(sample_sources):

    answer = "No relevant information was found."

    result = validate_citations(
        answer,
        sample_sources,
        require_citations=False,
    )

    assert result == []


def test_reject_empty_answer(sample_sources):

    with pytest.raises(ValueError, match="non-empty string"):
        validate_citations("", sample_sources)


def test_reject_invalid_sources():

    with pytest.raises(ValueError, match="Sources must be a list"):
        validate_citations("Answer [S1]", None)


def test_reject_duplicate_source_ids(sample_sources):

    duplicate_sources = sample_sources + [
        {
            **sample_sources[0],
            "chunk_id": 999,
        }
    ]

    with pytest.raises(ValueError, match="Duplicate source ID"):
        validate_citations("Answer [S1]", duplicate_sources)


def test_reject_invalid_source_id():

    sources = [
        {
            "source_id": "INVALID",
            "document_id": 10,
        }
    ]

    with pytest.raises(ValueError, match="Invalid source ID"):
        validate_citations("Answer [INVALID]", sources)


def test_preserve_citation_order(sample_sources):

    answer = "WBC is recorded [S2]. Haemoglobin is recorded [S1]."

    result = validate_citations(answer, sample_sources)

    assert [source["source_id"] for source in result] == [
        "S2",
        "S1",
    ]
