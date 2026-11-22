
from types import SimpleNamespace

import pytest

from app.services import rag_generation_service


def test_generate_rag_answer_success(monkeypatch):

    expected_answer = (
        "The recorded haemoglobin level is "
        "12.5 g/dL [S1]."
    )

    def mock_generate_content(**kwargs):
        assert kwargs["model"] == (
            rag_generation_service.settings.GEMINI_MODEL
        )

        assert "haemoglobin" in kwargs["contents"].lower()
        assert "12.5 g/dL" in kwargs["contents"]

        return SimpleNamespace(text=expected_answer)

    monkeypatch.setattr(
        rag_generation_service.client.models,
        "generate_content",
        mock_generate_content,
    )

    answer = rag_generation_service.generate_rag_answer(
        question="What is the haemoglobin level?",
        context="[S1]\nHaemoglobin: 12.5 g/dL",
    )

    assert answer == expected_answer


def test_generate_rag_answer_rejects_empty_question():

    with pytest.raises(ValueError, match="Question cannot be empty"):
        rag_generation_service.generate_rag_answer(
            question="",
            context="Some medical context",
        )


def test_generate_rag_answer_handles_empty_context():

    answer = rag_generation_service.generate_rag_answer(
        question="What is the haemoglobin level?",
        context="",
    )

    assert "could not find relevant information" in answer.lower()


def test_generate_rag_answer_rejects_non_string_context():

    with pytest.raises(ValueError, match="Context must be a string"):
        rag_generation_service.generate_rag_answer(
            question="What is the haemoglobin level?",
            context=None,
        )


def test_generate_rag_answer_handles_empty_gemini_response(
    monkeypatch,
):

    def mock_generate_content(**kwargs):
        return SimpleNamespace(text=None)

    monkeypatch.setattr(
        rag_generation_service.client.models,
        "generate_content",
        mock_generate_content,
    )

    with pytest.raises(ValueError, match="Gemini returned an empty response"):
        rag_generation_service.generate_rag_answer(
            question="What is the haemoglobin level?",
            context="[S1]\nHaemoglobin: 12.5 g/dL",
        )
