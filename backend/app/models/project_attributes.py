from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from pydantic import ConfigDict


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

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            ObjectId: str
        }
    )