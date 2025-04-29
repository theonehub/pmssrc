from fastapi import APIRouter, Depends, HTTPException
from auth.auth import extract_emp_id, extract_hostname, extract_role, role_checker
from models.user_model import User
from models.project_attributes import *
from services import project_attributes_service as attribute_service

router = APIRouter(prefix="/attributes", tags=["Project Attributes"])

@router.post("/", summary="Create project attribute")
def create_attr(data: ProjectAttributeCreate, 
                hostname: str = Depends(extract_hostname),
                role: str = Depends(role_checker(["superadmin"]))):
    return attribute_service.create_attribute(data, hostname)

@router.put("/{key}", summary="Update attribute")
def update_attr(key: str, data: ProjectAttributeUpdate, 
                hostname: str = Depends(extract_hostname),
                role: str = Depends(role_checker(["superadmin"]))):
    if not attribute_service.update_attribute(key, data, hostname):
        raise HTTPException(status_code=404, detail="Attribute not found")
    return {"success": True}

@router.get("/", summary="List all attributes")
def list_attrs(hostname: str = Depends(extract_hostname),
                role: str = Depends(role_checker(["superadmin"]))):
    return attribute_service.get_all_attributes(hostname)

@router.get("/{key}", summary="Get attribute by key")
def get_attr(key: str, hostname: str = Depends(extract_hostname),
                role: str = Depends(role_checker(["superadmin"]))):
    attr = attribute_service.get_attribute_by_key(key, hostname)
    if not attr:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attr

@router.delete("/{key}", summary="Delete attribute")
def delete_attr(key: str, hostname: str = Depends(extract_hostname),
                role: str = Depends(role_checker(["superadmin"]))):
    if not attribute_service.delete_attribute(key, hostname):
        raise HTTPException(status_code=404, detail="Attribute not found")
    return {"success": True}
