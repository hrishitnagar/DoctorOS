
from types import SimpleNamespace

import pytest

from app.schemas.medical_extraction import (
    DiagnosisExtraction,
    MedicineExtraction,
)

from app.services.medical_extraction_service import (
    extract_and_validate_medical_data,
)


@pytest.fixture
def sample_report():
    return """
    Patient Name: Rahul Sharma
    Report Date: 12/11/2026

    Diagnosis: Iron Deficiency Anemia

    Prescription:
    Medicine: Ferrous Sulphate
    Dose: 325 mg
    Frequency: Once daily

    Laboratory Results:

    Hemoglobin: 11.2 g/dL
    Reference Range: 13.0 - 17.0 g/dL

    WBC: 7500 cells/mcL
    Reference Range: 4000 - 11000 cells/mcL
    """


def test_medical_extraction_without_gemini(
    sample_report,
    monkeypatch,
):
    # Mock Gemini extraction result.
    mock_llm_result = SimpleNamespace(
        diagnoses=[
            DiagnosisExtraction(
                name="Iron Deficiency Anemia",
                confidence=0.95,
                needs_review=True,
            )
        ],
        medicines=[
             MedicineExtraction(
                name="Ferrous Sulphate",
                dose="325 mg",
                frequency="Once daily",
                confidence=0.95,
                needs_review=True,
            )
        ],
        lab_tests=[
            {
                "name": "Hemoglobin",
                "value": 11.2,
                "unit": "g/dL",
                "reference_range": "13.0 - 17.0 g/dL",
                "confidence": 0.95,
                "needs_review": True,
            }
        ],
        dates=[
            {
                "value": "12/11/2026",
                "type": "report_date",
            }
        ],
    )

    # Replace the real Gemini function with our mock.
    monkeypatch.setattr(
        "app.services.medical_extraction_service.extract_medical_information",
        lambda text: mock_llm_result,
    )

    # Execute medical extraction and validation.
    result = extract_and_validate_medical_data(sample_report)

    print("\nCOMBINED VALIDATED MEDICAL DATA\n")
    print(result.model_dump_json(indent=4))

    # Basic validation checks.
    assert result is not None
    assert len(result.diagnoses) > 0
    assert len(result.medicines) > 0
    assert len(result.lab_tests) > 0

    # Every extracted medical record must require human review.
    for diagnosis in result.diagnoses:
        assert diagnosis.needs_review is True

    for medicine in result.medicines:
        assert medicine.needs_review is True

    for lab_test in result.lab_tests:
        assert lab_test.needs_review is True

    print("\nVALIDATION SUCCESSFUL")

