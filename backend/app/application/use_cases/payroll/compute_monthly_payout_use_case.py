"""
Compute Monthly Payout Use Case
Handles monthly payout computation with LWP integration
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from app.domain.entities.taxation.monthly_payout import MonthlyPayoutRecord, MonthlyPayoutStatus
from app.domain.entities.taxation.monthly_payroll import LWPDetails
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime
from app.application.interfaces.repositories.user_repository import UserQueryRepository
from app.application.interfaces.repositories.taxation_repository import TaxationRepository
from app.application.dto.payroll_dto import MonthlyPayoutRequestDTO, MonthlyPayoutResponseDTO, BulkPayoutRequestDTO
from app.application.interfaces.repositories.monthly_payout_repository import MonthlyPayoutRepository

logger = logging.getLogger(__name__)


class ComputeMonthlyPayoutUseCase:
    """
    Use case for computing monthly payouts with LWP integration.
    
    Handles:
    - Individual employee monthly payout computation
    - Bulk monthly payout computation for multiple employees
    - LWP integration and adjustment calculations
    - Tax liability integration
    - Payout storage and status management
    """
    
    def __init__(
        self,
        user_query_repository: UserQueryRepository,
        taxation_query_repository: TaxationRepository,
        monthly_payout_repository: MonthlyPayoutRepository
    ):
        self._user_repository = user_query_repository
        self._taxation_repository = taxation_query_repository
        self._payout_repository = monthly_payout_repository
    
    async def compute_employee_monthly_payout(
        self,
        request: MonthlyPayoutRequestDTO,
        organization_id: str
    ) -> MonthlyPayoutResponseDTO:
        """
        Compute monthly payout for a single employee.
        
        Args:
            request: Monthly payout request
            organization_id: Organization ID
            
        Returns:
            Monthly payout response with calculated amounts
        """
        try:
            logger.info(f"Computing monthly payout for employee {request.employee_id} for {request.month}/{request.year}")
            
            # Get employee data
            employee = await self._user_repository.get_by_employee_id(
                EmployeeId(request.employee_id), 
                organization_id
            )
            
            if not employee:
                raise ValueError(f"Employee {request.employee_id} not found")
            
            # Get or create salary income
            salary_income = await self._get_employee_salary_income(
                request.employee_id, 
                organization_id,
                request.year
            )
            
            # Get tax regime and liability
            tax_regime, annual_tax_liability = await self._get_tax_information(
                request.employee_id,
                organization_id,
                request.year
            )
            
            # Create LWP details
            lwp_details = LWPDetails(
                lwp_days=request.lwp_days,
                total_working_days=request.total_working_days,
                month=request.month,
                year=request.year
            )
            
            # Create monthly payout record
            payout_record = MonthlyPayoutRecord(
                employee_id=EmployeeId(request.employee_id),
                organization_id=organization_id,
                month=request.month,
                year=request.year,
                base_salary_income=salary_income,
                lwp_details=lwp_details,
                tax_regime=tax_regime,
                annual_tax_liability=annual_tax_liability
            )
            
            # Add additional deductions if provided
            if request.advance_deduction or request.loan_deduction or request.other_deductions:
                payout_record.update_additional_deductions(
                    advance=Money(Decimal(str(request.advance_deduction))) if request.advance_deduction else None,
                    loan=Money(Decimal(str(request.loan_deduction))) if request.loan_deduction else None,
                    other=Money(Decimal(str(request.other_deductions))) if request.other_deductions else None
                )
            
            # Set status based on request
            if request.auto_approve:
                payout_record.status = MonthlyPayoutStatus.APPROVED
            else:
                payout_record.status = MonthlyPayoutStatus.CALCULATED
            
            # Save payout record
            saved_record = await self._payout_repository.create_monthly_payout(
                payout_record, 
                organization_id
            )
            
            # Convert to response DTO
            response = self._convert_to_response_dto(saved_record, employee)
            
            logger.info(f"Monthly payout computed successfully for employee {request.employee_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error computing monthly payout for employee {request.employee_id}: {e}")
            raise
    
    async def compute_bulk_monthly_payouts(
        self,
        request: BulkPayoutRequestDTO,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Compute monthly payouts for multiple employees.
        
        Args:
            request: Bulk payout request
            organization_id: Organization ID
            
        Returns:
            Bulk computation results
        """
        try:
            logger.info(f"Computing bulk monthly payouts for {len(request.employee_ids)} employees for {request.month}/{request.year}")
            
            results = {
                "successful_payouts": [],
                "failed_payouts": [],
                "summary": {
                    "total_employees": len(request.employee_ids),
                    "successful_count": 0,
                    "failed_count": 0,
                    "total_gross_amount": 0.0,
                    "total_net_amount": 0.0,
                    "total_lwp_deduction": 0.0
                }
            }
            
            for employee_id in request.employee_ids:
                try:
                    # Get employee-specific LWP details
                    employee_lwp = request.employee_lwp_details.get(employee_id, {})
                    
                    # Create individual request
                    individual_request = MonthlyPayoutRequestDTO(
                        employee_id=employee_id,
                        month=request.month,
                        year=request.year,
                        lwp_days=employee_lwp.get("lwp_days", 0),
                        total_working_days=employee_lwp.get("total_working_days", 30),
                        advance_deduction=employee_lwp.get("advance_deduction", 0.0),
                        loan_deduction=employee_lwp.get("loan_deduction", 0.0),
                        other_deductions=employee_lwp.get("other_deductions", 0.0),
                        auto_approve=request.auto_approve
                    )
                    
                    # Compute individual payout
                    payout_response = await self.compute_employee_monthly_payout(
                        individual_request,
                        organization_id
                    )
                    
                    results["successful_payouts"].append(payout_response)
                    results["summary"]["successful_count"] += 1
                    results["summary"]["total_gross_amount"] += payout_response.adjusted_monthly_gross
                    results["summary"]["total_net_amount"] += payout_response.monthly_net_salary
                    results["summary"]["total_lwp_deduction"] += payout_response.lwp_deduction_amount
                    
                except Exception as e:
                    logger.error(f"Failed to compute payout for employee {employee_id}: {e}")
                    results["failed_payouts"].append({
                        "employee_id": employee_id,
                        "error": str(e)
                    })
                    results["summary"]["failed_count"] += 1
            
            logger.info(f"Bulk payout computation completed: {results['summary']['successful_count']} successful, {results['summary']['failed_count']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk payout computation: {e}")
            raise
    
    async def get_employee_monthly_payout(
        self,
        employee_id: str,
        month: int,
        year: int,
        organization_id: str
    ) -> Optional[MonthlyPayoutResponseDTO]:
        """
        Get existing monthly payout for an employee.
        
        Args:
            employee_id: Employee ID
            month: Month (1-12)
            year: Year
            organization_id: Organization ID
            
        Returns:
            Monthly payout response if found
        """
        try:
            payout_record = await self._payout_repository.get_monthly_payout(
                employee_id, month, year, organization_id
            )
            
            if not payout_record:
                return None
            
            # Get employee data for response
            employee = await self._user_repository.get_by_employee_id(
                EmployeeId(employee_id), 
                organization_id
            )
            
            return self._convert_to_response_dto(payout_record, employee)
            
        except Exception as e:
            logger.error(f"Error getting monthly payout for employee {employee_id}: {e}")
            raise
    
    async def get_monthly_payouts_summary(
        self,
        month: int,
        year: int,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get summary of all monthly payouts for a given month.
        
        Args:
            month: Month (1-12)
            year: Year
            organization_id: Organization ID
            
        Returns:
            Monthly payouts summary
        """
        try:
            payouts = await self._payout_repository.get_monthly_payouts_by_period(
                month, year, organization_id
            )
            
            summary = {
                "month": month,
                "year": year,
                "total_employees": len(payouts),
                "total_gross_amount": 0.0,
                "total_net_amount": 0.0,
                "total_lwp_deduction": 0.0,
                "status_breakdown": {},
                "payouts": []
            }
            
            for payout in payouts:
                # Get employee data
                employee = await self._user_repository.get_by_employee_id(
                    EmployeeId(payout.employee_id), 
                    organization_id
                )
                
                payout_dto = self._convert_to_response_dto(payout, employee)
                summary["payouts"].append(payout_dto)
                
                # Update totals
                summary["total_gross_amount"] += payout_dto.adjusted_monthly_gross
                summary["total_net_amount"] += payout_dto.monthly_net_salary
                summary["total_lwp_deduction"] += payout_dto.lwp_deduction_amount
                
                # Update status breakdown
                status = payout_dto.status
                summary["status_breakdown"][status] = summary["status_breakdown"].get(status, 0) + 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting monthly payouts summary for {month}/{year}: {e}")
            raise
    
    async def approve_monthly_payout(
        self,
        employee_id: str,
        month: int,
        year: int,
        organization_id: str,
        approved_by: str
    ) -> MonthlyPayoutResponseDTO:
        """
        Approve a monthly payout.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            organization_id: Organization ID
            approved_by: User ID who approved
            
        Returns:
            Updated payout response
        """
        try:
            payout_record = await self._payout_repository.get_monthly_payout(
                employee_id, month, year, organization_id
            )
            
            if not payout_record:
                raise ValueError(f"Payout not found for employee {employee_id} for {month}/{year}")
            
            payout_record.approve_payout(approved_by)
            
            updated_record = await self._payout_repository.update_monthly_payout(
                payout_record, organization_id
            )
            
            # Get employee data for response
            employee = await self._user_repository.get_by_employee_id(
                EmployeeId(employee_id), 
                organization_id
            )
            
            return self._convert_to_response_dto(updated_record, employee)
            
        except Exception as e:
            logger.error(f"Error approving monthly payout for employee {employee_id}: {e}")
            raise
    
    async def process_monthly_payout(
        self,
        employee_id: str,
        month: int,
        year: int,
        organization_id: str,
        processed_by: str
    ) -> MonthlyPayoutResponseDTO:
        """
        Process a monthly payout.
        
        Args:
            employee_id: Employee ID
            month: Month
            year: Year
            organization_id: Organization ID
            processed_by: User ID who processed
            
        Returns:
            Updated payout response
        """
        try:
            payout_record = await self._payout_repository.get_monthly_payout(
                employee_id, month, year, organization_id
            )
            
            if not payout_record:
                raise ValueError(f"Payout not found for employee {employee_id} for {month}/{year}")
            
            payout_record.process_payout(processed_by)
            
            updated_record = await self._payout_repository.update_monthly_payout(
                payout_record, organization_id
            )
            
            # Get employee data for response
            employee = await self._user_repository.get_by_employee_id(
                EmployeeId(employee_id), 
                organization_id
            )
            
            return self._convert_to_response_dto(updated_record, employee)
            
        except Exception as e:
            logger.error(f"Error processing monthly payout for employee {employee_id}: {e}")
            raise
    
    async def _get_employee_salary_income(
        self, 
        employee_id: str, 
        organization_id: str,
        year: int
    ) -> SalaryIncome:
        """Get employee salary income for the year."""
        try:
            # Try to get from taxation record first
            taxation_record = await self._taxation_repository.get_by_employee_and_year(
                employee_id, str(year), organization_id
            )
            
            if taxation_record and taxation_record.salary_income:
                return taxation_record.salary_income
            
            # Fallback: get from user entity
            employee = await self._user_repository.get_by_employee_id(
                EmployeeId(employee_id), 
                organization_id
            )
            
            if not employee or not hasattr(employee, 'salary_details'):
                raise ValueError(f"No salary information found for employee {employee_id}")
            
            # Convert employee salary details to SalaryIncome entity
            salary_details = employee.salary_details
            return SalaryIncome(
                basic_salary=Money(Decimal(str(salary_details.get('basic_salary', 0)))),
                dearness_allowance=Money(Decimal(str(salary_details.get('da', 0)))),
                hra_received=Money(Decimal(str(salary_details.get('hra', 0)))),
                special_allowance=Money(Decimal(str(salary_details.get('special_allowance', 0)))),
                conveyance_allowance=Money(Decimal(str(salary_details.get('transport_allowance', 0)))),
                medical_allowance=Money(Decimal(str(salary_details.get('medical_allowance', 0)))),
                bonus=Money(Decimal(str(salary_details.get('bonus', 0)))),
                commission=Money(Decimal(str(salary_details.get('commission', 0)))),
                other_allowances=Money(Decimal(str(salary_details.get('other_allowances', 0))))
            )
            
        except Exception as e:
            logger.error(f"Error getting salary income for employee {employee_id}: {e}")
            raise
    
    async def _get_tax_information(
        self, 
        employee_id: str, 
        organization_id: str,
        year: int
    ) -> tuple[TaxRegime, Money]:
        """Get tax regime and annual tax liability."""
        try:
            # Try to get from taxation record
            taxation_record = await self._taxation_repository.get_by_employee_and_year(
                employee_id, str(year), organization_id
            )
            
            if taxation_record:
                tax_liability = Money.zero()
                if taxation_record.calculation_result:
                    tax_liability = taxation_record.calculation_result.total_tax_liability
                
                return taxation_record.regime, tax_liability
            
            # Default to new regime with zero tax liability
            return TaxRegime.new_regime(), Money.zero()
            
        except Exception as e:
            logger.error(f"Error getting tax information for employee {employee_id}: {e}")
            # Return defaults
            return TaxRegime.new_regime(), Money.zero()
    
    def _convert_to_response_dto(
        self, 
        payout_record: MonthlyPayoutRecord, 
        employee: Optional[Any]
    ) -> MonthlyPayoutResponseDTO:
        """Convert payout record to response DTO."""
        salary_breakdown = payout_record.get_salary_breakdown()
        lwp_impact = payout_record.get_lwp_impact_summary()
        
        return MonthlyPayoutResponseDTO(
            payout_id=payout_record.payout_id,
            employee_id=str(payout_record.employee_id),
            employee_name=employee.name if employee else "Unknown",
            organization_id=payout_record.organization_id,
            month=payout_record.month,
            year=payout_record.year,
            
            # Salary components
            basic_salary=salary_breakdown["earnings"]["basic_salary"],
            dearness_allowance=salary_breakdown["earnings"]["dearness_allowance"],
            hra=salary_breakdown["earnings"]["hra"],
            special_allowance=salary_breakdown["earnings"]["special_allowance"],
            transport_allowance=salary_breakdown["earnings"]["transport_allowance"],
            medical_allowance=salary_breakdown["earnings"]["medical_allowance"],
            bonus=salary_breakdown["earnings"]["bonus"],
            commission=salary_breakdown["earnings"]["commission"],
            other_allowances=salary_breakdown["earnings"]["other_allowances"],
            
            # Deductions
            epf_employee=salary_breakdown["deductions"]["epf_employee"],
            esi_employee=salary_breakdown["deductions"]["esi_employee"],
            professional_tax=salary_breakdown["deductions"]["professional_tax"],
            tds=salary_breakdown["deductions"]["tds"],
            advance_deduction=salary_breakdown["deductions"]["advance_deduction"],
            loan_deduction=salary_breakdown["deductions"]["loan_deduction"],
            other_deductions=salary_breakdown["deductions"]["other_deductions"],
            
            # Totals
            base_monthly_gross=lwp_impact["base_monthly_gross"],
            adjusted_monthly_gross=salary_breakdown["earnings"]["total_earnings"],
            total_deductions=salary_breakdown["deductions"]["total_deductions"],
            monthly_net_salary=salary_breakdown["net_salary"],
            
            # LWP details
            lwp_days=lwp_impact["lwp_days"],
            effective_working_days=lwp_impact["effective_working_days"],
            lwp_factor=lwp_impact["lwp_factor"],
            lwp_deduction_amount=lwp_impact["lwp_deduction_amount"],
            
            # Tax information
            tax_regime=payout_record.tax_regime.regime_type.value,
            annual_tax_liability=payout_record.annual_tax_liability.to_float(),
            tax_exemptions=payout_record.tax_exemptions.to_float(),
            
            # Status and metadata
            status=payout_record.status.value,
            calculation_date=payout_record.calculation_date.isoformat(),
            processed_date=payout_record.processed_date.isoformat() if payout_record.processed_date else None,
            approved_by=payout_record.approved_by,
            processed_by=payout_record.processed_by,
            notes=payout_record.notes
        ) 