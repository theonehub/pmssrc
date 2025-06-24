"""
Salary Component Assignment Repository Interface
Defines contract for salary component assignment data access
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from datetime import datetime

from app.domain.entities.salary_component_assignment import SalaryComponentAssignment, AssignmentStatus
from app.domain.value_objects.organization_id import OrganizationId
from app.domain.value_objects.component_id import ComponentId


class SalaryComponentAssignmentRepository(ABC):
    """Repository interface for salary component assignments"""
    
    @abstractmethod
    async def save_assignment(self, assignment: SalaryComponentAssignment) -> SalaryComponentAssignment:
        """Save a component assignment"""
        pass
    
    @abstractmethod
    async def save_assignments(self, assignments: List[SalaryComponentAssignment]) -> List[SalaryComponentAssignment]:
        """Save multiple component assignments"""
        pass
    
    @abstractmethod
    async def get_assignment_by_id(self, assignment_id: str) -> Optional[SalaryComponentAssignment]:
        """Get assignment by ID"""
        pass
    
    @abstractmethod
    async def get_assignments_by_organization(
        self, 
        organization_id: OrganizationId,
        include_inactive: bool = False
    ) -> List[SalaryComponentAssignment]:
        """Get all assignments for an organization"""
        pass
    
    @abstractmethod
    async def get_assignments_by_component(
        self, 
        component_id: ComponentId,
        include_inactive: bool = False
    ) -> List[SalaryComponentAssignment]:
        """Get all assignments for a component"""
        pass
    
    @abstractmethod
    async def get_assignment_by_organization_and_component(
        self,
        organization_id: OrganizationId,
        component_id: ComponentId
    ) -> Optional[SalaryComponentAssignment]:
        """Get specific assignment by organization and component"""
        pass
    
    @abstractmethod
    async def update_assignment(self, assignment: SalaryComponentAssignment) -> SalaryComponentAssignment:
        """Update an existing assignment"""
        pass
    
    @abstractmethod
    async def delete_assignment(self, assignment_id: str) -> bool:
        """Delete an assignment"""
        pass
    
    @abstractmethod
    async def delete_assignments_by_organization_and_components(
        self,
        organization_id: OrganizationId,
        component_ids: List[ComponentId]
    ) -> int:
        """Delete multiple assignments for an organization"""
        pass
    
    @abstractmethod
    async def search_assignments(
        self,
        organization_id: Optional[OrganizationId] = None,
        component_id: Optional[ComponentId] = None,
        status: Optional[AssignmentStatus] = None,
        include_inactive: bool = False,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[SalaryComponentAssignment], int]:
        """Search assignments with filters and pagination"""
        pass
    
    @abstractmethod
    async def get_assignment_summary(self, organization_id: OrganizationId) -> dict:
        """Get assignment summary for an organization"""
        pass
    
    @abstractmethod
    async def check_component_assigned(
        self,
        organization_id: OrganizationId,
        component_id: ComponentId
    ) -> bool:
        """Check if a component is assigned to an organization"""
        pass
    
    @abstractmethod
    async def get_effective_assignments(
        self,
        organization_id: OrganizationId,
        as_of_date: Optional[datetime] = None
    ) -> List[SalaryComponentAssignment]:
        """Get effective assignments for an organization as of a specific date"""
        pass


class GlobalSalaryComponentRepository(ABC):
    """Repository interface for global salary components"""
    
    @abstractmethod
    async def get_all_components(self) -> List[dict]:
        """Get all global salary components"""
        pass
    
    @abstractmethod
    async def get_component_by_id(self, component_id: str) -> Optional[dict]:
        """Get global component by ID"""
        pass
    
    @abstractmethod
    async def get_components_by_type(self, component_type: str) -> List[dict]:
        """Get global components by type"""
        pass
    
    @abstractmethod
    async def get_active_components(self) -> List[dict]:
        """Get all active global components"""
        pass
    
    @abstractmethod
    async def search_components(
        self,
        search_term: Optional[str] = None,
        component_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[dict], int]:
        """Search global components with filters and pagination"""
        pass 