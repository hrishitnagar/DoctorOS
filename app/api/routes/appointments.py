
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
)
from app.schemas.appointment import AppointmentStatusUpdate
from app.models.appointment import Appointment
from app.services.appointment_service import create_appointment
from app.core.audit import record_audit_event
from app.api.deps import require_role


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        appointment = create_appointment(
            db=db,
            appointment_data=appointment_data,
            doctor_id=current_user.id,
        )

        record_audit_event(
            db=db,
            user_id=current_user.id,
            patient_id=appointment.patient_id,
            action="CREATE",
            resource_type="appointment",
            resource_id=str(appointment.id),
            details={
                "appointment_datetime": (
                    appointment.appointment_datetime.isoformat()
                ),
                "duration_minutes": appointment.duration_minutes,
                "status": appointment.status,
            },
        )

        return appointment

    except ValueError as exc:
        message = str(exc)

        if message == "Patient not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )
@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: int,
    status_data: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.doctor_id == current_user.id,
        )
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found",
        )

    # Only scheduled appointments can be updated
    if appointment.status != "scheduled":
        raise HTTPException(
            status_code=400,
            detail="Only scheduled appointments can be updated",
        )

    old_status = appointment.status
    new_status = status_data.status

    appointment.status = new_status

    try:
        db.commit()
        db.refresh(appointment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update appointment status",
        )

    # Record the status change in the audit log
    record_audit_event(
        db=db,
        user_id=current_user.id,
        patient_id=appointment.patient_id,
        action="UPDATE",
        resource_type="appointment",
        resource_id=str(appointment.id),
        details={
            "old_status": old_status,
            "new_status": new_status,
        },
    )

    return appointment