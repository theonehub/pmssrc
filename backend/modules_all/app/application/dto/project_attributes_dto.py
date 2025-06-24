"""
Project Attributes DTOs
Data Transfer Objects for project attributes operations following SOLID principles
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectAttributeCreateRequestDTO(BaseModel):
    """DTO for creating project attributes"""
    
    key: str = Field(..., description="Project attribute key")
    value: str = Field(..., description="Project attribute value")
    description: Optional[str] = Field(None, description="Description of the attribute")
    is_active: bool = Field(True, description="Whether the attribute is active")


class ProjectAttributeUpdateRequestDTO(BaseModel):
    """DTO for updating project attributes"""
    
    value: Optional[str] = Field(None, description="Project attribute value")
    description: Optional[str] = Field(None, description="Description of the attribute")
    is_active: Optional[bool] = Field(None, description="Whether the attribute is active")


class ProjectAttributeSearchFiltersDTO(BaseModel):
    """DTO for project attribute search filters"""
    
    key: Optional[str] = Field(None, description="Filter by key")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")


class ProjectAttributeResponseDTO(BaseModel):
    """DTO for project attribute response"""
    
    key: str
    value: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class ProjectAttributeSummaryDTO(BaseModel):
    """DTO for project attribute summary"""
    
    total_attributes: int = 0
    active_attributes: int = 0
    inactive_attributes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class ProjectAttributeAnalyticsDTO(BaseModel):
    """DTO for project attribute analytics"""
    
    total_count: int = 0
    usage_statistics: Dict[str, int] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


# Exception DTOs
class ProjectAttributeValidationError(Exception):
    """Exception raised when project attribute validation fails"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProjectAttributeBusinessRuleError(Exception):
    """Exception raised when project attribute business rules are violated"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ProjectAttributeNotFoundError(Exception):
    """Exception raised when project attribute is not found"""
    
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"Project attribute not found: {key}") 