
from getpass import getpass

from app.database.connection import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_doctor():
    db = SessionLocal()

    try:
        name = input("Enter doctor name: ").strip()
        email = input("Enter doctor email: ").strip().lower()
        password = getpass("Enter doctor password: ")

        if not name or not email or not password:
            print("All fields are required.")
            return

        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            print("An account with this email already exists.")
            return

        doctor = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="doctor",
            is_active=True
        )

        db.add(doctor)
        db.commit()
        db.refresh(doctor)

        print("\nDoctor account created successfully!")
        print("Doctor ID:", doctor.id)
        print("Email:", doctor.email)
        print("Role:", doctor.role)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_doctor()
