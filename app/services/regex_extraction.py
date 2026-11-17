
import re
from typing import Any


# Common date formats: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
DATE_PATTERN = re.compile(
    r"\b(?:"
    r"\d{1,2}[/-]\d{1,2}[/-]\d{4}"
    r"|"
    r"\d{4}-\d{2}-\d{2}"
    r")\b"
)

# Examples:
# Hemoglobin: 11.2 g/dL
# WBC: 7500 cells/mcL
# Glucose: 105 mg/dL
LAB_PATTERN = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9 ()/.-]{1,60}?)"
    r"\s*[:\-]\s*"
    r"([<>]?\s*\d+(?:\.\d+)?)"
    r"\s*"
    r"([A-Za-zµμ/%0-9^]+(?:/[A-Za-zµμ0-9^]+)?)?"
    r"\s*$",
    re.MULTILINE,
)

REFERENCE_PATTERN = re.compile(
    r"^\s*(?:Reference Range|Ref(?:erence)?\.? Range)"
    r"\s*[:\-]\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def extract_dates(text: str) -> list[str]:
    """Extract date strings from OCR text."""
    return list(dict.fromkeys(DATE_PATTERN.findall(text)))



def extract_lab_values(text: str) -> list[dict[str, Any]]:
    """Extract lab values while excluding dates and other metadata."""

    lines = text.splitlines()
    lab_results = []

    excluded_labels = {
    "report date",
    "test date",
    "date",
    "dob",
    "date of birth",
    "reference range",
    "dose",
    "dosage",
    "frequency",
    "medicine",
    "medication",
    "prescription",
    "patient name",
    "patient id",
    "age",
    "gender",
}

    for index, line in enumerate(lines):
        match = LAB_PATTERN.match(line)

        if not match:
            continue

        test_name = match.group(1).strip()

        # Ignore metadata fields.
        if test_name.lower() in excluded_labels:
            continue

        # Ignore lines that contain date-like values.
        value_text = match.group(2).strip()

        if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{4}", line):
            continue

        # Ignore values that have no meaningful numeric measurement.
        try:
            value = float(value_text.lstrip("<>").strip())
        except ValueError:
            continue

        unit = match.group(3)

        reference_range = None

        for next_line in lines[index + 1:index + 4]:
            range_match = REFERENCE_PATTERN.match(next_line)

            if range_match:
                reference_range = range_match.group(1).strip()
                break

        lab_results.append({
            "test_name": test_name,
            "value": value,
            "unit": unit.strip() if unit else None,
            "reference_range": reference_range,
            "needs_review": True,
        })

    return lab_results



def extract_structured_data(text: str) -> dict[str, Any]:
    """Extract dates and basic lab values from medical text."""

    return {
        "dates": extract_dates(text),
        "lab_tests": extract_lab_values(text),
    }
