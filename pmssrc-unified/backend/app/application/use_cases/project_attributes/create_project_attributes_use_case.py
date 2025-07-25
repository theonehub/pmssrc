"""
Create Project Attributes Use Case
Business workflow for creating project attributes with enhanced type support
"""

import logging
from typing import Optional

from app.application.dto.project_attributes_dto import (
    ProjectAttributeCreateRequestDTO,
    ProjectAttributeResponseDTO,
    ProjectAttributeBusinessRuleError,
    ProjectAttributeValidationError
)
from app.application.interfaces.repositories.project_attributes_repository import ProjectAttributesRepository


class CreateProjectAttributesUseCase:
    """
    Use case for creating project attributes.
    
    Handles the business logic for creating organization-specific configuration attributes.
    """
    
    def __init__(self, repository: ProjectAttributesRepository, event_publisher=None):
        self._repository = repository
        self._event_publisher = event_publisher
        self._logger = logging.getLogger(__name__)
    
    async def execute(
        self, 
        request: ProjectAttributeCreateRequestDTO,
        hostname: str
    ) -> ProjectAttributeResponseDTO:
        """
        Execute project attribute creation workflow.
        
        Args:
            request: Project attribute creation request
            hostname: Organisation hostname
            
        Returns:
            ProjectAttributeResponseDTO with created attribute details
            
        Raises:
            ProjectAttributeValidationError: Validation failed
            ProjectAttributeBusinessRuleError: Business rules violated
        """
        
        try:
            self._logger.info(f"Creating project attribute: {request.key}")
            
            # Validate business rules
            await self._validate_business_rules(request, hostname)
            
            # Create the attribute
            response = await self._repository.create(request, hostname)
            
            # Publish event if event publisher is available
            if self._event_publisher:
                await self._publish_attribute_created_event(response, hostname)
            
            self._logger.info(f"Successfully created project attribute: {request.key}")
            return response
            
        except (ProjectAttributeValidationError, ProjectAttributeBusinessRuleError):
            raise
        except Exception as e:
            self._logger.error(f"Failed to create project attribute: {str(e)}")
            raise ProjectAttributeBusinessRuleError(f"Failed to create attribute: {str(e)}")
    
    async def _validate_business_rules(
        self, 
        request: ProjectAttributeCreateRequestDTO, 
        hostname: str
    ) -> None:
        """
        Validate business rules for attribute creation.
        
        Args:
            request: Creation request
            hostname: Organisation hostname
            
        Raises:
            ProjectAttributeBusinessRuleError: Business rules violated
        """
        
        # Check if attribute with same key already exists
        existing = await self._repository.get_by_key(request.key, hostname)
        if existing:
            raise ProjectAttributeBusinessRuleError(
                f"Attribute with key '{request.key}' already exists for this organization"
            )
        
        # Validate key format
        if not self._is_valid_key_format(request.key):
            raise ProjectAttributeValidationError(
                "Key must contain only alphanumeric characters, underscores, and hyphens"
            )
        
        # Validate key length
        if len(request.key) > 100:
            raise ProjectAttributeValidationError("Key must be 100 characters or less")
        
        # Validate description length
        if request.description and len(request.description) > 500:
            raise ProjectAttributeValidationError("Description must be 500 characters or less")
        
        # Validate category length
        if request.category and len(request.category) > 50:
            raise ProjectAttributeValidationError("Category must be 50 characters or less")
        
        # Validate value type specific rules
        await self._validate_type_specific_rules(request)
    
    async def _validate_type_specific_rules(self, request: ProjectAttributeCreateRequestDTO) -> None:
        """
        Validate type-specific business rules.
        
        Args:
            request: Creation request
            
        Raises:
            ProjectAttributeValidationError: Validation failed
        """
        
        if request.value_type.value == "dropdown":
            if not request.validation_rules or "options" not in request.validation_rules:
                raise ProjectAttributeValidationError(
                    "Dropdown type requires options list in validation_rules"
                )
            
            options = request.validation_rules["options"]
            if not isinstance(options, list) or len(options) == 0:
                raise ProjectAttributeValidationError(
                    "Dropdown options must be a non-empty list"
                )
            
            if request.value not in options:
                raise ProjectAttributeValidationError(
                    f"Value '{request.value}' is not in the dropdown options"
                )
        
        elif request.value_type.value == "number":
            if request.validation_rules:
                min_val = request.validation_rules.get("min")
                max_val = request.validation_rules.get("max")
                
                if min_val is not None and request.value < min_val:
                    raise ProjectAttributeValidationError(
                        f"Value {request.value} is less than minimum {min_val}"
                    )
                
                if max_val is not None and request.value > max_val:
                    raise ProjectAttributeValidationError(
                        f"Value {request.value} is greater than maximum {max_val}"
                    )
    
    def _is_valid_key_format(self, key: str) -> bool:
        """
        Check if key format is valid.
        
        Args:
            key: Key to validate
            
        Returns:
            True if valid, False otherwise
        """
        return key.replace('_', '').replace('-', '').isalnum()
    
    async def _publish_attribute_created_event(
        self, 
        response: ProjectAttributeResponseDTO, 
        hostname: str
    ) -> None:
        """
        Publish attribute created event.
        
        Args:
            response: Created attribute response
            hostname: Organisation hostname
        """
        try:
            event_data = {
                "event_type": "project_attribute_created",
                "attribute_key": response.key,
                "value_type": response.value_type.value,
                "category": response.category,
                "organisation_hostname": hostname,
                "timestamp": response.created_at.isoformat() if response.created_at else None
            }
            
            await self._event_publisher.publish("project_attributes", event_data)
            
        except Exception as e:
            self._logger.warning(f"Failed to publish attribute created event: {e}")
            # Don't fail the operation if event publishing fails 