from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Organisation(BaseModel):
    organisation_id: Optional[str] = None
    name: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    phone: str
    description: str
    email: str
    website: str
    logo_path: Optional[str] = None
    pan_number: str
    gst_number: str
    tan_number: str
    hostname: str
    employee_strength: int
    used_employee_strength: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool

class OrganisationCreate(BaseModel):
    organisation_id: Optional[str] = None   
    name: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    phone: str
    email: str
    website: str
    logo_path: Optional[str] = None
    pan_number: str
    gst_number: str
    tan_number: str
    hostname: str
    employee_strength: int
    used_employee_strength: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool
    description: str


class OrganisationUpdate(BaseModel):
    organisation_id: Optional[str] = None
    name: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    phone: str
    email: str
    website: str
    logo_path: Optional[str] = None
    pan_number: str
    gst_number: str
    tan_number: str
    hostname: str
    employee_strength: int
    used_employee_strength: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool 
    description: str

class OrganisationListResponse(BaseModel):
    organisations: List[Organisation]
    total: int
