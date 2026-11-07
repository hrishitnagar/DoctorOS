
from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.patient import PatientCreate, PatientUpdate


def valid_patient_data():
    return {
        "name": "Aarav Sharma",
        "dob": "1998-05-15",
        "gender": "Male",
        "phone": "9876543210",
        "email": "aarav.test@example.com",
        "address": "Indore, Madhya Pradesh",
        "blood_group": "O+",
        "emergency_contact": "9876543211",
    }


def test_valid_patient_data():
    patient = PatientCreate(**valid_patient_data())

    assert patient.name == "Aarav Sharma"
    assert patient.phone == "9876543210"
    assert patient.dob == date(1998, 5, 15)


def test_name_cannot_be_empty():
    data = valid_patient_data()
    data["name"] = "   "

    with pytest.raises(ValidationError):
        PatientCreate(**data)


def test_future_dob_is_rejected():
    data = valid_patient_data()
    data["dob"] = (date.today() + timedelta(days=1)).isoformat()

    with pytest.raises(ValidationError):
        PatientCreate(**data)


@pytest.mark.parametrize(
    "phone",
    [
        "12345",
        "abcdefghij",
        "98765@3210",
        "12345678901234567890",
    ],
)
def test_invalid_phone_numbers_are_rejected(phone):
    data = valid_patient_data()
    data["phone"] = phone

    with pytest.raises(ValidationError):
        PatientCreate(**data)


@pytest.mark.parametrize(
    "phone",
    [
        "9876543210",
        "+91 9876543210",
        "987-654-3210",
        "(987) 654-3210",
    ],
)
def test_valid_phone_numbers_are_accepted(phone):
    data = valid_patient_data()
    data["phone"] = phone

    patient = PatientCreate(**data)

    assert patient.phone == phone


def test_invalid_email_is_rejected():
    data = valid_patient_data()
    data["email"] = "not-an-email"

    with pytest.raises(ValidationError):
        PatientCreate(**data)


def test_patient_update_allows_partial_data():
    patient = PatientUpdate(name="Aarav Sharma Updated")

    assert patient.name == "Aarav Sharma Updated"
    assert patient.phone is None
