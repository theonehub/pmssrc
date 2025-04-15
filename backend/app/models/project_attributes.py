from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class ProjectAttributeBase(BaseModel):
    key: str = Field(..., description="Unique attribute key")
    value: str
    default_value: str
    description: Optional[str] = None

class ProjectAttributeCreate(ProjectAttributeBase):
    pass

class ProjectAttributeUpdate(BaseModel):
    value: Optional[str]
    default_value: Optional[str]
    description: Optional[str]

class ProjectAttributeInDB(ProjectAttributeBase):
    id: str
    created_at: datetime


class AttributeOut(BaseModel):
    key: str
    value: str
    default_value: str
    description: Optional[str]
    id: Optional[str] = Field(alias="_id")  # maps MongoDB _id to id in response

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }