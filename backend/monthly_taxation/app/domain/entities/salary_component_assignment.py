"""
Salary Component Assignment Domain Entity
Represents the assignment of a salary component to an organization
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any
from enum import Enum

from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.component_id import ComponentId

logger = logging.getLogger(__name__)


class AssignmentStatus(Enum):
    """Status of component assignment"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"


@dataclass
class SalaryComponentAssignment:
    """
    Domain entity representing the assignment of a salary component to an organization.
    """
    
    # Core identifiers (required fields first)
    organization_id: OrganizationId
    component_id: ComponentId
    assignment_id: str = field(default_factory=lambda: f"assign_{datetime.utcnow().timestamp()}")
    
    # Assignment metadata
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    assigned_by: str = ""
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    
    # Effective dates
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    
    # Organization-specific configuration
    organization_specific_config: Dict[str, Any] = field(default_factory=dict)
    
    # Component details (cached for performance)
    component_name: Optional[str] = None
    component_code: Optional[str] = None
    component_type: Optional[str] = None
    
    # Audit fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    updated_by: str = ""
    
    def __post_init__(self):
        """Post-initialization validation"""
        if not self.assignment_id:
            self.assignment_id = f"assign_{datetime.utcnow().timestamp()}"
        
        if not self.assigned_at:
            self.assigned_at = datetime.utcnow()
        
        if not self.created_at:
            self.created_at = datetime.utcnow()
        
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def is_effective(self, check_date: Optional[date] = None) -> bool:
        """
        Check if this assignment is effective on the given date.
        
        Args:
            check_date: Date to check (defaults to today)
            
        Returns:
            True if assignment is effective on the given date
        """
        if not check_date:
            check_date = date.today()
        
        # Check if assignment is active
        if self.status != AssignmentStatus.ACTIVE:
            return False
        
        # Check effective from date
        if self.effective_from and check_date < self.effective_from.date():
            return False
        
        # Check effective to date
        if self.effective_to and check_date > self.effective_to.date():
            return False
        
        return True
    
    def activate(self, activated_by: str, notes: Optional[str] = None):
        """Activate the assignment"""
        self.status = AssignmentStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = activated_by
        if notes:
            self.notes = notes
    
    def deactivate(self, deactivated_by: str, notes: Optional[str] = None):
        """Deactivate the assignment"""
        self.status = AssignmentStatus.INACTIVE
        self.updated_at = datetime.utcnow()
        self.updated_by = deactivated_by
        if notes:
            self.notes = notes
    
    def update_effective_dates(self, effective_from: Optional[datetime], effective_to: Optional[datetime], updated_by: str):
        """Update effective dates"""
        if effective_from and effective_to and effective_from >= effective_to:
            raise ValueError("Effective from date must be before effective to date")
        
        self.effective_from = effective_from
        self.effective_to = effective_to
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
    
    def update_config(self, config: Dict[str, Any], updated_by: str):
        """Update organization-specific configuration"""
        self.organization_specific_config = config
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
    
    def get_assignment_summary(self) -> Dict[str, Any]:
        """Get assignment summary for reporting"""
        return {
            "assignment_id": self.assignment_id,
            "organization_id": str(self.organization_id),
            "component_id": str(self.component_id),
            "component_name": self.component_name,
            "component_code": self.component_code,
            "status": self.status.value,
            "assigned_by": self.assigned_by,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "notes": self.notes,
            "effective_from": self.effective_from.isoformat() if self.effective_from else None,
            "effective_to": self.effective_to.isoformat() if self.effective_to else None,
            "is_effective": self.is_effective(),
            "organization_specific_config": self.organization_specific_config
        }
    
    def __str__(self) -> str:
        return f"Assignment({self.assignment_id}: {self.component_id} -> {self.organization_id})"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class BulkComponentAssignment:
    """
    Domain entity for bulk component assignment operations.
    """
    
    # Required fields first
    organization_id: OrganizationId
    component_ids: list[ComponentId]
    
    # Optional fields with defaults
    operation_id: str = field(default_factory=lambda: f"bulk_{datetime.utcnow().timestamp()}")
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    assigned_by: str = ""
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    organization_specific_config: Dict[str, Any] = field(default_factory=dict)
    
    # Operation tracking
    total_components: int = 0
    successful_assignments: int = 0
    failed_assignments: int = 0
    successful_component_ids: list[str] = field(default_factory=list)
    failed_component_ids: list[Dict[str, str]] = field(default_factory=list)  # [{"component_id": "", "error": ""}]
    operation_status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    
    def __post_init__(self):
        """Post-initialization setup"""
        if not self.operation_id:
            self.operation_id = f"bulk_{datetime.utcnow().timestamp()}"
        
        if not self.assigned_at:
            self.assigned_at = datetime.utcnow()
        
        self.total_components = len(self.component_ids)
    
    def mark_success(self, component_id: str):
        """Mark a component as successfully assigned"""
        self.successful_assignments += 1
        self.successful_component_ids.append(component_id)
    
    def mark_failure(self, component_id: str, error: str):
        """Mark a component as failed to assign"""
        self.failed_assignments += 1
        self.failed_component_ids.append({
            "component_id": component_id,
            "error": error
        })
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get operation summary for reporting"""
        return {
            "operation_id": self.operation_id,
            "organization_id": str(self.organization_id),
            "total_components": self.total_components,
            "successful_assignments": self.successful_assignments,
            "failed_assignments": self.failed_assignments,
            "successful_components": self.successful_component_ids,
            "failed_components": self.failed_component_ids,
            "operation_status": self.operation_status,
            "assigned_by": self.assigned_by,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "notes": self.notes
        } 