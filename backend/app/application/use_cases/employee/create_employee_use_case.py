"""
Create Employee Use Case
Application service for creating new employees
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from app.domain.entities.employee import Employee, EmployeeType
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money
from app.application.interfaces.repositories.employee_repository import (
    EmployeeRepository, 
    EmployeeQueryRepository,
    EmployeeAlreadyExistsError
)
from app.application.dto.employee_dto import CreateEmployeeRequest, CreateEmployeeResponse
from app.application.interfaces.services.email_service import EmailService
from app.application.interfaces.services.event_publisher import EventPublisher


@dataclass
class CreateEmployeeUseCase:
    """
    Use case for creating new employees.
    
    Follows SOLID principles:
    - SRP: Only handles employee creation workflow
    - OCP: Can be extended without modification
    - LSP: Can be substituted with other employee creation implementations
    - ISP: Depends only on interfaces it needs
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    employee_repository: EmployeeRepository
    employee_query_repository: EmployeeQueryRepository
    email_service: EmailService
    event_publisher: EventPublisher
    
    def execute(self, request: CreateEmployeeRequest) -> CreateEmployeeResponse:
        """
        Execute the create employee use case.
        
        Args:
            request: The create employee request
            
        Returns:
            CreateEmployeeResponse with the created employee details
            
        Raises:
            EmployeeAlreadyExistsError: If employee already exists
            ValueError: If request data is invalid
        """
        
        # 1. Validate request
        self._validate_request(request)
        
        # 2. Check if employee already exists
        employee_id = EmployeeId.from_string(request.employee_id)
        if self.employee_repository.exists(employee_id):
            raise EmployeeAlreadyExistsError(employee_id)
        
        # 3. Check if email is already in use
        existing_employee = self.employee_query_repository.find_by_email(request.email)
        if existing_employee:
            raise ValueError(f"Email {request.email} is already in use by employee {existing_employee.id}")
        
        # 4. Create employee entity
        employee = self._create_employee_entity(request)
        
        # 5. Save employee
        self.employee_repository.save(employee)
        
        # 6. Publish domain events
        self._publish_domain_events(employee)
        
        # 7. Send welcome email (async)
        self._send_welcome_email(employee)
        
        # 8. Return response
        return self._create_response(employee)
    
    def _validate_request(self, request: CreateEmployeeRequest) -> None:
        """Validate the create employee request"""
        
        if not request.employee_id:
            raise ValueError("Employee ID is required")
        
        if not request.first_name or not request.first_name.strip():
            raise ValueError("First name is required")
        
        if not request.last_name or not request.last_name.strip():
            raise ValueError("Last name is required")
        
        if not request.email or '@' not in request.email:
            raise ValueError("Valid email is required")
        
        if not request.date_of_joining:
            raise ValueError("Date of joining is required")
        
        if not request.date_of_birth:
            raise ValueError("Date of birth is required")
        
        if request.date_of_birth >= date.today():
            raise ValueError("Date of birth must be in the past")
        
        if request.date_of_joining > date.today():
            raise ValueError("Date of joining cannot be in the future")
        
        # Validate age (minimum 18 years at joining)
        joining_age = request.date_of_joining.year - request.date_of_birth.year - (
            (request.date_of_joining.month, request.date_of_joining.day) < 
            (request.date_of_birth.month, request.date_of_birth.day)
        )
        
        if joining_age < 18:
            raise ValueError("Employee must be at least 18 years old at joining")
        
        if request.initial_salary and request.initial_salary <= 0:
            raise ValueError("Initial salary must be positive")
    
    def _create_employee_entity(self, request: CreateEmployeeRequest) -> Employee:
        """Create employee entity from request"""
        
        employee_id = EmployeeId.from_string(request.employee_id)
        initial_salary = Money.from_float(request.initial_salary) if request.initial_salary else Money.zero()
        employee_type = EmployeeType(request.employee_type) if request.employee_type else EmployeeType.PERMANENT
        
        employee = Employee.create_new_employee(
            employee_id=employee_id,
            first_name=request.first_name.strip(),
            last_name=request.last_name.strip(),
            email=request.email.lower().strip(),
            date_of_joining=request.date_of_joining,
            date_of_birth=request.date_of_birth,
            initial_salary=initial_salary,
            employee_type=employee_type,
            department=request.department,
            designation=request.designation
        )
        
        # Set optional fields
        if request.phone:
            employee.phone = request.phone.strip()
        
        if request.address:
            employee.address = request.address
        
        if request.emergency_contact:
            employee.emergency_contact = request.emergency_contact
        
        if request.manager_id:
            manager_id = EmployeeId.from_string(request.manager_id)
            # Validate manager exists
            if not self.employee_repository.exists(manager_id):
                raise ValueError(f"Manager with ID {manager_id} does not exist")
            employee.assign_manager(manager_id)
        
        return employee
    
    def _publish_domain_events(self, employee: Employee) -> None:
        """Publish domain events from the employee entity"""
        
        events = employee.get_domain_events()
        for event in events:
            self.event_publisher.publish(event)
        
        employee.clear_domain_events()
    
    def _send_welcome_email(self, employee: Employee) -> None:
        """Send welcome email to new employee"""
        
        try:
            self.email_service.send_welcome_email(
                to_email=employee.email,
                employee_name=employee.get_full_name(),
                employee_id=str(employee.id),
                date_of_joining=employee.date_of_joining
            )
        except Exception as e:
            # Log error but don't fail the use case
            # In a real system, you might want to queue this for retry
            print(f"Failed to send welcome email to {employee.email}: {e}")
    
    def _create_response(self, employee: Employee) -> CreateEmployeeResponse:
        """Create response from employee entity"""
        
        return CreateEmployeeResponse(
            employee_id=str(employee.id),
            full_name=employee.get_full_name(),
            email=employee.email,
            department=employee.department,
            designation=employee.designation,
            date_of_joining=employee.date_of_joining,
            employee_type=employee.employee_type.value,
            status=employee.status.value,
            current_salary=employee.current_salary.to_float(),
            created_at=employee.created_at
        )


class CreateEmployeeUseCaseError(Exception):
    """Base exception for create employee use case"""
    pass


class InvalidEmployeeDataError(CreateEmployeeUseCaseError):
    """Exception raised when employee data is invalid"""
    pass


class ManagerNotFoundError(CreateEmployeeUseCaseError):
    """Exception raised when specified manager is not found"""
    
    def __init__(self, manager_id: str):
        self.manager_id = manager_id
        super().__init__(f"Manager not found: {manager_id}")


class EmailAlreadyInUseError(CreateEmployeeUseCaseError):
    """Exception raised when email is already in use"""
    
    def __init__(self, email: str, existing_employee_id: str):
        self.email = email
        self.existing_employee_id = existing_employee_id
        super().__init__(f"Email {email} is already in use by employee {existing_employee_id}") 