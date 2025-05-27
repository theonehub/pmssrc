"""
SOLID-Compliant Employee Salary Controller
Handles HTTP requests for employee salary operations
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from app.application.dto.employee_salary_dto import (
    EmployeeSalaryCreateRequestDTO, EmployeeSalaryUpdateRequestDTO,
    BulkEmployeeSalaryAssignRequestDTO, SalaryStructureQueryRequestDTO,
    SalaryCalculationRequestDTO, EmployeeSalaryResponseDTO, SalaryStructureResponseDTO,
    SalaryAssignmentStatusResponseDTO, BulkSalaryAssignmentResponseDTO,
    SalaryCalculationResponseDTO, SalaryHistoryResponseDTO, SalaryComponentSummaryResponseDTO,
    SalaryAuditResponseDTO, EmployeeSalaryErrorResponseDTO
)

logger = logging.getLogger(__name__)


class EmployeeSalaryController:
    """
    SOLID-compliant controller for employee salary operations.
    
    Responsibilities:
    - Handle HTTP request/response mapping for salary operations
    - Validate input data
    - Coordinate with salary business services
    - Return standardized responses
    """
    
    def __init__(self):
        """Initialize employee salary controller."""
        pass
    
    async def health_check(self) -> Dict[str, str]:
        """Health check endpoint for employee salary service."""
        return {
            "service": "employee_salary_service", 
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    
    async def create_employee_salary(
        self,
        request: EmployeeSalaryCreateRequestDTO,
        hostname: str
    ) -> EmployeeSalaryResponseDTO:
        """
        Create a single salary component entry for an employee.
        
        Args:
            request: Employee salary creation request
            hostname: Organization hostname
            
        Returns:
            Created salary component response
        """
        try:
            logger.info(f"Creating salary component {request.component_id} for employee {request.employee_id}")
            
            # For now, return a mock response
            # In real implementation, this would call the service layer
            salary_id = f"SAL_{request.employee_id}_{request.component_id}_{int(datetime.now().timestamp())}"
            
            return EmployeeSalaryResponseDTO(
                salary_id=salary_id,
                employee_id=request.employee_id,
                component_id=request.component_id,
                amount=request.amount,
                percentage=request.percentage,
                is_fixed=request.is_fixed,
                effective_from=request.effective_from,
                effective_to=request.effective_to,
                frequency=request.frequency,
                is_active=request.is_active,
                notes=request.notes,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error creating employee salary: {e}")
            raise
    
    async def get_employee_salary_by_id(
        self,
        employee_id: str,
        hostname: str
    ) -> List[EmployeeSalaryResponseDTO]:
        """
        Get all salary components assigned to a specific employee.
        
        Args:
            employee_id: Employee ID
            hostname: Organization hostname
            
        Returns:
            List of employee salary components
        """
        try:
            logger.info(f"Getting salary components for employee {employee_id}")
            
            # For now, return mock data
            # In real implementation, this would call the service layer
            return [
                EmployeeSalaryResponseDTO(
                    salary_id=f"SAL_{employee_id}_BASIC",
                    employee_id=employee_id,
                    component_id="BASIC_SALARY",
                    component_name="Basic Salary",
                    amount=50000.00,
                    percentage=None,
                    is_fixed=True,
                    effective_from=date(2024, 1, 1),
                    effective_to=None,
                    frequency="monthly",
                    is_active=True,
                    notes="Basic salary component",
                    created_at=datetime.now()
                )
            ]
            
        except Exception as e:
            logger.error(f"Error getting employee salary components: {e}")
            raise
    
    async def update_employee_salary(
        self,
        salary_id: str,
        request: EmployeeSalaryUpdateRequestDTO,
        hostname: str
    ) -> EmployeeSalaryResponseDTO:
        """
        Update an employee's salary component details.
        
        Args:
            salary_id: Salary component ID to update
            request: Update request data
            hostname: Organization hostname
            
        Returns:
            Updated salary component response
        """
        try:
            logger.info(f"Updating salary component {salary_id}")
            
            # For now, return mock response
            # In real implementation, this would call the service layer
            return EmployeeSalaryResponseDTO(
                salary_id=salary_id,
                employee_id="EMP001",  # Would come from database
                component_id="BASIC_SALARY",
                amount=request.amount or 50000.00,
                percentage=request.percentage,
                is_fixed=request.is_fixed if request.is_fixed is not None else True,
                effective_from=request.effective_from or date.today(),
                effective_to=request.effective_to,
                frequency=request.frequency or "monthly",
                is_active=request.is_active if request.is_active is not None else True,
                notes=request.notes,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error updating employee salary: {e}")
            raise
    
    async def delete_employee_salary(
        self,
        salary_id: str,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Delete an employee's salary component entry.
        
        Args:
            salary_id: Salary component ID to delete
            hostname: Organization hostname
            
        Returns:
            Deletion confirmation
        """
        try:
            logger.info(f"Deleting salary component {salary_id}")
            
            # For now, return success message
            # In real implementation, this would call the service layer
            return {
                "message": "Salary component deleted successfully",
                "salary_id": salary_id,
                "deleted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error deleting employee salary: {e}")
            raise
    
    async def check_salary_assignment_status(
        self,
        employee_id: str,
        hostname: str
    ) -> SalaryAssignmentStatusResponseDTO:
        """
        Check if salary components are already assigned to the employee.
        
        Args:
            employee_id: Employee ID
            hostname: Organization hostname
            
        Returns:
            Salary assignment status
        """
        try:
            logger.info(f"Checking salary assignment status for employee {employee_id}")
            
            # Get assigned components (mock data)
            assigned_components = await self.get_employee_salary_by_id(employee_id, hostname)
            
            # Calculate statistics
            is_assigned = len(assigned_components) > 0
            active_components = len([c for c in assigned_components if c.is_active])
            last_assignment = max(
                (c.created_at for c in assigned_components), 
                default=None
            )
            
            return SalaryAssignmentStatusResponseDTO(
                employee_id=employee_id,
                is_assigned=is_assigned,
                total_components=len(assigned_components),
                active_components=active_components,
                assigned_components=assigned_components,
                last_assignment_date=last_assignment
            )
            
        except Exception as e:
            logger.error(f"Error checking salary assignment status: {e}")
            raise
    
    async def assign_salary_structure(
        self,
        request: BulkEmployeeSalaryAssignRequestDTO,
        hostname: str
    ) -> BulkSalaryAssignmentResponseDTO:
        """
        Bulk assign salary components to an employee (insert or update).
        
        Args:
            request: Bulk salary assignment request
            hostname: Organization hostname
            
        Returns:
            Bulk assignment response
        """
        try:
            logger.info(f"Assigning salary structure to employee {request.employee_id} with {len(request.components)} components")
            
            start_time = datetime.now()
            
            # For now, assume all assignments are successful
            # In real implementation, this would handle partial failures
            operation_id = f"BULK_SAL_{request.employee_id}_{int(start_time.timestamp())}"
            
            return BulkSalaryAssignmentResponseDTO(
                employee_id=request.employee_id,
                operation_id=operation_id,
                total_components=len(request.components),
                successful_assignments=len(request.components),
                failed_assignments=0,
                successful_components=[comp.component_id for comp in request.components],
                failed_components=[],
                operation_status="completed",
                processed_at=start_time
            )
            
        except Exception as e:
            logger.error(f"Error assigning salary structure: {e}")
            raise
    
    async def get_salary_structure(
        self,
        employee_id: str,
        hostname: str,
        as_of_date: Optional[date] = None
    ) -> SalaryStructureResponseDTO:
        """
        Get full salary structure assigned to an employee.
        
        Args:
            employee_id: Employee ID
            hostname: Organization hostname
            as_of_date: Date for structure calculation (optional)
            
        Returns:
            Salary structure response
        """
        try:
            logger.info(f"Getting salary structure for employee {employee_id}")
            
            # Get salary components (mock data)
            component_responses = await self.get_employee_salary_by_id(employee_id, hostname)
            
            # Calculate totals (simplified calculation)
            total_earnings = sum(
                comp.amount for comp in component_responses 
                if comp.is_active and comp.amount > 0
            )
            total_deductions = sum(
                abs(comp.amount) for comp in component_responses 
                if comp.is_active and comp.amount < 0
            )
            net_salary = total_earnings - total_deductions
            
            # Get structure effective date
            structure_effective_from = min(
                (comp.effective_from for comp in component_responses),
                default=date.today()
            )
            
            # Get last updated date
            last_updated = max(
                (comp.updated_at for comp in component_responses if comp.updated_at),
                default=None
            )
            
            return SalaryStructureResponseDTO(
                employee_id=employee_id,
                total_earnings=total_earnings,
                total_deductions=total_deductions,
                net_salary=net_salary,
                components=component_responses,
                structure_effective_from=structure_effective_from,
                last_updated=last_updated
            )
            
        except Exception as e:
            logger.error(f"Error getting salary structure: {e}")
            raise
    
    async def get_salary_structure_with_names(
        self,
        employee_id: str,
        hostname: str
    ) -> List[EmployeeSalaryResponseDTO]:
        """
        View-only endpoint for salary structure (with component names).
        
        Args:
            employee_id: Employee ID
            hostname: Organization hostname
            
        Returns:
            List of salary components with names
        """
        try:
            logger.info(f"Getting salary structure with names for employee {employee_id}")
            
            # For now, return the same as regular structure
            # In real implementation, this would include component names from lookup tables
            return await self.get_employee_salary_by_id(employee_id, hostname)
            
        except Exception as e:
            logger.error(f"Error getting salary structure with names: {e}")
            raise
    
    async def calculate_salary(
        self,
        request: SalaryCalculationRequestDTO,
        hostname: str
    ) -> SalaryCalculationResponseDTO:
        """
        Calculate salary for an employee on a specific date.
        
        Args:
            request: Salary calculation request
            hostname: Organization hostname
            
        Returns:
            Salary calculation response
        """
        try:
            logger.info(f"Calculating salary for employee {request.employee_id} on {request.calculation_date}")
            
            # For now, return mock calculation
            # In real implementation, this would perform actual calculations
            earnings_breakdown = {"BASIC_SALARY": 50000.00, "HRA": 15000.00}
            deductions_breakdown = {"PF": 6000.00, "TAX": 5000.00}
            employer_contributions = {"PF_EMPLOYER": 6000.00, "ESI_EMPLOYER": 750.00}
            
            gross_salary = sum(earnings_breakdown.values())
            total_deductions = sum(deductions_breakdown.values())
            net_salary = gross_salary - total_deductions
            
            return SalaryCalculationResponseDTO(
                employee_id=request.employee_id,
                calculation_date=request.calculation_date,
                gross_salary=gross_salary,
                total_deductions=total_deductions,
                net_salary=net_salary,
                earnings_breakdown=earnings_breakdown,
                deductions_breakdown=deductions_breakdown,
                employer_contributions=employer_contributions,
                calculated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error calculating salary: {e}")
            raise
