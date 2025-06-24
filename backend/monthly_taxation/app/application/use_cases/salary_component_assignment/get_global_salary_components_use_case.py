"""
Get Global Salary Components Use Case
Retrieves all salary components from the global database
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

from app.application.interfaces.repositories.salary_component_assignment_repository import GlobalSalaryComponentRepository
from app.application.dto.salary_component_assignment_dto import GlobalSalaryComponentDTO

logger = logging.getLogger(__name__)


@dataclass
class GetGlobalSalaryComponentsCommand:
    """Command to get global salary components"""
    search_term: Optional[str] = None
    component_type: Optional[str] = None
    is_active: Optional[bool] = None
    page: int = 1
    page_size: int = 50


class GetGlobalSalaryComponentsUseCase:
    """Use case for retrieving global salary components"""
    
    def __init__(self, global_component_repository: GlobalSalaryComponentRepository):
        self.global_component_repository = global_component_repository
    
    async def execute(self, command: GetGlobalSalaryComponentsCommand) -> List[GlobalSalaryComponentDTO]:
        """
        Execute the use case.
        
        Args:
            command: Command containing search parameters
            
        Returns:
            List of global salary components
        """
        try:
            logger.info(f"Getting global salary components with filters: {command}")
            
            # Get components from global repository
            components, total_count = await self.global_component_repository.search_components(
                search_term=command.search_term,
                component_type=command.component_type,
                is_active=command.is_active,
                page=command.page,
                page_size=command.page_size
            )
            
            # Convert to DTOs
            component_dtos = []
            for component in components:
                dto = GlobalSalaryComponentDTO(
                    component_id=component.get("component_id", ""),
                    code=component.get("code", ""),
                    name=component.get("name", ""),
                    component_type=component.get("component_type", ""),
                    value_type=component.get("value_type", ""),
                    is_taxable=component.get("is_taxable", False),
                    exemption_section=component.get("exemption_section"),
                    formula=component.get("formula"),
                    default_value=component.get("default_value"),
                    description=component.get("description"),
                    is_active=component.get("is_active", True),
                    created_at=component.get("created_at"),
                    updated_at=component.get("updated_at")
                )
                component_dtos.append(dto)
            
            logger.info(f"Retrieved {len(component_dtos)} global components (total: {total_count})")
            return component_dtos
            
        except Exception as e:
            logger.error(f"Error getting global salary components: {e}")
            raise
    
    async def get_all_active_components(self) -> List[GlobalSalaryComponentDTO]:
        """
        Get all active global components.
        
        Returns:
            List of active global salary components
        """
        try:
            logger.info("Getting all active global salary components")
            
            components = await self.global_component_repository.get_active_components()
            
            # Convert to DTOs
            component_dtos = []
            for component in components:
                dto = GlobalSalaryComponentDTO(
                    component_id=component.get("component_id", ""),
                    code=component.get("code", ""),
                    name=component.get("name", ""),
                    component_type=component.get("component_type", ""),
                    value_type=component.get("value_type", ""),
                    is_taxable=component.get("is_taxable", False),
                    exemption_section=component.get("exemption_section"),
                    formula=component.get("formula"),
                    default_value=component.get("default_value"),
                    description=component.get("description"),
                    is_active=component.get("is_active", True),
                    created_at=component.get("created_at"),
                    updated_at=component.get("updated_at")
                )
                component_dtos.append(dto)
            
            logger.info(f"Retrieved {len(component_dtos)} active global components")
            return component_dtos
            
        except Exception as e:
            logger.error(f"Error getting active global salary components: {e}")
            raise
    
    async def get_components_by_type(self, component_type: str) -> List[GlobalSalaryComponentDTO]:
        """
        Get global components by type.
        
        Args:
            component_type: Type of components to retrieve
            
        Returns:
            List of global salary components of specified type
        """
        try:
            logger.info(f"Getting global salary components by type: {component_type}")
            
            components = await self.global_component_repository.get_components_by_type(component_type)
            
            # Convert to DTOs
            component_dtos = []
            for component in components:
                dto = GlobalSalaryComponentDTO(
                    component_id=component.get("component_id", ""),
                    code=component.get("code", ""),
                    name=component.get("name", ""),
                    component_type=component.get("component_type", ""),
                    value_type=component.get("value_type", ""),
                    is_taxable=component.get("is_taxable", False),
                    exemption_section=component.get("exemption_section"),
                    formula=component.get("formula"),
                    default_value=component.get("default_value"),
                    description=component.get("description"),
                    is_active=component.get("is_active", True),
                    created_at=component.get("created_at"),
                    updated_at=component.get("updated_at")
                )
                component_dtos.append(dto)
            
            logger.info(f"Retrieved {len(component_dtos)} global components of type {component_type}")
            return component_dtos
            
        except Exception as e:
            logger.error(f"Error getting global salary components by type {component_type}: {e}")
            raise 