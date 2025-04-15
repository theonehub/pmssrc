from fastapi import APIRouter, Depends, HTTPException
from auth.auth import get_current_user
from models.user_model import User
from models.project_attributes import *
from services import project_attributes_service as attribute_service

router = APIRouter(prefix="/attributes", tags=["Project Attributes"])

@router.post("/", summary="Create project attribute")
def create_attr(data: ProjectAttributeCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    return attribute_service.create_attribute(data)

@router.put("/{key}", summary="Update attribute")
def update_attr(key: str, data: ProjectAttributeUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    if not attribute_service.update_attribute(key, data):
        raise HTTPException(status_code=404, detail="Attribute not found")
    return {"success": True}

@router.get("/", summary="List all attributes")
def list_attrs(current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    return attribute_service.get_all_attributes()

@router.get("/{key}", summary="Get attribute by key")
def get_attr(key: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    attr = attribute_service.get_attribute_by_key(key)
    if not attr:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attr

@router.delete("/{key}", summary="Delete attribute")
def delete_attr(key: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Access denied")
    if not attribute_service.delete_attribute(key):
        raise HTTPException(status_code=404, detail="Attribute not found")
    return {"success": True}
