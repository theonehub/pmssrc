"""
Create Taxation Use Case
Handles taxation record creation business logic
"""

import logging
from typing import Optional
from datetime import datetime, date

from app.application.dto.taxation_dto import (
    TaxationCreateRequestDTO,
    TaxationResponseDTO,
    TaxationValidationError,
    TaxationBusinessRuleError
)
from app.application.interfaces.repositories.taxation_repository import (
    TaxationCommandRepository,
    TaxationQueryRepository
)
from app.application.interfaces.services.notification_service import NotificationService
from app.domain.events.taxation_events import TaxationCalculated
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money


logger = logging.getLogger(__name__)


class CreateTaxationUseCase:
    """
    Use case for creating new taxation records.
    
    Follows SOLID principles:
    - SRP: Only handles taxation creation logic
    - OCP: Can be extended with new creation methods
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for taxation creation
    - DIP: Depends on repository abstractions
    """
    
    def __init__(
        self,
        command_repository: TaxationCommandRepository,
        query_repository: TaxationQueryRepository,
        notification_service: NotificationService
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.notification_service = notification_service
    
    async def execute(
        self,
        request: TaxationCreateRequestDTO,
        hostname: str
    ) -> TaxationResponseDTO:
        """
        Execute taxation record creation.
        
        Args:
            request: Taxation creation request
            hostname: Organization hostname
            
        Returns:
            Created taxation response
            
        Raises:
            TaxationValidationError: If validation fails
            TaxationBusinessRuleError: If business rules are violated
        """
        try:
            logger.info(f"Creating taxation record for employee: {request.employee_id}")
            
            # Validate request
            await self._validate_creation_request(request, hostname)
            
            # Check business rules
            await self._validate_business_rules(request, hostname)
            
            # Create taxation record
            taxation_response = await self.command_repository.create_taxation(
                request,
                hostname
            )
            
            # Send welcome notification
            await self._send_creation_notification(taxation_response)
            
            logger.info(f"Taxation record created successfully for employee: {request.employee_id}")
            return taxation_response
            
        except (TaxationValidationError, TaxationBusinessRuleError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating taxation for {request.employee_id}: {e}")
            raise TaxationBusinessRuleError(
                f"Failed to create taxation record: {str(e)}"
            )
    
    async def create_default_taxation(
        self,
        employee_id: str,
        emp_age: int,
        is_govt_employee: bool,
        hostname: str,
        created_by: str
    ) -> TaxationResponseDTO:
        """
        Create default taxation record for new employee.
        
        Args:
            employee_id: Employee identifier
            emp_age: Employee age
            is_govt_employee: Whether employee is government employee
            hostname: Organization hostname
            created_by: User creating the record
            
        Returns:
            Created taxation response
        """
        try:
            logger.info(f"Creating default taxation record for employee: {employee_id}")
            
            # Get current tax year
            current_tax_year = self._get_current_tax_year()
            
            # Create default request
            default_request = TaxationCreateRequestDTO(
                employee_id=employee_id,
                tax_year=current_tax_year,
                regime="old",  # Default to old regime
                emp_age=emp_age,
                is_govt_employee=is_govt_employee,
                created_by=created_by
            )
            
            # Create the taxation record
            return await self.execute(default_request, hostname)
            
        except Exception as e:
            logger.error(f"Error creating default taxation for {employee_id}: {e}")
            raise TaxationBusinessRuleError(
                f"Failed to create default taxation record: {str(e)}"
            )
    
    async def _validate_creation_request(
        self,
        request: TaxationCreateRequestDTO,
        hostname: str
    ):
        """Validate taxation creation request"""
        
        # Basic validation
        validation_errors = request.validate()
        if validation_errors:
            raise TaxationValidationError(
                "request",
                str(request),
                f"Validation failed: {', '.join(validation_errors)}"
            )
        
        # Tax year format validation
        if not self._is_valid_tax_year_format(request.tax_year):
            raise TaxationValidationError(
                "tax_year",
                request.tax_year,
                "Invalid tax year format. Expected format: YYYY-YYYY"
            )
        
        # Age validation
        if request.emp_age < 18 or request.emp_age > 100:
            raise TaxationValidationError(
                "emp_age",
                request.emp_age,
                "Employee age must be between 18 and 100"
            )
        
        logger.info(f"Taxation creation request validation passed for {request.employee_id}")
    
    async def _validate_business_rules(
        self,
        request: TaxationCreateRequestDTO,
        hostname: str
    ):
        """Validate business rules for taxation creation"""
        
        # Check if taxation record already exists for this employee and tax year
        existing_taxation = await self.query_repository.exists_taxation(
            request.employee_id,
            request.tax_year,
            hostname
        )
        
        if existing_taxation:
            raise TaxationBusinessRuleError(
                f"Taxation record already exists for employee {request.employee_id} "
                f"for tax year {request.tax_year}",
                {
                    "employee_id": request.employee_id,
                    "tax_year": request.tax_year,
                    "rule": "unique_taxation_per_year"
                }
            )
        
        # Validate tax year is not in the future
        current_tax_year = self._get_current_tax_year()
        if request.tax_year > current_tax_year:
            raise TaxationBusinessRuleError(
                f"Cannot create taxation record for future tax year {request.tax_year}",
                {
                    "tax_year": request.tax_year,
                    "current_year": current_tax_year,
                    "rule": "no_future_tax_year"
                }
            )
        
        # Validate salary components if provided
        if request.salary:
            await self._validate_salary_components(request.salary)
        
        # Validate deductions if provided
        if request.deductions:
            await self._validate_deduction_components(request.deductions)
        
        logger.info(f"Business rules validation passed for {request.employee_id}")
    
    async def _validate_salary_components(self, salary):
        """Validate salary components"""
        
        # Basic salary cannot be negative
        if salary.basic < 0:
            raise TaxationValidationError(
                "salary.basic",
                salary.basic,
                "Basic salary cannot be negative"
            )
        
        # HRA cannot be more than basic salary in most cases
        if salary.hra > salary.basic * 1.5:
            raise TaxationValidationError(
                "salary.hra",
                salary.hra,
                "HRA seems unusually high compared to basic salary"
            )
        
        # Special allowance should be reasonable
        if salary.special_allowance < 0:
            raise TaxationValidationError(
                "salary.special_allowance",
                salary.special_allowance,
                "Special allowance cannot be negative"
            )
    
    async def _validate_deduction_components(self, deductions):
        """Validate deduction components"""
        
        # Section 80C limit validation (Rs. 1.5 lakh)
        if deductions.section_80c > 150000:
            raise TaxationValidationError(
                "deductions.section_80c",
                deductions.section_80c,
                "Section 80C deduction cannot exceed Rs. 1.5 lakh"
            )
        
        # Section 80D limit validation (varies by age)
        max_80d = 75000  # For senior citizens with parents
        if deductions.section_80d > max_80d:
            raise TaxationValidationError(
                "deductions.section_80d",
                deductions.section_80d,
                f"Section 80D deduction cannot exceed Rs. {max_80d:,}"
            )
        
        # All deductions must be non-negative
        deduction_fields = [
            ("section_80c", deductions.section_80c),
            ("section_80d", deductions.section_80d),
            ("section_80e", deductions.section_80e),
            ("section_80g", deductions.section_80g),
            ("section_80ccd", deductions.section_80ccd),
            ("other_deductions", deductions.other_deductions)
        ]
        
        for field_name, value in deduction_fields:
            if value < 0:
                raise TaxationValidationError(
                    f"deductions.{field_name}",
                    value,
                    f"{field_name} deduction cannot be negative"
                )
    
    def _is_valid_tax_year_format(self, tax_year: str) -> bool:
        """Validate tax year format (YYYY-YYYY)"""
        try:
            parts = tax_year.split('-')
            if len(parts) != 2:
                return False
            
            start_year = int(parts[0])
            end_year = int(parts[1])
            
            # End year should be start year + 1
            if end_year != start_year + 1:
                return False
            
            # Years should be reasonable (not too far in past or future)
            current_year = date.today().year
            if start_year < current_year - 10 or start_year > current_year + 1:
                return False
            
            return True
        except:
            return False
    
    def _get_current_tax_year(self) -> str:
        """Get current tax year in Indian format"""
        current_date = date.today()
        if current_date.month >= 4:  # April onwards
            return f"{current_date.year}-{current_date.year + 1}"
        else:  # January to March
            return f"{current_date.year - 1}-{current_date.year}"
    
    async def _send_creation_notification(self, taxation: TaxationResponseDTO):
        """Send notification about taxation record creation"""
        try:
            # This would be implemented with actual notification logic
            logger.info(f"Sending taxation creation notification for {taxation.employee_id}")
            
            # Example notification (would be implemented properly)
            # await self.notification_service.send_system_notification(
            #     recipient_email=employee_email,
            #     subject="Tax Information Record Created",
            #     message=f"Your tax information record for {taxation.tax_year} has been created."
            # )
            
        except Exception as e:
            logger.warning(f"Failed to send creation notification: {e}")


class BulkCreateTaxationUseCase:
    """
    Use case for bulk creation of taxation records.
    """
    
    def __init__(
        self,
        create_use_case: CreateTaxationUseCase
    ):
        self.create_use_case = create_use_case
    
    async def execute(
        self,
        employee_ids: list[str],
        tax_year: str,
        hostname: str,
        created_by: str
    ) -> dict:
        """
        Create taxation records for multiple employees.
        
        Args:
            employee_ids: List of employee identifiers
            tax_year: Tax year for records
            hostname: Organization hostname
            created_by: User creating the records
            
        Returns:
            Dictionary with creation results
        """
        results = {
            "successful": [],
            "failed": [],
            "total": len(employee_ids)
        }
        
        logger.info(f"Starting bulk taxation creation for {len(employee_ids)} employees")
        
        for employee_id in employee_ids:
            try:
                # Create default taxation record
                taxation = await self.create_use_case.create_default_taxation(
                    employee_id=employee_id,
                    emp_age=30,  # Default age, would be retrieved from employee record
                    is_govt_employee=False,  # Default, would be retrieved from organization
                    hostname=hostname,
                    created_by=created_by
                )
                
                results["successful"].append({
                    "employee_id": employee_id,
                    "taxation_id": taxation.taxation_id
                })
                
            except Exception as e:
                logger.error(f"Failed to create taxation for {employee_id}: {e}")
                results["failed"].append({
                    "employee_id": employee_id,
                    "error": str(e)
                })
        
        logger.info(f"Bulk taxation creation completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
        return results 