

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.schemas.medical_extraction import (
    MedicalExtractionResult,
    DiagnosisExtraction,
    MedicineExtraction,
    LabTestExtraction,
    DateExtraction,
)

from app.services.llm_extraction import (
    extract_medical_information,
)


def test_extract_medical_information_success():
    """Test extraction using a mocked Gemini response."""

    mock_result = MedicalExtractionResult(
        diagnoses=[
            DiagnosisExtraction(
                name="Iron Deficiency Anemia",
                confidence=0.95,
                needs_review=False,
            )
        ],
        medicines=[
            MedicineExtraction(
                name="Ferrous Sulphate",
                dose="325 mg",
                frequency="Once daily",
                confidence=0.92,
                needs_review=False,
            )
        ],
        lab_tests=[
            LabTestExtraction(
                name="Hemoglobin",
                value=11.2,
                unit="g/dL",
                reference_range="13.0 - 17.0 g/dL",
                confidence=0.98,
                needs_review=False,
            )
        ],
        dates=[
            DateExtraction(
                value="12/11/2026",
                type="report_date",
            )
        ],
    )

    mock_response = SimpleNamespace(
        parsed=mock_result,
        text=None,
    )

    with patch.object(
        __import__(
            "app.services.llm_extraction",
            fromlist=["client"],
        ).client.models,
        "generate_content",
        return_value=mock_response,
    ) as mock_generate:

        result = extract_medical_information(
            "Synthetic laboratory report for testing."
        )

    assert isinstance(result, MedicalExtractionResult)

    assert len(result.diagnoses) == 1
    assert result.diagnoses[0].name == "Iron Deficiency Anemia"

    assert len(result.medicines) == 1
    assert result.medicines[0].name == "Ferrous Sulphate"

    assert len(result.lab_tests) == 1
    assert result.lab_tests[0].name == "Hemoglobin"
    assert result.lab_tests[0].value == 11.2

    assert len(result.dates) == 1
    assert result.dates[0].type == "report_date"

    # All extracted medical items must require human review.
    assert all(item.needs_review for item in result.diagnoses)
    assert all(item.needs_review for item in result.medicines)
    assert all(item.needs_review for item in result.lab_tests)

    mock_generate.assert_called_once()


def test_extract_medical_information_rejects_empty_text():
    """Empty input must be rejected before calling Gemini."""

    with patch(
        "app.services.llm_extraction.client.models.generate_content"
    ) as mock_generate:

        with pytest.raises(ValueError, match="Medical text cannot be empty"):
            extract_medical_information("   ")

        mock_generate.assert_not_called()
