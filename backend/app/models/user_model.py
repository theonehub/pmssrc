from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class UserInfo(BaseModel):
    """
    Model for user information. Uses snake_case fields.
    Uses pattern for mobile number validation.
    """
    empId: str
    name: str
    email: str
    gender: str
    dob: str
    doj: str
    mobile: str #= Field(..., pattern="^\\d{10}$")
    managerId: Optional[str] = None
    leave_balance: Optional[dict] = {}
    password: str
    role: str
    is_active: Optional[bool] = True

    @field_validator('gender')
    def validate_gender(cls, v):
        valid_genders = ['male', 'female', 'other']
        if v.lower() not in valid_genders:
            raise ValueError('Gender must be either "male" or "female" or "other"')
        return v.lower()

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "empId": "EMP001",
                "name": "John Doe",
                "email": "john@example.com",
                "gender": "male",
                "dob": "1990-01-15",
                "doj": "2020-01-15",
                "mobile": "1234567890",
                "managerId": "EMP002",
                "password": "password123",
                "role": "user",
                "is_active": True
            }
        }


class UserCreate(BaseModel):
    empId: str
    password: str
    role: str = "user"
    is_active: bool = True
    
class UserOut(BaseModel):
    empId: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    empId: str
    role: str