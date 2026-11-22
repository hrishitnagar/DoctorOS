

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import patient_summaries
from app.api.deps import require_role
from app.api.routes.auth import router as auth_router
from app.api.routes.patients import router as patients_router
from app.api.routes.appointments import router as appointments_router
from app.api.routes import visits, documents, review, rag
from app.models.user import User
from app.api.routes import conversations


app = FastAPI(
    title="DoctorOS AI",
    description="Intelligent Clinical Records & Patient Management System",
    version="1.0.0",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "DoctorOS AI",
        "message": "Backend is running successfully",
    }


# Register API routers
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(appointments_router)
app.include_router(visits.router)
app.include_router(documents.router)
app.include_router(review.router)
app.include_router(rag.router)
app.include_router(conversations.router)
app.include_router(patient_summaries.router)


# Protected doctor dashboard
@app.get("/doctor/dashboard")
def doctor_dashboard(
    current_user: User = Depends(require_role("doctor")),
):
    return {
        "message": "Doctor access granted",
        "doctor_id": current_user.id,
        "doctor_name": current_user.name,
        "role": current_user.role,
    }
