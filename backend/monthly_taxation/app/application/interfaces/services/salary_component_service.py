"""
Salary Component Service Interface
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from app.application.dto.salary_component_dto import (
    CreateSalaryComponentDTO,
    UpdateSalaryComponentDTO,
    SalaryComponentResponseDTO,
    SalaryComponentSearchFiltersDTO
)


class SalaryComponentService(ABC):
    """Interface for salary component service operations"""
    
    @abstractmethod
    async def create_component(
        self, 
        dto: CreateSalaryComponentDTO, 
        hostname: str,
        user_id: str
    ) -> SalaryComponentResponseDTO:
        """Create a new salary component"""
        pass
    
    @abstractmethod
    async def update_component(
        self, 
        component_id: str, 
        dto: UpdateSalaryComponentDTO, 
        hostname: str,
        user_id: str
    ) -> SalaryComponentResponseDTO:
        """Update existing salary component"""
        pass
    
    @abstractmethod
    async def get_component(self, component_id: str, hostname: str) -> SalaryComponentResponseDTO:
        """Get salary component by ID"""
        pass
    
    @abstractmethod
    async def get_component_by_code(self, code: str, hostname: str) -> SalaryComponentResponseDTO:
        """Get salary component by code"""
        pass
    
    @abstractmethod
    async def search_components(
        self, 
        filters: SalaryComponentSearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[SalaryComponentResponseDTO], int]:
        """Search salary components with filters"""
        pass
    
    @abstractmethod
    async def get_active_components(self, hostname: str) -> List[SalaryComponentResponseDTO]:
        """Get all active salary components"""
        pass
    
    @abstractmethod
    async def delete_component(self, component_id: str, hostname: str) -> bool:
        """Delete salary component"""
        pass
    
    @abstractmethod
    async def get_components_by_type(
        self, 
        component_type: str, 
        hostname: str
    ) -> List[SalaryComponentResponseDTO]:
        """Get components by type"""
        pass
    
    @abstractmethod
    async def validate_formula(self, formula: str) -> bool:
        """Validate component formula"""
        pass 