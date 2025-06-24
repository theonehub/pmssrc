"""
Use case for getting taxation record by employee ID.
Handles fetching detailed taxation records for a specific employee and tax year.
"""

from typing import Optional
from datetime import datetime
import logging

from app.application.dto.taxation_dto import TaxationRecordSummaryDTO
from app.domain.repositories.taxation_repository import TaxationRepository
from app.domain.value_objects.employee_id import EmployeeId
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class GetTaxationRecordByEmployeeUseCase:
    """
    Use case for retrieving taxation record by employee ID.
    
    This use case:
    1. Validates the employee ID and tax year
    2. Fetches the taxation record from repository
    3. Converts domain entity to DTO for API response
    4. Handles cases where no record exists
    """
    
    def __init__(self, taxation_repository: TaxationRepository):
        self._taxation_repository = taxation_repository
    
    async def execute(
        self,
        employee_id: str,
        organization_id: str,
        tax_year: Optional[str] = None
    ) -> TaxationRecordSummaryDTO:
        """
        Execute the use case to get taxation record by employee ID.
        
        Args:
            employee_id: Employee ID to fetch record for
            organization_id: Organization ID for context
            tax_year: Optional tax year filter (e.g., "2024-25")
            
        Returns:
            TaxationRecordSummaryDTO: Taxation record summary
            
        Raises:
            ValueError: If employee_id is invalid
            Exception: If record not found or other errors occur
        """
        
        logger.info(f"Getting taxation record for employee {employee_id}, tax_year: {tax_year}")
        
        # Validate inputs
        if not employee_id or not employee_id.strip():
            raise ValueError("Employee ID is required")
        
        if not organization_id or not organization_id.strip():
            raise ValueError("Organization ID is required")
        
        try:
            # Determine financial year
            financial_year = self._get_financial_year(tax_year)
            
            # Get taxation record from repository
            taxation_record = await self._taxation_repository.get_taxation_record(
                employee_id=employee_id,
                financial_year=financial_year,
                organisation_id=organization_id
            )
            
            if taxation_record:
                # Convert domain entity to DTO
                return self._convert_to_dto(taxation_record, organization_id)
            else:
                # Return default/empty record if not found
                return self._create_default_record(employee_id, organization_id, tax_year or self._get_current_tax_year())
                
        except Exception as e:
            logger.error(f"Error getting taxation record for employee {employee_id}: {str(e)}")
            raise
    
    def _get_financial_year(self, tax_year: Optional[str]) -> int:
        """
        Convert tax year string to financial year integer.
        
        Args:
            tax_year: Tax year string (e.g., "2024-25") or None
            
        Returns:
            int: Financial year (e.g., 2024)
        """
        if tax_year:
            # Extract year from "2024-25" format
            return int(tax_year.split('-')[0])
        else:
            # Use current financial year
            from datetime import date
            current_year = date.today().year
            current_month = date.today().month
            # Financial year starts from April 1st
            if current_month >= 4:
                return current_year
            else:
                return current_year - 1
    
    def _get_current_tax_year(self) -> str:
        """
        Get current tax year in string format.
        
        Returns:
            str: Current tax year (e.g., "2024-25")
        """
        from datetime import date
        current_year = date.today().year
        current_month = date.today().month
        # Tax year starts from April 1st
        if current_month >= 4:
            return f"{current_year}-{str(current_year + 1)[2:]}"
        else:
            return f"{current_year - 1}-{str(current_year)[2:]}"
    
    def _convert_to_dto(self, taxation_record, organization_id: str) -> TaxationRecordSummaryDTO:
        """
        Convert domain entity to DTO.
        
        Args:
            taxation_record: Domain taxation record entity
            organization_id: Organization ID
            
        Returns:
            TaxationRecordSummaryDTO: DTO for API response
        """
        from decimal import Decimal
        
        # Extract basic information
        tax_year = f"{taxation_record.financial_year}-{str(taxation_record.financial_year + 1)[2:]}"
        
        # Get regime information
        regime = "new"  # Default
        if hasattr(taxation_record, 'regime') and taxation_record.regime:
            if hasattr(taxation_record.regime, 'regime_type'):
                regime = taxation_record.regime.regime_type.value.lower()
            elif hasattr(taxation_record.regime, 'value'):
                regime = taxation_record.regime.value.lower()
        
        # Calculate financial values
        gross_income = Decimal("0")
        taxable_income = Decimal("0")
        total_tax_liability = Decimal("0")
        monthly_tax = Decimal("0")
        
        # Extract income information if available
        if hasattr(taxation_record, 'salary_income') and taxation_record.salary_income:
            if hasattr(taxation_record.salary_income, 'get_total_salary'):
                gross_income = Decimal(str(taxation_record.salary_income.get_total_salary().to_float()))
            elif hasattr(taxation_record.salary_income, 'total_salary'):
                gross_income = Decimal(str(taxation_record.salary_income.total_salary))
        
        # Extract tax calculation if available
        if hasattr(taxation_record, 'calculation_result') and taxation_record.calculation_result:
            if hasattr(taxation_record.calculation_result, 'total_tax_liability'):
                total_tax_liability = Decimal(str(taxation_record.calculation_result.total_tax_liability.to_float()))
                monthly_tax = total_tax_liability / 12
            if hasattr(taxation_record.calculation_result, 'taxable_income'):
                taxable_income = Decimal(str(taxation_record.calculation_result.taxable_income.to_float()))
        
        # Calculate effective tax rate
        effective_tax_rate = "0.0%"
        if gross_income > 0:
            rate = (total_tax_liability / gross_income) * 100
            effective_tax_rate = f"{rate:.1f}%"
        
        # Get timestamps
        created_at = getattr(taxation_record, 'created_at', datetime.utcnow())
        updated_at = getattr(taxation_record, 'updated_at', datetime.utcnow())
        last_calculated = getattr(taxation_record, 'last_calculated_at', datetime.utcnow())
        
        return TaxationRecordSummaryDTO(
            taxation_id=getattr(taxation_record, 'taxation_id', f"tax_{taxation_record.employee_id}_{taxation_record.financial_year}"),
            employee_id=taxation_record.employee_id,
            organization_id=organization_id,
            tax_year=tax_year,
            regime=regime,
            age=getattr(taxation_record, 'age', 30),
            is_final=getattr(taxation_record, 'is_final', False),
            status="draft" if not getattr(taxation_record, 'is_final', False) else "final",
            gross_income=gross_income,
            taxable_income=taxable_income,
            total_tax_liability=total_tax_liability,
            monthly_tax=monthly_tax,
            effective_tax_rate=effective_tax_rate,
            last_calculated=last_calculated,
            created_at=created_at,
            updated_at=updated_at
        )
    
    def _create_default_record(self, employee_id: str, organization_id: str, tax_year: str) -> TaxationRecordSummaryDTO:
        """
        Create a default/empty record when no taxation record exists.
        
        Args:
            employee_id: Employee ID
            organization_id: Organization ID
            tax_year: Tax year
            
        Returns:
            TaxationRecordSummaryDTO: Default record
        """
        from decimal import Decimal
        
        return TaxationRecordSummaryDTO(
            taxation_id=f"tax_{employee_id}_{tax_year.replace('-', '_')}",
            employee_id=employee_id,
            organization_id=organization_id,
            tax_year=tax_year,
            regime="new",
            age=30,
            is_final=False,
            status="not_started",
            gross_income=Decimal("0"),
            taxable_income=Decimal("0"),
            total_tax_liability=Decimal("0"),
            monthly_tax=Decimal("0"),
            effective_tax_rate="0.0%",
            last_calculated=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ) 