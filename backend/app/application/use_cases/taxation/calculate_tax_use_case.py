"""
Calculate Tax Use Case
Handles tax calculation business workflow
"""

from typing import Optional, Dict, Any
import logging
from datetime import datetime

from domain.entities.employee import Employee
from domain.entities.taxation import Taxation
from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.money import Money
from domain.value_objects.tax_regime import TaxRegime
from domain.domain_services.tax_calculator import TaxCalculatorFactory, TaxOptimizationService

from application.interfaces.repositories.employee_repository import EmployeeQueryRepository
from application.interfaces.repositories.taxation_repository import (
    TaxationCommandRepository, TaxationQueryRepository
)
from application.interfaces.services.email_service import EmailService
from application.interfaces.services.event_publisher import EventPublisher
from application.dto.taxation_dto import TaxCalculationRequestDTO, TaxCalculationResponseDTO


class CalculateTaxUseCase:
    """
    Use case for calculating employee tax.
    
    Follows SOLID principles:
    - SRP: Only handles tax calculation workflow
    - OCP: Can be extended without modification
    - LSP: Can be substituted with other tax calculation implementations
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        employee_query_repo: EmployeeQueryRepository,
        taxation_command_repo: TaxationCommandRepository,
        taxation_query_repo: TaxationQueryRepository,
        email_service: EmailService,
        event_publisher: EventPublisher,
        tax_calculator_factory: TaxCalculatorFactory
    ):
        self.employee_query_repo = employee_query_repo
        self.taxation_command_repo = taxation_command_repo
        self.taxation_query_repo = taxation_query_repo
        self.email_service = email_service
        self.event_publisher = event_publisher
        self.tax_calculator_factory = tax_calculator_factory
        self.logger = logging.getLogger(__name__)
    
    def execute(self, request: TaxCalculationRequestDTO) -> TaxCalculationResponseDTO:
        """
        Execute tax calculation workflow.
        
        Business Rules:
        1. Employee must exist and be active
        2. Tax year must be valid
        3. Salary information must be available
        4. Tax regime must be specified
        5. Deductions must be validated
        """
        
        try:
            self.logger.info(f"Starting tax calculation for employee {request.employee_id} for year {request.tax_year}")
            
            # Step 1: Validate and get employee
            employee = self._get_and_validate_employee(request.employee_id)
            
            # Step 2: Get or create taxation record
            taxation = self._get_or_create_taxation_record(
                employee, request.tax_year, request.regime, request.gross_annual_salary
            )
            
            # Step 3: Update deductions
            self._update_deductions(taxation, request.deductions)
            
            # Step 4: Calculate tax
            total_tax_liability = taxation.calculate_tax()
            
            # Step 5: Save taxation record
            self.taxation_command_repo.save(taxation)
            
            # Step 6: Publish domain events
            self._publish_domain_events(taxation)
            
            # Step 7: Send notification email
            if request.send_notification:
                self._send_tax_calculation_notification(employee, taxation)
            
            # Step 8: Generate optimization suggestions if requested
            optimization_suggestions = []
            if request.include_optimization_suggestions:
                optimization_suggestions = self._generate_optimization_suggestions(
                    employee, taxation
                )
            
            self.logger.info(f"Tax calculation completed for employee {request.employee_id}")
            
            return TaxCalculationResponseDTO(
                employee_id=request.employee_id,
                tax_year=request.tax_year,
                regime=taxation.regime,
                gross_annual_salary=taxation.gross_annual_salary,
                taxable_income=taxation.taxable_income,
                calculated_tax=taxation.calculated_tax,
                surcharge_amount=taxation.surcharge_amount,
                cess_amount=taxation.cess_amount,
                rebate_87a=taxation.rebate_87a,
                total_tax_liability=taxation.total_tax_liability,
                effective_tax_rate=taxation.get_effective_tax_rate(),
                deductions=taxation.deductions,
                optimization_suggestions=optimization_suggestions,
                calculated_at=taxation.calculated_at
            )
            
        except Exception as e:
            self.logger.error(f"Tax calculation failed for employee {request.employee_id}: {str(e)}")
            raise TaxCalculationError(f"Tax calculation failed: {str(e)}") from e
    
    def _get_and_validate_employee(self, employee_id: str) -> Employee:
        """Get and validate employee"""
        
        emp_id = EmployeeId.from_string(employee_id)
        employee = self.employee_query_repo.get_by_id(emp_id)
        
        if not employee:
            raise EmployeeNotFoundError(f"Employee with ID {employee_id} not found")
        
        if not employee.is_active():
            raise InactiveEmployeeError(f"Employee {employee_id} is not active")
        
        return employee
    
    def _get_or_create_taxation_record(
        self, 
        employee: Employee, 
        tax_year: str, 
        regime: TaxRegime,
        gross_annual_salary: Money
    ) -> Taxation:
        """Get existing taxation record or create new one"""
        
        # Try to get existing record
        existing_taxation = self.taxation_query_repo.get_by_employee_and_year(
            employee.employee_id, tax_year
        )
        
        if existing_taxation:
            # Update existing record if needed
            if existing_taxation.regime != regime:
                existing_taxation.change_regime(regime, "User requested regime change")
            
            # Update salary if different
            if existing_taxation.gross_annual_salary != gross_annual_salary:
                existing_taxation.gross_annual_salary = gross_annual_salary
                existing_taxation.updated_at = datetime.utcnow()
            
            return existing_taxation
        else:
            # Create new taxation record
            return Taxation.create_new_taxation(
                employee_id=employee.employee_id,
                tax_year=tax_year,
                regime=regime,
                gross_annual_salary=gross_annual_salary,
                basic_salary=employee.salary_details.basic_salary,
                hra=employee.salary_details.hra
            )
    
    def _update_deductions(self, taxation: Taxation, deductions: Dict[str, float]):
        """Update tax deductions"""
        
        # Remove existing deductions not in the new list
        existing_sections = set(taxation.deductions.keys())
        new_sections = set(deductions.keys())
        
        for section in existing_sections - new_sections:
            taxation.remove_deduction(section)
        
        # Add or update deductions
        for section, amount in deductions.items():
            if amount > 0:
                money_amount = Money.from_float(amount)
                taxation.add_deduction(section, money_amount)
    
    def _publish_domain_events(self, taxation: Taxation):
        """Publish domain events"""
        
        events = taxation.get_domain_events()
        for event in events:
            try:
                self.event_publisher.publish(event)
            except Exception as e:
                self.logger.warning(f"Failed to publish event {event.get_event_type()}: {str(e)}")
        
        taxation.clear_domain_events()
    
    def _send_tax_calculation_notification(self, employee: Employee, taxation: Taxation):
        """Send tax calculation notification email"""
        
        try:
            self.email_service.send_tax_calculation_notification(
                to_email=employee.contact_info.email,
                employee_name=employee.get_full_name(),
                tax_year=taxation.tax_year,
                total_tax_liability=float(taxation.total_tax_liability.amount),
                regime=str(taxation.regime)
            )
        except Exception as e:
            self.logger.warning(f"Failed to send tax calculation notification: {str(e)}")
    
    def _generate_optimization_suggestions(
        self, 
        employee: Employee, 
        taxation: Taxation
    ) -> list:
        """Generate tax optimization suggestions"""
        
        try:
            tax_calculator = self.tax_calculator_factory.create_calculator()
            optimization_service = TaxOptimizationService(tax_calculator)
            
            suggestions = optimization_service.suggest_optimizations(
                current_income=taxation.gross_annual_salary,
                current_deductions=taxation.deductions,
                regime=taxation.regime,
                employee_age=employee.get_age()
            )
            
            # Convert Money objects to float for DTO
            serialized_suggestions = []
            for suggestion in suggestions:
                serialized_suggestion = {}
                for key, value in suggestion.items():
                    if isinstance(value, Money):
                        serialized_suggestion[key] = float(value.amount)
                    else:
                        serialized_suggestion[key] = value
                serialized_suggestions.append(serialized_suggestion)
            
            return serialized_suggestions
            
        except Exception as e:
            self.logger.warning(f"Failed to generate optimization suggestions: {str(e)}")
            return []


class CompareTaxRegimesUseCase:
    """
    Use case for comparing tax liability under different regimes.
    """
    
    def __init__(
        self,
        employee_query_repo: EmployeeQueryRepository,
        tax_calculator_factory: TaxCalculatorFactory
    ):
        self.employee_query_repo = employee_query_repo
        self.tax_calculator_factory = tax_calculator_factory
        self.logger = logging.getLogger(__name__)
    
    def execute(
        self, 
        employee_id: str, 
        gross_annual_salary: float,
        deductions: Dict[str, float]
    ) -> Dict[str, Any]:
        """Compare tax liability under both regimes"""
        
        try:
            # Get employee for age information
            emp_id = EmployeeId.from_string(employee_id)
            employee = self.employee_query_repo.get_by_id(emp_id)
            
            if not employee:
                raise EmployeeNotFoundError(f"Employee with ID {employee_id} not found")
            
            # Create tax calculator and optimization service
            tax_calculator = self.tax_calculator_factory.create_calculator()
            optimization_service = TaxOptimizationService(tax_calculator)
            
            # Convert inputs
            income = Money.from_float(gross_annual_salary)
            deduction_money = {k: Money.from_float(v) for k, v in deductions.items()}
            
            # Compare regimes
            comparison = optimization_service.compare_regimes(
                income=income,
                deductions=deduction_money,
                employee_age=employee.get_age()
            )
            
            # Convert Money objects to float for response
            def convert_money_dict(d):
                result = {}
                for key, value in d.items():
                    if isinstance(value, Money):
                        result[key] = float(value.amount)
                    elif isinstance(value, dict):
                        result[key] = convert_money_dict(value)
                    else:
                        result[key] = str(value) if hasattr(value, '__str__') else value
                return result
            
            return {
                'old_regime': convert_money_dict(comparison['old_regime']),
                'new_regime': convert_money_dict(comparison['new_regime']),
                'recommendation': comparison['recommendation']
            }
            
        except Exception as e:
            self.logger.error(f"Tax regime comparison failed: {str(e)}")
            raise TaxCalculationError(f"Tax regime comparison failed: {str(e)}") from e


# Custom Exceptions
class TaxCalculationError(Exception):
    """Base exception for tax calculation operations"""
    pass


class EmployeeNotFoundError(TaxCalculationError):
    """Exception raised when employee is not found"""
    pass


class InactiveEmployeeError(TaxCalculationError):
    """Exception raised when employee is inactive"""
    pass


class InvalidTaxYearError(TaxCalculationError):
    """Exception raised when tax year is invalid"""
    pass


class InvalidDeductionError(TaxCalculationError):
    """Exception raised when deduction is invalid"""
    pass 