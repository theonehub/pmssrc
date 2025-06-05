"""
Update Company Leave Use Case
Business workflow for updating existing company leave policies
"""

import logging
from typing import Optional
from datetime import datetime

from app.application.dto.company_leave_dto import (
    UpdateCompanyLeaveRequestDTO, 
    CompanyLeaveResponseDTO,
    CompanyLeaveDTOValidationError,
    CompanyLeaveNotFoundError
)
from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.domain.entities.company_leave import CompanyLeave


logger = logging.getLogger(__name__)


class UpdateCompanyLeaveUseCase:
    """
    Use case for updating company leave policies.
    
    Follows SOLID principles:
    - SRP: Only handles company leave update workflow
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with other use cases
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        command_repository,
        query_repository: CompanyLeaveQueryRepository,
        event_publisher: EventPublisher
    ):
        self._command_repository = command_repository
        self._query_repository = query_repository
        self._event_publisher = event_publisher
    
    async def execute(
        self, 
        company_leave_id: str, 
        request: UpdateCompanyLeaveRequestDTO, 
        updated_by: str
    ) -> CompanyLeaveResponseDTO:
        """
        Execute company leave update workflow.
        
        Business Rules:
        1. Company leave must exist
        2. All required fields must be provided
        3. Annual allocation must be valid
        4. Events must be published for downstream processing
        
        Args:
            company_leave_id: ID of company leave to update
            request: Company leave update request
            updated_by: User performing the update
            
        Returns:
            CompanyLeaveResponseDTO with updated company leave details
            
        Raises:
            CompanyLeaveNotFoundError: If company leave doesn't exist
            CompanyLeaveDTOValidationError: If request data is invalid
            ValueError: If business rules are violated
            Exception: If update fails
        """
        
        try:
            # Step 1: Validate request data
            logger.info(f"Updating company leave: {company_leave_id} by {updated_by}")
            validation_errors = request.validate()
            if validation_errors:
                raise CompanyLeaveDTOValidationError(validation_errors)
            
            # Step 2: Get existing company leave
            company_leave = await self._query_repository.get_by_id(company_leave_id)
            if not company_leave:
                raise CompanyLeaveNotFoundError(f"Company leave {company_leave_id} not found")
            
            # Step 3: Check business rules
            self._validate_business_rules(request)
            
            # Step 4: Update company leave entity
            if request.accrual_type is not None:
                company_leave.accrual_type = request.accrual_type
            
            if request.annual_allocation is not None:
                company_leave.annual_allocation = request.annual_allocation
                company_leave.computed_monthly_allocation = request.annual_allocation / 12
            
            if request.description is not None:
                company_leave.description = request.description
            
            if request.is_active is not None:
                company_leave.is_active = request.is_active
                
            if request.encashable is not None:
                company_leave.encashable = request.encashable
                
            if request.is_allowed_on_probation is not None:
                company_leave.is_allowed_on_probation = request.is_allowed_on_probation
            
            company_leave.updated_at = datetime.now()
            company_leave.updated_by = updated_by
            
            # Step 5: Persist to database
            success = await self._command_repository.update(company_leave)
            if not success:
                raise Exception("Failed to update company leave in database")
            
            # Step 6: Publish domain events
            await self._publish_domain_events(company_leave, updated_by)
            
            # Step 7: Return response
            response = CompanyLeaveResponseDTO.from_entity(company_leave)
            logger.info(f"Successfully updated company leave: {company_leave.company_leave_id}")
            
            return response
            
        except CompanyLeaveNotFoundError:
            logger.warning(f"Company leave not found for update: {company_leave_id}")
            raise
        except CompanyLeaveDTOValidationError:
            logger.warning(f"Validation failed for company leave update: {company_leave_id}")
            raise
        except ValueError as e:
            logger.error(f"Business rule violation in company leave update: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to update company leave: {str(e)}")
            raise Exception(f"Company leave update failed: {str(e)}")
    
    def _validate_business_rules(self, request: UpdateCompanyLeaveRequestDTO):
        """Validate business rules for company leave update"""
        
        # Validate allocation limits
        if request.annual_allocation is not None and request.annual_allocation > 365:
            raise ValueError("Annual allocation cannot exceed 365 days")
        
        # Validate accrual type
        if request.accrual_type is not None:
            valid_accrual_types = ['monthly', 'quarterly', 'annually', 'immediate']
            if request.accrual_type not in valid_accrual_types:
                raise ValueError(f"Invalid accrual type. Must be one of: {', '.join(valid_accrual_types)}")
    
    async def _publish_domain_events(self, company_leave: CompanyLeave, updated_by: str):
        """Publish domain events for company leave update"""
        try:
            event_data = {
                'company_leave_id': company_leave.company_leave_id,
                'accrual_type': company_leave.accrual_type,
                'annual_allocation': company_leave.annual_allocation,
                'updated_by': updated_by,
                'updated_at': company_leave.updated_at.isoformat()
            }
            
            await self._event_publisher.publish('company_leave_updated', event_data)
            logger.debug(f"Published company_leave_updated event for {company_leave.company_leave_id}")
            
        except Exception as e:
            logger.warning(f"Failed to publish events for company leave {company_leave.company_leave_id}: {e}")


class UpdateCompanyLeaveUseCaseError(Exception):
    """Base exception for update company leave use case"""
    pass