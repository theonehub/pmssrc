"""
Salary Component Service Implementation
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime

from app.application.interfaces.services.salary_component_service import SalaryComponentService
from app.application.interfaces.repositories.salary_component_repository import SalaryComponentRepository
from app.application.dto.salary_component_dto import (
    CreateSalaryComponentDTO, 
    UpdateSalaryComponentDTO,
    SalaryComponentResponseDTO,
    SalaryComponentSearchFiltersDTO
)
from app.domain.entities.salary_component import SalaryComponent, ExemptionSection
from app.domain.value_objects.component_id import ComponentId
from app.domain.value_objects.component_type import ComponentType, ValueType
from app.domain.services.formula_engine import FormulaEngine
from app.domain.exceptions.salary_component_exceptions import (
    SalaryComponentNotFoundError,
    SalaryComponentAlreadyExistsError,
    SalaryComponentInUseError,
    SalaryComponentValidationError
)

logger = logging.getLogger(__name__)


class SalaryComponentServiceImpl(SalaryComponentService):
    """Service implementation for salary component operations"""
    
    def __init__(
        self, 
        repository: SalaryComponentRepository,
        formula_engine: FormulaEngine
    ):
        self.repository = repository
        self.formula_engine = formula_engine
    
    async def create_component(
        self, 
        dto: CreateSalaryComponentDTO, 
        hostname: str,
        user_id: str
    ) -> SalaryComponentResponseDTO:
        """Create a new salary component"""
        try:
            logger.info(f"Creating salary component: {dto.code}")
            
            # Check if code already exists
            if await self.repository.check_code_exists(dto.code, hostname):
                raise SalaryComponentAlreadyExistsError(f"Component with code '{dto.code}' already exists")
            
            # Validate formula if provided
            if dto.formula:
                self._validate_formula(dto.formula)
            
            # Create entity
            component = SalaryComponent.create(
                id=ComponentId.generate(),
                code=dto.code,
                name=dto.name,
                component_type=ComponentType(dto.component_type),
                value_type=ValueType(dto.value_type),
                is_taxable=dto.is_taxable,
                exemption_section=ExemptionSection(dto.exemption_section),
                formula=dto.formula,
                default_value=dto.default_value,
                description=dto.description,
                created_by=user_id
            )
            
            # Save to repository
            saved_component = await self.repository.save(component, hostname)
            
            logger.info(f"Created salary component: {saved_component.code}")
            return self._entity_to_response_dto(saved_component)
            
        except Exception as e:
            logger.error(f"Error creating salary component: {e}")
            raise
    
    async def update_component(
        self, 
        component_id: str, 
        dto: UpdateSalaryComponentDTO, 
        hostname: str,
        user_id: str
    ) -> SalaryComponentResponseDTO:
        """Update existing salary component"""
        try:
            logger.info(f"Updating salary component: {component_id}")
            
            # Get existing component
            existing = await self.repository.get_by_id(ComponentId(component_id), hostname)
            if not existing:
                raise SalaryComponentNotFoundError(f"Component with ID '{component_id}' not found")
            
            # Check if code change conflicts
            if dto.code and dto.code != existing.code:
                if await self.repository.check_code_exists(dto.code, hostname, ComponentId(component_id)):
                    raise SalaryComponentAlreadyExistsError(f"Component with code '{dto.code}' already exists")
            
            # Validate formula if provided
            if dto.formula:
                self._validate_formula(dto.formula)
            
            # Update entity
            updated_component = existing.update(
                name=dto.name or existing.name,
                code=dto.code or existing.code,
                component_type=ComponentType(dto.component_type) if dto.component_type else existing.component_type,
                value_type=ValueType(dto.value_type) if dto.value_type else existing.value_type,
                is_taxable=dto.is_taxable if dto.is_taxable is not None else existing.is_taxable,
                exemption_section=dto.exemption_section or existing.exemption_section,
                formula=dto.formula if dto.formula is not None else existing.formula,
                default_value=dto.default_value if dto.default_value is not None else existing.default_value,
                description=dto.description if dto.description is not None else existing.description,
                updated_by=user_id
            )
            
            # Save to repository
            saved_component = await self.repository.save(updated_component, hostname)
            
            logger.info(f"Updated salary component: {saved_component.code}")
            return self._entity_to_response_dto(saved_component)
            
        except Exception as e:
            logger.error(f"Error updating salary component: {e}")
            raise
    
    async def get_component(self, component_id: str, hostname: str) -> SalaryComponentResponseDTO:
        """Get salary component by ID"""
        try:
            component = await self.repository.get_by_id(ComponentId(component_id), hostname)
            if not component:
                raise SalaryComponentNotFoundError(f"Component with ID '{component_id}' not found")
            
            return self._entity_to_response_dto(component)
            
        except Exception as e:
            logger.error(f"Error getting salary component: {e}")
            raise
    
    async def get_component_by_code(self, code: str, hostname: str) -> SalaryComponentResponseDTO:
        """Get salary component by code"""
        try:
            component = await self.repository.get_by_code(code, hostname)
            if not component:
                raise SalaryComponentNotFoundError(f"Component with code '{code}' not found")
            
            return self._entity_to_response_dto(component)
            
        except Exception as e:
            logger.error(f"Error getting salary component by code: {e}")
            raise
    
    async def search_components(
        self, 
        filters: SalaryComponentSearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[SalaryComponentResponseDTO], int]:
        """Search salary components with filters"""
        try:
            components, total_count = await self.repository.find_with_filters(filters, hostname)
            
            response_dtos = [self._entity_to_response_dto(comp) for comp in components]
            
            return response_dtos, total_count
            
        except Exception as e:
            logger.error(f"Error searching salary components: {e}")
            raise
    
    async def get_active_components(self, hostname: str) -> List[SalaryComponentResponseDTO]:
        """Get all active salary components"""
        try:
            components = await self.repository.get_all_active(hostname)
            return [self._entity_to_response_dto(comp) for comp in components]
            
        except Exception as e:
            logger.error(f"Error getting active salary components: {e}")
            raise
    
    async def delete_component(self, component_id: str, hostname: str) -> bool:
        """Delete salary component"""
        try:
            logger.info(f"Deleting salary component: {component_id}")
            
            # Check if component exists
            component = await self.repository.get_by_id(ComponentId(component_id), hostname)
            if not component:
                raise SalaryComponentNotFoundError(f"Component with ID '{component_id}' not found")
            
            # Check usage
            usage_count = await self.repository.get_usage_count(ComponentId(component_id), hostname)
            if usage_count > 0:
                raise SalaryComponentInUseError(
                    f"Component '{component.code}' is in use by {usage_count} employees"
                )
            
            # Delete from repository
            result = await self.repository.delete(ComponentId(component_id), hostname)
            
            logger.info(f"Deleted salary component: {component.code}")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting salary component: {e}")
            raise
    
    async def get_components_by_type(
        self, 
        component_type: str, 
        hostname: str
    ) -> List[SalaryComponentResponseDTO]:
        """Get components by type"""
        try:
            components = await self.repository.get_components_by_type(component_type, hostname)
            return [self._entity_to_response_dto(comp) for comp in components]
            
        except Exception as e:
            logger.error(f"Error getting components by type: {e}")
            raise
    
    async def validate_formula(self, formula: str) -> bool:
        """Validate component formula"""
        try:
            return self._validate_formula(formula)
        except Exception as e:
            logger.error(f"Error validating formula: {e}")
            raise
    
    def _validate_formula(self, formula: str) -> bool:
        """Validate formula using formula engine"""
        try:
            # Use formula engine to validate
            test_variables = {"BASIC": 10000, "HRA": 5000, "DA": 2000}
            result = self.formula_engine.evaluate_formula(formula, test_variables)
            
            if result is None:
                raise SalaryComponentValidationError(f"Invalid formula: {formula}")
            
            return True
            
        except Exception as e:
            raise SalaryComponentValidationError(f"Formula validation failed: {str(e)}")
    
    def _entity_to_response_dto(self, component: SalaryComponent) -> SalaryComponentResponseDTO:
        """Convert entity to response DTO"""
        return SalaryComponentResponseDTO(
            id=component.id.value,
            code=component.code,
            name=component.name,
            component_type=component.component_type.value,
            value_type=component.value_type.value,
            is_taxable=component.is_taxable,
            exemption_section=component.exemption_section.value,
            formula=component.formula,
            default_value=component.default_value,
            description=component.description,
            is_active=component.is_active,
            created_at=component.created_at,
            updated_at=component.updated_at,
            created_by=component.created_by,
            updated_by=component.updated_by,
            metadata=component.metadata
        ) 