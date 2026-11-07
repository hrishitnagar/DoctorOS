
from datetime import date
from pydantic import EmailStr
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    dob: date | None = None
    gender: str | None = Field(default=None, max_length=30)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=255)
    address: str | None = None
    blood_group: str | None = Field(default=None, max_length=10)
    emergency_contact: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Patient name cannot be empty")

        return value

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            return None

        allowed_characters = set("0123456789+-() ")

        if not all(character in allowed_characters for character in value):
            raise ValueError("Phone number contains invalid characters")

        digits = "".join(character for character in value if character.isdigit())

        if not 7 <= len(digits) <= 15:
            raise ValueError("Phone number must contain 7 to 15 digits")

        return value


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    dob: date | None = None
    gender: str | None = Field(default=None, max_length=30)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = Field(default=None, max_length=255)
    address: str | None = None
    blood_group: str | None = Field(default=None, max_length=10)
    emergency_contact: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Patient name cannot be empty")

        return value

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            return None

        allowed_characters = set("0123456789+-() ")

        if not all(character in allowed_characters for character in value):
            raise ValueError("Phone number contains invalid characters")

        digits = "".join(character for character in value if character.isdigit())

        if not 7 <= len(digits) <= 15:
            raise ValueError("Phone number must contain 7 to 15 digits")

        return value


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_uid: str
    name: str
    dob: date | None
    gender: str | None
    phone: str | None
    email: str | None
    address: str | None
    blood_group: str | None
    emergency_contact: str | None
