"""
Salary Component Assignment DTOs
Data Transfer Objects for salary component assignment operations
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.domain.entities.salary_component_assignment import AssignmentStatus


# ==================== REQUEST DTOs ====================

class AssignComponentsRequestDTO(BaseModel):
    """Request DTO for assigning components to organization"""
    organization_id: str = Field(..., min_length=1, max_length=50, description="Organization ID")
    component_ids: List[str] = Field(..., min_items=1, description="List of component IDs to assign")
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    notes: Optional[str] = Field(None, max_length=500, description="Assignment notes")
    effective_from: Optional[datetime] = Field(None, description="Effective from date")
    effective_to: Optional[datetime] = Field(None, description="Effective to date")
    organization_specific_config: Optional[Dict[str, Any]] = Field(None, description="Organization-specific configuration")
    
    @validator('effective_to')
    def validate_effective_dates(cls, v, values):
        if v and 'effective_from' in values and values['effective_from'] and v <= values['effective_from']:
            raise ValueError("Effective to date must be after effective from date")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "org_123",
                "component_ids": ["BASIC_SALARY", "HRA", "DEARNESS_ALLOWANCE"],
                "status": "active",
                "notes": "Standard salary components for new organization",
                "effective_from": "2024-01-01T00:00:00"
            }
        }


class RemoveComponentsRequestDTO(BaseModel):
    """Request DTO for removing component assignments"""
    organization_id: str = Field(..., min_length=1, max_length=50, description="Organization ID")
    component_ids: List[str] = Field(..., min_items=1, description="List of component IDs to remove")
    notes: Optional[str] = Field(None, max_length=500, description="Removal notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "org_123",
                "component_ids": ["BONUS", "COMMISSION"],
                "notes": "Removing variable components"
            }
        }


class UpdateAssignmentRequestDTO(BaseModel):
    """Request DTO for updating component assignment"""
    assignment_id: str = Field(..., min_length=1, description="Assignment ID")
    status: Optional[AssignmentStatus] = None
    notes: Optional[str] = Field(None, max_length=500, description="Assignment notes")
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    organization_specific_config: Optional[Dict[str, Any]] = None
    
    @validator('effective_to')
    def validate_effective_dates(cls, v, values):
        if v and 'effective_from' in values and values['effective_from'] and v <= values['effective_from']:
            raise ValueError("Effective to date must be after effective from date")
        return v


class AssignmentQueryRequestDTO(BaseModel):
    """Request DTO for querying assignments"""
    organization_id: Optional[str] = Field(None, description="Filter by organization ID")
    component_id: Optional[str] = Field(None, description="Filter by component ID")
    status: Optional[AssignmentStatus] = Field(None, description="Filter by status")
    include_inactive: bool = Field(False, description="Include inactive assignments")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Page size")


# ==================== RESPONSE DTOs ====================

class GlobalSalaryComponentDTO(BaseModel):
    """Response DTO for global salary component"""
    component_id: str
    code: str
    name: str
    component_type: str
    value_type: str
    is_taxable: bool
    exemption_section: Optional[str] = None
    formula: Optional[str] = None
    default_value: Optional[float] = None
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "component_id": "BASIC_SALARY",
                "code": "BASIC",
                "name": "Basic Salary",
                "component_type": "EARNING",
                "value_type": "FIXED",
                "is_taxable": True,
                "exemption_section": "NONE",
                "description": "Basic salary component",
                "is_active": True
            }
        }


class ComponentAssignmentDTO(BaseModel):
    """Response DTO for component assignment"""
    assignment_id: str
    organization_id: str
    component_id: str
    component_name: Optional[str] = None
    component_code: Optional[str] = None
    status: AssignmentStatus
    assigned_by: str
    assigned_at: datetime
    notes: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    organization_specific_config: Dict[str, Any] = {}
    is_effective: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": "assign_123",
                "organization_id": "org_123",
                "component_id": "BASIC_SALARY",
                "component_name": "Basic Salary",
                "component_code": "BASIC",
                "status": "active",
                "assigned_by": "superadmin",
                "assigned_at": "2024-01-01T00:00:00",
                "is_effective": True
            }
        }


class AssignmentSummaryDTO(BaseModel):
    """Response DTO for assignment summary"""
    organization_id: str
    organization_name: Optional[str] = None
    total_components: int
    active_assignments: int
    inactive_assignments: int
    last_assignment_date: Optional[datetime] = None
    assigned_components: List[ComponentAssignmentDTO] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "org_123",
                "organization_name": "Acme Corp",
                "total_components": 15,
                "active_assignments": 12,
                "inactive_assignments": 3,
                "last_assignment_date": "2024-01-01T00:00:00"
            }
        }


class BulkAssignmentResponseDTO(BaseModel):
    """Response DTO for bulk assignment operations"""
    operation_id: str
    organization_id: str
    total_components: int
    successful_assignments: int
    failed_assignments: int
    successful_components: List[str]  # Component IDs
    failed_components: List[Dict[str, str]]  # {"component_id": "", "error": ""}
    operation_status: str
    processed_at: datetime
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "operation_id": "bulk_assign_123",
                "organization_id": "org_123",
                "total_components": 5,
                "successful_assignments": 4,
                "failed_assignments": 1,
                "successful_components": ["BASIC_SALARY", "HRA", "DA", "SPECIAL_ALLOWANCE"],
                "failed_components": [{"component_id": "BONUS", "error": "Component not found"}],
                "operation_status": "completed",
                "processed_at": "2024-01-01T00:00:00"
            }
        }


class AssignmentComparisonDTO(BaseModel):
    """Response DTO for comparing global vs organization components"""
    organization_id: str
    organization_name: Optional[str] = None
    global_components: List[GlobalSalaryComponentDTO]
    assigned_components: List[ComponentAssignmentDTO]
    available_for_assignment: List[GlobalSalaryComponentDTO]  # Global components not yet assigned
    assignment_summary: AssignmentSummaryDTO
    
    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "org_123",
                "organization_name": "Acme Corp",
                "global_components": [],
                "assigned_components": [],
                "available_for_assignment": [],
                "assignment_summary": {
                    "organization_id": "org_123",
                    "total_components": 0,
                    "active_assignments": 0,
                    "inactive_assignments": 0
                }
            }
        }


class AssignmentErrorResponseDTO(BaseModel):
    """Response DTO for assignment errors"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    organization_id: Optional[str] = None
    component_id: Optional[str] = None
    assignment_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "COMPONENT_NOT_FOUND",
                "error_message": "Component not found in global database",
                "error_details": {"component_id": "INVALID_COMPONENT"},
                "timestamp": "2024-01-01T00:00:00",
                "component_id": "INVALID_COMPONENT"
            }
        } 