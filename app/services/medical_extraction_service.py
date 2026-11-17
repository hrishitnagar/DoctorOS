

import re
from typing import Any

from pydantic import ValidationError

from app.schemas.medical_extraction import (
    MedicalExtractionResult,
)
from app.services.regex_extraction import (
    extract_structured_data,
)
from app.services.llm_extraction import (
    extract_medical_information,
)


# Administrative labels that must never become laboratory tests.
EXCLUDED_LAB_LABELS = {
    "patient id",
    "patient name",
    "report id",
    "report number",
    "specimen id",
    "specimen number",
    "sample id",
    "sample number",
    "accession number",
    "registration number",
    "barcode",
    "invoice number",
    "order number",
}


def is_valid_lab_candidate(lab: dict[str, Any]) -> bool:
    """
    Reject administrative identifiers incorrectly classified
    as laboratory measurements.
    """

    name = str(
        lab.get("name") or lab.get("test_name") or ""
    ).strip()

    if not name:
        return False

    normalized_name = re.sub(
        r"\s+",
        " ",
        name.lower(),
    )

    # Reject exact administrative labels.
    if normalized_name in EXCLUDED_LAB_LABELS:
        return False

    # Reject common identifier-style labels.
    identifier_patterns = [
        r"\b(?:patient|report|specimen|sample|accession|"
        r"registration|barcode|invoice|order)\s*"
        r"(?:id|no\.?|number|#)\b",
        r"^(?:syn|test)[-_](?:doctoros|spec|report)\b",
    ]

    if any(
        re.search(pattern, normalized_name, re.IGNORECASE)
        for pattern in identifier_patterns
    ):
        return False

    # A lab result must have a numeric value.
    try:
        float(lab.get("value"))
    except (TypeError, ValueError):
        return False

    return True


def merge_lab_results(
    regex_labs: list[dict[str, Any]],
    llm_labs: list[Any],
) -> list[dict[str, Any]]:
    """
    Merge regex and Gemini laboratory results.

    Gemini results take priority. Regex fills missing
    units and reference ranges.

    Administrative identifiers are excluded.
    """

    merged = []

    # Process Gemini results first.
    for lab in llm_labs:
        if hasattr(lab, "model_dump"):
            lab = lab.model_dump()

        lab = dict(lab)

        if not is_valid_lab_candidate(lab):
            continue

        merged.append(lab)

    # Merge regex results.
    for regex_lab in regex_labs:

        regex_candidate = {
            "name": regex_lab.get("test_name"),
            "value": regex_lab.get("value"),
            "unit": regex_lab.get("unit"),
            "reference_range": regex_lab.get(
                "reference_range"
            ),
            "confidence": 0.5,
            "needs_review": True,
        }

        if not is_valid_lab_candidate(regex_candidate):
            continue

        match = next(
            (
                lab for lab in merged
                if str(lab.get("name", "")).strip().lower()
                == str(regex_candidate["name"]).strip().lower()
                and lab.get("value") == regex_candidate["value"]
            ),
            None,
        )

        if match:
            if not match.get("unit"):
                match["unit"] = regex_candidate["unit"]

            if not match.get("reference_range"):
                match["reference_range"] = (
                    regex_candidate["reference_range"]
                )

            match["needs_review"] = True

        else:
            merged.append(regex_candidate)

    # Final validation before Pydantic validation.
    return [
        lab for lab in merged
        if is_valid_lab_candidate(lab)
    ]


def merge_dates(
    regex_dates: list[str],
    llm_dates: list[Any],
) -> list[dict[str, str]]:
    """Combine dates from regex and Gemini."""

    merged = []
    seen = set()

    for item in llm_dates:
        if hasattr(item, "model_dump"):
            item = item.model_dump()

        value = item["value"].strip()

        if value not in seen:
            merged.append({
                "value": value,
                "type": item["type"],
            })
            seen.add(value)

    for value in regex_dates:
        if value not in seen:
            merged.append({
                "value": value,
                "type": "unknown_date",
            })
            seen.add(value)

    return merged


def extract_and_validate_medical_data(
    medical_text: str,
) -> MedicalExtractionResult:
    """
    Run regex and Gemini extraction, merge results,
    validate the final structured output.
    """

    if not medical_text or not medical_text.strip():
        raise ValueError("Medical text cannot be empty.")

    # 1. Regex extraction.
    regex_result = extract_structured_data(
        medical_text
    )

    # 2. Gemini extraction.
    llm_result = extract_medical_information(
        medical_text
    )

    # 3. Merge and filter laboratory results.
    combined_labs = merge_lab_results(
        regex_labs=regex_result["lab_tests"],
        llm_labs=llm_result.lab_tests,
    )

    # 4. Merge dates.
    combined_dates = merge_dates(
        regex_dates=regex_result["dates"],
        llm_dates=llm_result.dates,
    )

    # 5. Prepare final structured result.
    final_data = {
        "diagnoses": [
            item.model_dump()
            for item in llm_result.diagnoses
        ],
        "medicines": [
            item.model_dump()
            for item in llm_result.medicines
        ],
        "lab_tests": combined_labs,
        "dates": combined_dates,
    }

    # 6. Validate using Pydantic.
    try:
        validated_result = (
            MedicalExtractionResult.model_validate(
                final_data
            )
        )
    except ValidationError:
        raise

    # 7. Keep all extracted medical information under review.
    for item in validated_result.diagnoses:
        item.needs_review = True

    for item in validated_result.medicines:
        item.needs_review = True

    for item in validated_result.lab_tests:
        item.needs_review = True

    return validated_result
