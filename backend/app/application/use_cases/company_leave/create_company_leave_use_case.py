"""
Create Company Leave Use Case
Business workflow for creating new company leave policies
"""

import logging
from typing import Optional
from datetime import datetime

from app.application.dto.company_leave_dto import (
    CreateCompanyLeaveRequestDTO, 
    CompanyLeaveResponseDTO,
    CompanyLeaveDTOValidationError
)
from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveCommandRepository,
    CompanyLeaveQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.domain.entities.company_leave import CompanyLeave


logger = logging.getLogger(__name__)


class CreateCompanyLeaveUseCase:
    """
    Use case for creating company leave policies.
    
    Follows SOLID principles:
    - SRP: Only handles company leave creation workflow
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with other use cases
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        command_repository: CompanyLeaveCommandRepository,
        query_repository: CompanyLeaveQueryRepository,
        event_publisher: EventPublisher
    ):
        self._command_repository = command_repository
        self._query_repository = query_repository
        self._event_publisher = event_publisher
    
    async def execute(self, request: CreateCompanyLeaveRequestDTO) -> CompanyLeaveResponseDTO:
        """
        Execute company leave creation workflow.
        
        Business Rules:
        1. All required fields must be provided
        2. Annual allocation must be valid
        3. Events must be published for downstream processing
        
        Args:
            request: Company leave creation request
            
        Returns:
            CompanyLeaveResponseDTO with created company leave details
            
        Raises:
            CompanyLeaveDTOValidationError: If request data is invalid
            ValueError: If business rules are violated
            Exception: If creation fails
        """
        
        try:
            # Step 1: Validate request data
            logger.info(f"Creating company leave with accrual type: {request.accrual_type}")
            validation_errors = request.validate()
            if validation_errors:
                raise CompanyLeaveDTOValidationError(validation_errors)
            
            # Step 2: Check business rules
            self._validate_business_rules(request)
            
            # Step 3: Create company leave entity
            company_leave = CompanyLeave.create_new_company_leave(
                leave_type=request.leave_type,
                leave_name=request.leave_name,
                accrual_type=request.accrual_type,
                annual_allocation=request.annual_allocation,
                created_by=request.created_by,
                description=request.description,
                encashable=request.encashable,
                is_allowed_on_probation=request.is_allowed_on_probation
            )
            
            # Step 4: Persist to database
            success = await self._command_repository.save(company_leave)
            if not success:
                raise Exception("Failed to save company leave to database")
            
            # Step 5: Publish domain events
            await self._publish_domain_events(company_leave)
            
            # Step 6: Return response
            response = CompanyLeaveResponseDTO.from_entity(company_leave)
            logger.info(f"Successfully created company leave: {company_leave.company_leave_id}")
            
            return response
            
        except CompanyLeaveDTOValidationError:
            logger.warning(f"Validation failed for company leave creation: {request.accrual_type}")
            raise
        except ValueError as e:
            logger.error(f"Business rule violation in company leave creation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to create company leave: {str(e)}")
            raise Exception(f"Company leave creation failed: {str(e)}")
    
    def _validate_business_rules(self, request: CreateCompanyLeaveRequestDTO):
        """Validate business rules for company leave creation"""
        
        # Validate allocation limits
        if request.annual_allocation > 365:
            raise ValueError("Annual allocation cannot exceed 365 days")
        
        # Validate accrual type
        valid_accrual_types = ['monthly', 'quarterly', 'annually', 'immediate']
        if request.accrual_type not in valid_accrual_types:
            raise ValueError(f"Invalid accrual type. Must be one of: {', '.join(valid_accrual_types)}")
    
    async def _publish_domain_events(self, company_leave: CompanyLeave):
        """Publish domain events for company leave creation"""
        try:
            # TODO: Implement proper domain event creation and publishing
            # For now, just log the event instead of publishing
            logger.info(f"Would publish company_leave_created event for {company_leave.company_leave_id}")
            logger.debug(f"Event data: leave_type={company_leave.leave_type}, created_by={company_leave.created_by}")
            
        except Exception as e:
            logger.warning(f"Failed to publish events for company leave {company_leave.company_leave_id}: {e}")


class CreateCompanyLeaveUseCaseError(Exception):
    """Base exception for create company leave use case"""
    pass


class CompanyLeaveAlreadyExistsError(CreateCompanyLeaveUseCaseError):
    """Exception raised when company leave already exists"""
    
    def __init__(self, accrual_type: str):
        self.accrual_type = accrual_type
        super().__init__(f"Company leave with accrual type '{accrual_type}' already exists")


class InvalidLeaveConfigurationError(CreateCompanyLeaveUseCaseError):
    """Exception raised when leave configuration is invalid"""
    
    def __init__(self, field: str, value: str, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {field} '{value}': {reason}") 