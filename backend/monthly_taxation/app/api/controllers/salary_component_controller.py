"""
Salary Component Controller
"""

import logging
from typing import List, Dict, Any
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.application.interfaces.services.salary_component_service import SalaryComponentService


class CurrentUser(BaseModel):
    """Current user model for controller operations"""
    employee_id: str
    hostname: str
    role: str

    @property
    def user_id(self) -> str:
        """Alias for employee_id for backward compatibility"""
        return self.employee_id
from app.application.dto.salary_component_dto import (
    CreateSalaryComponentDTO,
    UpdateSalaryComponentDTO,
    SalaryComponentResponseDTO,
    SalaryComponentSearchFiltersDTO
)
from app.domain.exceptions.salary_component_exceptions import (
    SalaryComponentNotFoundError,
    SalaryComponentAlreadyExistsError,
    SalaryComponentInUseError,
    SalaryComponentValidationError
)

logger = logging.getLogger(__name__)


class SalaryComponentController:
    """Controller for salary component operations"""
    
    def __init__(self, service: SalaryComponentService):
        self.service = service
    
    async def create_component(
        self, 
        dto: CreateSalaryComponentDTO, 
        current_user: CurrentUser
    ) -> Dict[str, Any]:
        """Create new salary component"""
        try:
            logger.info(f"Controller: Creating salary component {dto.code}")
            
            component = await self.service.create_component(dto, current_user.hostname, current_user.user_id)
            
            return {
                "status": "success",
                "message": "Salary component created successfully",
                "data": component.dict()
            }
            
        except SalaryComponentAlreadyExistsError as e:
            logger.warning(f"Component already exists: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except SalaryComponentValidationError as e:
            logger.warning(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error creating component: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def update_component(
        self, 
        component_id: str,
        dto: UpdateSalaryComponentDTO, 
        current_user: CurrentUser
    ) -> Dict[str, Any]:
        """Update salary component"""
        try:
            logger.info(f"Controller: Updating salary component {component_id}")
            
            component = await self.service.update_component(component_id, dto, current_user.hostname, current_user.user_id)
            
            return {
                "status": "success",
                "message": "Salary component updated successfully",
                "data": component.dict()
            }
            
        except SalaryComponentNotFoundError as e:
            logger.warning(f"Component not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except SalaryComponentAlreadyExistsError as e:
            logger.warning(f"Component already exists: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except SalaryComponentValidationError as e:
            logger.warning(f"Validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error updating component: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_component(self, component_id: str, current_user: CurrentUser) -> Dict[str, Any]:
        """Get salary component by ID"""
        try:
            logger.info(f"Controller: Getting salary component {component_id}")
            
            component = await self.service.get_component(component_id, current_user.hostname)
            
            return {
                "status": "success",
                "data": component.dict()
            }
            
        except SalaryComponentNotFoundError as e:
            logger.warning(f"Component not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error getting component: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_component_by_code(self, code: str, current_user: CurrentUser) -> Dict[str, Any]:
        """Get salary component by code"""
        try:
            logger.info(f"Controller: Getting salary component by code {code}")
            
            component = await self.service.get_component_by_code(code, current_user.hostname)
            
            return {
                "status": "success",
                "data": component.dict()
            }
            
        except SalaryComponentNotFoundError as e:
            logger.warning(f"Component not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error getting component by code: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def search_components(
        self, 
        filters: SalaryComponentSearchFiltersDTO, 
        current_user: CurrentUser
    ) -> Dict[str, Any]:
        """Search salary components"""
        try:
            logger.info("Controller: Searching salary components")
            
            components, total_count = await self.service.search_components(filters, current_user.hostname)
            
            return {
                "status": "success",
                "data": {
                    "items": [comp.dict() for comp in components],
                    "total_count": total_count,
                    "page": filters.page,
                    "page_size": filters.page_size,
                    "total_pages": (total_count + filters.page_size - 1) // filters.page_size
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching components: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_active_components(self, current_user: CurrentUser) -> Dict[str, Any]:
        """Get all active salary components"""
        try:
            logger.info("Controller: Getting active salary components")
            
            components = await self.service.get_active_components(current_user.hostname)
            
            return {
                "status": "success",
                "data": [comp.dict() for comp in components]
            }
            
        except Exception as e:
            logger.error(f"Error getting active components: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def delete_component(self, component_id: str, current_user: CurrentUser) -> Dict[str, Any]:
        """Delete salary component"""
        try:
            logger.info(f"Controller: Deleting salary component {component_id}")
            
            success = await self.service.delete_component(component_id, current_user.hostname)
            
            if success:
                return {
                    "status": "success",
                    "message": "Salary component deleted successfully"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to delete component"
                )
            
        except SalaryComponentNotFoundError as e:
            logger.warning(f"Component not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except SalaryComponentInUseError as e:
            logger.warning(f"Component in use: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error deleting component: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_components_by_type(
        self, 
        component_type: str, 
        current_user: CurrentUser
    ) -> Dict[str, Any]:
        """Get components by type"""
        try:
            logger.info(f"Controller: Getting components by type {component_type}")
            
            components = await self.service.get_components_by_type(component_type, current_user.hostname)
            
            return {
                "status": "success",
                "data": [comp.dict() for comp in components]
            }
            
        except Exception as e:
            logger.error(f"Error getting components by type: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def validate_formula(self, formula: str) -> Dict[str, Any]:
        """Validate formula"""
        try:
            logger.info("Controller: Validating formula")
            
            is_valid = await self.service.validate_formula(formula)
            
            return {
                "status": "success",
                "data": {
                    "is_valid": is_valid,
                    "formula": formula
                }
            }
            
        except SalaryComponentValidationError as e:
            logger.warning(f"Formula validation error: {e}")
            return {
                "status": "error",
                "data": {
                    "is_valid": False,
                    "formula": formula,
                    "error": str(e)
                }
            }
        except Exception as e:
            logger.error(f"Error validating formula: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            ) 