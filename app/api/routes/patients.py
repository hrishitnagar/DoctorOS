from fastapi import status
from app.services.patient_timeline_service import get_patient_timeline
from app.schemas.patient import PatientCreate, PatientResponse
from app.services.patient_service import get_patients
from app.services.patient_service import create_patient
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import require_role
from app.core.audit import record_audit_event
from app.database.connection import get_db
from app.models.patient import Patient
from app.models.user import User

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)
@router.get("/", response_model=dict, status_code=200)
def list_patients(
    search: str | None = Query(default=None, min_length=1),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    patients, total = get_patients(
        db=db,
        search=search,
        skip=skip,
        limit=limit,
    )

    record_audit_event(
        db=db,
        user_id=current_user.id,
        action="READ",
        resource_type="patient",
        details={
            "search": search,
            "skip": skip,
            "limit": limit,
            "total": total,
        },
    )

    return {
        "items": [
            PatientResponse.model_validate(patient).model_dump()
            for patient in patients
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    patient = create_patient(
        db=db,
        patient_data=patient_data,
    )

    # Record the patient creation in the audit log.
    record_audit_event(
        db=db,
        user_id=current_user.id,
        patient_id=patient.id,
        action="CREATE",
        resource_type="patient",
        resource_id=str(patient.id),
    )

    return patient



@router.get("/{patient_id}")
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    # Record that the authenticated doctor accessed this patient.
    record_audit_event(
        db=db,
        user_id=current_user.id,
        patient_id=patient.id,
        action="READ",
        resource_type="patient",
        resource_id=str(patient.id),
    )

    return {
        "id": patient.id,
        "patient_uid": patient.patient_uid,
        "name": patient.name,
        "dob": patient.dob,
        "gender": patient.gender,
        "phone": patient.phone,
        "email": patient.email,
        "address": patient.address,
        "blood_group": patient.blood_group,
        "emergency_contact": patient.emergency_contact,
    }

@router.get("/{patient_id}/timeline", response_model=dict)
def get_patient_timeline_route(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("doctor")),
):
    try:
        timeline_data = get_patient_timeline(
            db=db,
            patient_id=patient_id,
        )

        # Record timeline access in the audit log
        record_audit_event(
            db=db,
            user_id=current_user.id,
            patient_id=patient_id,
            action="READ",
            resource_type="patient_timeline",
            resource_id=str(patient_id),
            details={
                "total_records": timeline_data["total_records"],
            },
        )

        return timeline_data

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
