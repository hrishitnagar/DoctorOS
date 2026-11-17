
from app.services.llm_extraction import (
    extract_medical_information,
)


sample_report = """
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


result = extract_medical_information(sample_report)

print("\nGEMINI EXTRACTION RESULT\n")

print(result.model_dump_json(indent=4))
