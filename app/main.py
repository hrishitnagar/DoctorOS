from fastapi import FastAPI

app = FastAPI(
    title="DoctorOS AI",
    description="Intelligent Clinical Records & Patient Management System",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "DoctorOS AI",
        "message": "Backend is running successfully"
    }