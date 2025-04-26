from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class UserInfo(BaseModel):
    """
    Model for user information. Uses snake_case fields.
    Uses pattern for mobile number validation.
    """
    emp_id: str
    name: str
    email: str
    gender: str
    dob: str
    doj: str
    mobile: str #= Field(..., pattern="^\\d{10}$")
    manager_id: Optional[str] = None
    leave_balance: Optional[dict] = {}
    password: str
    role: str
    is_active: Optional[bool] = True
    pan_number: Optional[str] = None
    uan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    location: Optional[str] = None
    esi_number: Optional[str] = None
    pan_file_path: Optional[str] = None
    aadhar_file_path: Optional[str] = None
    photo_path: Optional[str] = None

    @field_validator('gender')
    def validate_gender(cls, v):
        valid_genders = ['male', 'female', 'other']
        if v.lower() not in valid_genders:
            raise ValueError('Gender must be either "male" or "female" or "other"')
        return v.lower()

    @field_validator('pan_number')
    def validate_pan(cls, v):
        if v is not None and not v.strip():
            return None
        if v is not None and (len(v) != 10 or not v.isalnum()):
            raise ValueError('PAN number must be 10 alphanumeric characters')
        return v.upper() if v else None

    @field_validator('aadhar_number')
    def validate_aadhar(cls, v):
        if v is not None and not v.strip():
            return None
        if v is not None and (len(v) != 12 or not v.isdigit()):
            raise ValueError('Aadhar number must be 12 digits')
        return v

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "emp_id": "EMP001",
                "name": "John Doe",
                "email": "john@example.com",
                "gender": "male",
                "dob": "1990-01-15",
                "doj": "2020-01-15",
                "mobile": "1234567890",
                "manager_id": "EMP002",
                "password": "password123",
                "role": "user",
                "is_active": True,
                "pan_number": "ABCDE1234F",
                "uan_number": "123456789012",
                "aadhar_number": "123456789012",
                "department": "IT",
                "designation": "Software Engineer",
                "location": "Bangalore",
                "esi_number": "31001234560000001",
                "pan_file_path": None,
                "aadhar_file_path": None,
                "photo_path": None
            }
        }


class UserCreate(BaseModel):
    emp_id: str
    password: str
    role: str = "user"
    is_active: bool = True
    
class UserOut(BaseModel):
    emp_id: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    emp_id: str
    role: str