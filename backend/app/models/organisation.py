from pydantic import BaseModel
from datetime import datetime
class Organisation(BaseModel):
    organisation_id: str
    name: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    phone: str
    email: str
    website: str
    logo: str
    pan_number: str
    gst_number: str
    tan_number: str
    hostname: str
    employee_strength: int
    created_at: datetime
    updated_at: datetime

class OrganisationCreate(BaseModel):
    organisation_id: str
    name: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    phone: str
    email: str
    website: str
    logo: str
    pan_number: str
    gst_number: str
    tan_number: str
    hostname: str
    employee_strength: int
    created_at: datetime
    updated_at: datetime

class OrganisationUpdate(BaseModel):
    organisation_id: str
    name: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    phone: str
    email: str
    website: str
    logo: str
    pan_number: str
    gst_number: str
    tan_number: str
    hostname: str
    employee_strength: int
    created_at: datetime
    updated_at: datetime

    