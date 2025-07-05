"""
Project Attributes DTOs
Data Transfer Objects for project attributes operations following SOLID principles
Enhanced for organization-specific configurations with multiple value types
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class ValueType(str, Enum):
    """Supported value types for project attributes"""
    BOOLEAN = "boolean"
    STRING = "string"
    NUMBER = "number"
    TEXT = "text"
    MULTILINE_TEXT = "multiline_text"
    DROPDOWN = "dropdown"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    DATE = "date"
    JSON = "json"


class ProjectAttributeCreateRequestDTO(BaseModel):
    """DTO for creating project attributes with enhanced type support"""
    
    key: str = Field(..., description="Project attribute key", min_length=1, max_length=100)
    value: Union[str, bool, int, float] = Field(..., description="Project attribute value")
    value_type: ValueType = Field(..., description="Type of the attribute value")
    description: Optional[str] = Field(None, description="Description of the attribute", max_length=500)
    is_active: bool = Field(True, description="Whether the attribute is active")
    default_value: Optional[Union[str, bool, int, float]] = Field(None, description="Default value for the attribute")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Type-specific validation rules")
    category: Optional[str] = Field(None, description="Category for grouping attributes", max_length=50)
    is_system: bool = Field(False, description="Whether this is a system-managed attribute")
    
    @validator('key')
    def validate_key(cls, v):
        """Validate key format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Key must contain only alphanumeric characters, underscores, and hyphens')
        return v.lower()
    
    @validator('value')
    def validate_value_type(cls, v, values):
        """Validate value matches the specified type"""
        if 'value_type' not in values:
            return v
            
        value_type = values['value_type']
        
        if value_type == ValueType.BOOLEAN:
            if not isinstance(v, bool):
                raise ValueError('Value must be boolean for boolean type')
        elif value_type == ValueType.NUMBER:
            if not isinstance(v, (int, float)):
                try:
                    float(v)
                except (ValueError, TypeError):
                    raise ValueError('Value must be numeric for number type')
        elif value_type == ValueType.EMAIL:
            if not isinstance(v, str) or '@' not in v:
                raise ValueError('Value must be a valid email address')
        elif value_type == ValueType.PHONE:
            if not isinstance(v, str) or len(v) < 10:
                raise ValueError('Value must be a valid phone number')
        elif value_type == ValueType.URL:
            if not isinstance(v, str) or not v.startswith(('http://', 'https://')):
                raise ValueError('Value must be a valid URL')
        elif value_type == ValueType.DATE:
            if not isinstance(v, str):
                raise ValueError('Value must be a date string')
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Value must be a valid date in ISO format')
        
        return v
    
    @validator('validation_rules')
    def validate_validation_rules(cls, v, values):
        """Validate type-specific validation rules"""
        if v is None:
            return v
            
        if 'value_type' not in values:
            return v
            
        value_type = values['value_type']
        
        if value_type == ValueType.DROPDOWN:
            if 'options' not in v or not isinstance(v['options'], list):
                raise ValueError('Dropdown type requires options list in validation_rules')
        elif value_type == ValueType.NUMBER:
            if 'min' in v and not isinstance(v['min'], (int, float)):
                raise ValueError('Number min value must be numeric')
            if 'max' in v and not isinstance(v['max'], (int, float)):
                raise ValueError('Number max value must be numeric')
        elif value_type == ValueType.STRING:
            if 'max_length' in v and not isinstance(v['max_length'], int):
                raise ValueError('String max_length must be integer')
        
        return v


class ProjectAttributeUpdateRequestDTO(BaseModel):
    """DTO for updating project attributes"""
    
    value: Optional[Union[str, bool, int, float]] = Field(None, description="Project attribute value")
    description: Optional[str] = Field(None, description="Description of the attribute", max_length=500)
    is_active: Optional[bool] = Field(None, description="Whether the attribute is active")
    default_value: Optional[Union[str, bool, int, float]] = Field(None, description="Default value for the attribute")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Type-specific validation rules")
    category: Optional[str] = Field(None, description="Category for grouping attributes", max_length=50)


class ProjectAttributeSearchFiltersDTO(BaseModel):
    """DTO for project attribute search filters"""
    
    key: Optional[str] = Field(None, description="Filter by key")
    value_type: Optional[ValueType] = Field(None, description="Filter by value type")
    category: Optional[str] = Field(None, description="Filter by category")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_system: Optional[bool] = Field(None, description="Filter by system-managed status")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")


class ProjectAttributeResponseDTO(BaseModel):
    """DTO for project attribute response"""
    
    key: str
    value: Union[str, bool, int, float]
    value_type: ValueType
    description: Optional[str] = None
    is_active: bool = True
    default_value: Optional[Union[str, bool, int, float]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    is_system: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class ProjectAttributeSummaryDTO(BaseModel):
    """DTO for project attribute summary"""
    
    total_attributes: int = 0
    active_attributes: int = 0
    inactive_attributes: int = 0
    system_attributes: int = 0
    custom_attributes: int = 0
    type_distribution: Dict[str, int] = Field(default_factory=dict)
    category_distribution: Dict[str, int] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class ProjectAttributeAnalyticsDTO(BaseModel):
    """DTO for project attribute analytics"""
    
    total_count: int = 0
    usage_statistics: Dict[str, int] = Field(default_factory=dict)
    type_usage: Dict[str, int] = Field(default_factory=dict)
    category_usage: Dict[str, int] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class ProjectAttributeTemplateDTO(BaseModel):
    """DTO for predefined attribute templates"""
    
    name: str = Field(..., description="Template name")
    key: str = Field(..., description="Generated key from template")
    value_type: ValueType = Field(..., description="Value type")
    description: str = Field(..., description="Template description")
    default_value: Optional[Union[str, bool, int, float]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    category: str = Field(..., description="Template category")
    is_system: bool = Field(True, description="System template")


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


class ProjectAttributeTypeMismatchError(Exception):
    """Exception raised when value type doesn't match attribute type"""
    
    def __init__(self, key: str, expected_type: str, actual_type: str):
        self.key = key
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(f"Type mismatch for attribute {key}: expected {expected_type}, got {actual_type}")


# Predefined attribute templates for common organization configurations
PREDEFINED_ATTRIBUTES = [
    ProjectAttributeTemplateDTO(
        name="Monthly Disburse LTA",
        key="monthly_disburse_lta",
        value_type=ValueType.BOOLEAN,
        description="Enable/disable monthly LTA disbursement",
        default_value=False,
        category="payroll"
    ),
    ProjectAttributeTemplateDTO(
        name="Organization Phone",
        key="org_phone",
        value_type=ValueType.PHONE,
        description="Organization contact phone number",
        validation_rules={"format": "international"},
        category="contact"
    ),
    ProjectAttributeTemplateDTO(
        name="Organization Email",
        key="org_email",
        value_type=ValueType.EMAIL,
        description="Organization contact email",
        category="contact"
    ),
    ProjectAttributeTemplateDTO(
        name="Perquisites Required",
        key="perquisites_required",
        value_type=ValueType.BOOLEAN,
        description="Enable/disable perquisites in tax calculations",
        default_value=True,
        category="taxation"
    ),
    ProjectAttributeTemplateDTO(
        name="Default Currency",
        key="default_currency",
        value_type=ValueType.DROPDOWN,
        description="Default currency for financial calculations",
        default_value="INR",
        validation_rules={"options": ["INR", "USD", "EUR", "GBP"]},
        category="finance"
    ),
    ProjectAttributeTemplateDTO(
        name="Working Hours Per Day",
        key="working_hours_per_day",
        value_type=ValueType.NUMBER,
        description="Standard working hours per day",
        default_value=8.0,
        validation_rules={"min": 1, "max": 24},
        category="attendance"
    ),
    ProjectAttributeTemplateDTO(
        name="Organization Address",
        key="org_address",
        value_type=ValueType.MULTILINE_TEXT,
        description="Organization registered address",
        category="contact"
    ),
    ProjectAttributeTemplateDTO(
        name="Tax Year Start Month",
        key="tax_year_start_month",
        value_type=ValueType.DROPDOWN,
        description="Starting month of tax year",
        default_value="4",
        validation_rules={"options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]},
        category="taxation"
    )
] 