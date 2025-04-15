from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class UserInfo(BaseModel):
    """
    Model for user information. Uses snake_case fields.
    Uses pattern for mobile number validation.
    """
    empId: str
    name: str
    email: str
    gender: str
    dob: date
    doj: date
    mobile: str = Field(..., pattern="^\\d{10}$")
    login_required: bool
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

    class Config:
        extra = "forbid"


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    
class UserOut(BaseModel):
    username: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    username: str
    role: str