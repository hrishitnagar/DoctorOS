
import pytest

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.connection import engine
from app.models.user import User
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.api.deps import get_authorized_patient


@pytest.fixture
def db():
    """
    Use an isolated database transaction.
    All test changes are rolled back afterward.
    """

    connection = engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def doctor_and_patient(db):
    """Create temporary doctor and patient records."""

    doctor = User(
        name="Synthetic Test Doctor",
        email="test_doctor_auth@example.com",
        password_hash="temporary_test_hash",
        role="doctor",
        is_active=True,
    )

    patient = Patient(
        patient_uid="DOS-AUTH-TEST-001",
        name="Synthetic Test Patient",
    )

    db.add_all([doctor, patient])
    db.flush()

    return doctor, patient


def create_appointment(db, doctor, patient, appointment_status):
    """Create a temporary appointment for testing."""

    from datetime import datetime, timezone

    appointment = Appointment(
        doctor_id=doctor.id,
        patient_id=patient.id,
        appointment_datetime=datetime.now(timezone.utc),
        duration_minutes=30,
        status=appointment_status,
    )

    db.add(appointment)
    db.flush()

    return appointment


@pytest.mark.parametrize(
    "appointment_status",
    ["scheduled", "completed"],
)
def test_authorized_appointment_allows_access(
    db,
    doctor_and_patient,
    appointment_status,
):
    doctor, patient = doctor_and_patient

    create_appointment(
        db, doctor, patient, appointment_status
    )

    result = get_authorized_patient(
        patient_id=patient.id,
        db=db,
        current_user=doctor,
    )

    assert result.id == patient.id


@pytest.mark.parametrize(
    "appointment_status",
    ["cancelled", "no-show"],
)
def test_ineligible_appointment_denies_access(
    db,
    doctor_and_patient,
    appointment_status,
):
    doctor, patient = doctor_and_patient

    create_appointment(
        db, doctor, patient, appointment_status
    )

    with pytest.raises(HTTPException) as exc:
        get_authorized_patient(
            patient_id=patient.id,
            db=db,
            current_user=doctor,
        )

    assert exc.value.status_code == 403


def test_another_doctor_cannot_access_patient(
    db,
    doctor_and_patient,
):
    doctor, patient = doctor_and_patient

    another_doctor = User(
        name="Another Synthetic Doctor",
        email="another_test_doctor@example.com",
        password_hash="temporary_test_hash",
        role="doctor",
        is_active=True,
    )

    db.add(another_doctor)
    db.flush()

    create_appointment(
        db, another_doctor, patient, "scheduled"
    )

    with pytest.raises(HTTPException) as exc:
        get_authorized_patient(
            patient_id=patient.id,
            db=db,
            current_user=doctor,
        )

    assert exc.value.status_code == 403


def test_nonexistent_patient_returns_404(
    db,
    doctor_and_patient,
):
    doctor, _ = doctor_and_patient

    with pytest.raises(HTTPException) as exc:
        get_authorized_patient(
            patient_id=-1,
            db=db,
            current_user=doctor,
        )

    assert exc.value.status_code == 404
