from pydantic import BaseModel, Field
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
    dob: datetime
    doj: datetime
    mobile: str = Field(..., pattern="^\\d{10}$")
    managerId: str
    login_required: bool
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True

    class Config:
        extra = "forbid"


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