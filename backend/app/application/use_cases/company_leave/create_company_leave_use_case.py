"""
Create Company Leave Use Case
Business workflow for creating new company leave policies
"""

import logging
from typing import Optional
from datetime import datetime

from app.application.dto.company_leave_dto import (
    CompanyLeaveCreateRequestDTO, 
    CompanyLeaveResponseDTO,
    CompanyLeaveDTOValidationError
)
from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveCommandRepository,
    CompanyLeaveQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.email_service import EmailService
from app.domain.entities.company_leave import CompanyLeave
from app.domain.value_objects.leave_type import LeaveType, LeaveCategory, AccrualType
from app.domain.value_objects.leave_policy import LeavePolicy
from decimal import Decimal


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
        event_publisher: EventPublisher,
        email_service: Optional[EmailService] = None
    ):
        self._command_repository = command_repository
        self._query_repository = query_repository
        self._event_publisher = event_publisher
        self._email_service = email_service
        self._logger = logging.getLogger(__name__)
    
    def execute(self, request: CompanyLeaveCreateRequestDTO) -> CompanyLeaveResponseDTO:
        """
        Execute company leave creation workflow.
        
        Business Rules:
        1. Leave type code must be unique
        2. All required fields must be provided
        3. Policy configuration must be valid
        4. Events must be published for downstream processing
        
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
            self._logger.info(f"Creating company leave for type: {request.leave_type_code}")
            validation_errors = request.validate()
            if validation_errors:
                raise CompanyLeaveDTOValidationError(validation_errors)
            
            # Step 2: Check business rules
            self._validate_business_rules(request)
            
            # Step 3: Create domain objects
            leave_type = self._create_leave_type(request)
            leave_policy = self._create_leave_policy(request, leave_type)
            
            # Step 4: Create company leave entity
            company_leave = CompanyLeave.create_new_company_leave(
                leave_type=leave_type,
                policy=leave_policy,
                created_by=request.created_by,
                description=request.description,
                effective_from=self._parse_effective_from(request.effective_from)
            )
            
            # Step 5: Persist to database
            success = self._command_repository.save(company_leave)
            if not success:
                raise Exception("Failed to save company leave to database")
            
            # Step 6: Publish domain events
            self._publish_domain_events(company_leave)
            
            # Step 7: Send notifications (if email service available)
            if self._email_service:
                self._send_creation_notifications(company_leave)
            
            # Step 8: Return response
            response = CompanyLeaveResponseDTO.from_entity(company_leave)
            self._logger.info(f"Successfully created company leave: {company_leave.company_leave_id}")
            
            return response
            
        except CompanyLeaveDTOValidationError:
            self._logger.warning(f"Validation failed for company leave creation: {request.leave_type_code}")
            raise
        except ValueError as e:
            self._logger.error(f"Business rule violation in company leave creation: {str(e)}")
            raise
        except Exception as e:
            self._logger.error(f"Failed to create company leave: {str(e)}")
            raise Exception(f"Company leave creation failed: {str(e)}")
    
    def _validate_business_rules(self, request: CompanyLeaveCreateRequestDTO):
        """Validate business rules for company leave creation"""
        
        # Check if leave type code already exists
        if self._query_repository.exists_by_leave_type_code(request.leave_type_code):
            raise ValueError(f"Leave type code '{request.leave_type_code}' already exists")
        
        # Validate leave type code format
        if not self._is_valid_leave_type_code(request.leave_type_code):
            raise ValueError(f"Invalid leave type code format: {request.leave_type_code}")
        
        # Validate allocation limits
        if request.annual_allocation > 365:
            raise ValueError("Annual allocation cannot exceed 365 days")
        
        # Validate carryover rules
        if request.max_carryover_days and request.max_carryover_days > request.annual_allocation:
            raise ValueError("Max carryover days cannot exceed annual allocation")
        
        # Validate encashment rules
        if request.is_encashable and request.max_encashment_days:
            if request.max_encashment_days > request.annual_allocation:
                raise ValueError("Max encashment days cannot exceed annual allocation")
    
    def _create_leave_type(self, request: CompanyLeaveCreateRequestDTO) -> LeaveType:
        """Create LeaveType value object from request"""
        
        try:
            category = LeaveCategory(request.leave_category.lower())
        except ValueError:
            raise ValueError(f"Invalid leave category: {request.leave_category}")
        
        return LeaveType(
            code=request.leave_type_code.upper(),
            name=request.leave_type_name,
            category=category,
            description=request.description
        )
    
    def _create_leave_policy(
        self, 
        request: CompanyLeaveCreateRequestDTO, 
        leave_type: LeaveType
    ) -> LeavePolicy:
        """Create LeavePolicy value object from request"""
        
        try:
            accrual_type = AccrualType(request.accrual_type.lower())
        except ValueError:
            raise ValueError(f"Invalid accrual type: {request.accrual_type}")
        
        # Calculate accrual rate based on type
        accrual_rate = None
        if accrual_type == AccrualType.MONTHLY:
            accrual_rate = Decimal(str(request.annual_allocation / 12))
        elif accrual_type == AccrualType.QUARTERLY:
            accrual_rate = Decimal(str(request.annual_allocation / 4))
        
        return LeavePolicy(
            leave_type=leave_type,
            annual_allocation=request.annual_allocation,
            accrual_type=accrual_type,
            accrual_rate=accrual_rate,
            max_carryover_days=request.max_carryover_days or 0,
            min_advance_notice_days=request.min_advance_notice_days or 0,
            max_continuous_days=request.max_continuous_days,
            requires_approval=request.requires_approval,
            auto_approve_threshold=request.auto_approve_threshold,
            requires_medical_certificate=request.requires_medical_certificate,
            medical_certificate_threshold=request.medical_certificate_threshold,
            is_encashable=request.is_encashable,
            max_encashment_days=request.max_encashment_days or 0,
            available_during_probation=request.available_during_probation,
            probation_allocation=request.probation_allocation,
            gender_specific=request.gender_specific
        )
    
    def _parse_effective_from(self, effective_from_str: Optional[str]) -> Optional[datetime]:
        """Parse effective from date string"""
        if not effective_from_str:
            return None
        
        try:
            return datetime.fromisoformat(effective_from_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                return datetime.strptime(effective_from_str, '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"Invalid effective from date format: {effective_from_str}")
    
    def _publish_domain_events(self, company_leave: CompanyLeave):
        """Publish domain events for company leave creation"""
        
        try:
            events = company_leave.get_domain_events()
            for event in events:
                self._event_publisher.publish(event)
            
            # Clear events after publishing
            company_leave.clear_domain_events()
            
            self._logger.info(f"Published {len(events)} domain events for company leave: {company_leave.company_leave_id}")
            
        except Exception as e:
            self._logger.error(f"Failed to publish domain events: {str(e)}")
            # Don't fail the entire operation for event publishing failures
    
    def _send_creation_notifications(self, company_leave: CompanyLeave):
        """Send email notifications for company leave creation"""
        
        try:
            if self._email_service:
                # Send notification to HR team
                self._email_service.send_company_leave_created_notification(
                    leave_type_name=company_leave.leave_type.name,
                    annual_allocation=company_leave.policy.annual_allocation,
                    created_by=company_leave.created_by or "System"
                )
                
                self._logger.info(f"Sent creation notification for company leave: {company_leave.company_leave_id}")
                
        except Exception as e:
            self._logger.error(f"Failed to send creation notifications: {str(e)}")
            # Don't fail the entire operation for notification failures
    
    def _is_valid_leave_type_code(self, code: str) -> bool:
        """Validate leave type code format"""
        if not code or len(code) > 10:
            return False
        
        # Allow alphanumeric characters, underscores, and hyphens
        return code.replace('_', '').replace('-', '').isalnum()


class CreateCompanyLeaveUseCaseError(Exception):
    """Base exception for create company leave use case"""
    pass


class CompanyLeaveAlreadyExistsError(CreateCompanyLeaveUseCaseError):
    """Exception raised when company leave already exists"""
    
    def __init__(self, leave_type_code: str):
        self.leave_type_code = leave_type_code
        super().__init__(f"Company leave with type code '{leave_type_code}' already exists")


class InvalidLeaveConfigurationError(CreateCompanyLeaveUseCaseError):
    """Exception raised when leave configuration is invalid"""
    
    def __init__(self, field: str, value: str, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {field} '{value}': {reason}") 