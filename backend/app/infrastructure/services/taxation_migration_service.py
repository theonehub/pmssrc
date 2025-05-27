"""
Taxation Migration Service
Bridges legacy taxation service with SOLID architecture
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from application.dto.taxation_dto import (
    TaxationResponseDTO,
    TaxProjectionDTO,
    TaxComparisonDTO,
    TaxStatisticsDTO,
    TaxBreakdownDTO
)
from application.interfaces.repositories.taxation_repository import (
    TaxationCalculationRepository,
    TaxationAnalyticsRepository
)

# MIGRATION NOTE: Legacy taxation service functions have been migrated to SOLID architecture
# These functions are now implemented in the new taxation system
# This service acts as a bridge during migration


logger = logging.getLogger(__name__)


class TaxationMigrationService:
    """
    Migration service that wraps legacy taxation functions.
    
    This service acts as a bridge between the legacy taxation service
    and the new SOLID architecture, allowing gradual migration.
    """
    
    def __init__(self):
        """Initialize the migration service"""
        pass
    
    async def get_taxation_data_legacy(
        self,
        employee_id: str,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Get taxation data using legacy functions.
        
        Args:
            employee_id: Employee identifier
            hostname: Organization hostname
            
        Returns:
            Taxation data dictionary
        """
        try:
            logger.info(f"Getting taxation data using legacy service for {employee_id}")
            
            # Use legacy get_or_create_taxation_by_emp_id function
            taxation_data = get_or_create_taxation_by_emp_id(employee_id, hostname)
            
            logger.info(f"Retrieved taxation data for {employee_id}")
            return taxation_data
            
        except Exception as e:
            logger.error(f"Error getting legacy taxation data for {employee_id}: {e}")
            raise
    
    async def calculate_tax_legacy(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str,
        force_recalculate: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate tax using legacy service functions.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            force_recalculate: Force recalculation
            
        Returns:
            Tax calculation results
        """
        try:
            logger.info(f"Calculating tax using legacy service for {employee_id}")
            
            # Use legacy calculate_total_tax function
            total_tax = calculate_total_tax(employee_id, hostname)
            
            # Get taxation data
            taxation_data = get_or_create_taxation_by_emp_id(employee_id, hostname)
            
            # Extract calculation details from taxation data
            tax_breakdown = taxation_data.get("tax_breakup", {})
            
            # Create comprehensive result
            result = {
                "employee_id": employee_id,
                "tax_year": tax_year,
                "total_tax": total_tax,
                "tax_breakdown": tax_breakdown,
                "calculation_method": "legacy",
                "calculated_at": datetime.utcnow().isoformat(),
                "legacy_data": taxation_data
            }
            
            logger.info(f"Legacy tax calculation completed for {employee_id}, total tax: {total_tax}")
            return result
            
        except Exception as e:
            logger.error(f"Error in legacy tax calculation for {employee_id}: {e}")
            raise
    
    async def calculate_tax_projection_legacy(
        self,
        employee_id: str,
        projection_period: str,
        hostname: str
    ) -> TaxProjectionDTO:
        """
        Calculate tax projection using legacy functions.
        
        Args:
            employee_id: Employee identifier
            projection_period: Projection period
            hostname: Organization hostname
            
        Returns:
            Tax projection data
        """
        try:
            logger.info(f"Calculating tax projection using legacy service for {employee_id}")
            
            # Get current taxation data
            taxation_data = get_or_create_taxation_by_emp_id(employee_id, hostname)
            
            # Calculate current tax
            current_tax = calculate_total_tax(employee_id, hostname)
            
            # Get LWP-adjusted salary if available
            lwp_adjusted = calculate_lwp_adjusted_annual_salary(employee_id, hostname)
            
            # Calculate projected income
            projected_income = taxation_data.get("salary", {}).get("basic", 0) * 12
            if lwp_adjusted:
                projected_income = lwp_adjusted.get("actual_annual_gross", projected_income)
            
            # Simple projection logic (would be more sophisticated in practice)
            projected_tax = current_tax
            current_tax_paid = taxation_data.get("tax_paid", 0)
            remaining_liability = max(0, projected_tax - current_tax_paid)
            monthly_suggestion = remaining_liability / 12 if remaining_liability > 0 else 0
            
            # Generate investment suggestions
            investment_suggestions = self._generate_investment_suggestions(
                projected_income, 
                current_tax
            )
            
            return TaxProjectionDTO(
                employee_id=employee_id,
                projection_period=projection_period,
                projected_income=projected_income,
                projected_tax=projected_tax,
                current_tax_paid=current_tax_paid,
                remaining_tax_liability=remaining_liability,
                monthly_tax_suggestion=monthly_suggestion,
                investment_suggestions=investment_suggestions
            )
            
        except Exception as e:
            logger.error(f"Error in legacy tax projection for {employee_id}: {e}")
            raise
    
    async def calculate_tax_comparison_legacy(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> TaxComparisonDTO:
        """
        Calculate tax comparison between regimes using legacy functions.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            Tax comparison data
        """
        try:
            logger.info(f"Calculating tax comparison using legacy service for {employee_id}")
            
            # Get taxation data
            taxation_data = get_or_create_taxation_by_emp_id(employee_id, hostname)
            
            # Get employee age and income
            emp_age = taxation_data.get("emp_age", 0)
            salary = taxation_data.get("salary", {})
            gross_income = (
                salary.get("basic", 0) + 
                salary.get("dearness_allowance", 0) + 
                salary.get("hra", 0) + 
                salary.get("special_allowance", 0)
            )
            
            # Calculate tax under old regime
            old_regime_tax = self._calculate_regime_tax(
                gross_income, 
                "old", 
                emp_age, 
                taxation_data
            )
            
            # Calculate tax under new regime
            new_regime_tax = self._calculate_regime_tax(
                gross_income, 
                "new", 
                emp_age, 
                taxation_data
            )
            
            # Calculate savings
            savings_amount = abs(old_regime_tax - new_regime_tax)
            savings_percentage = (savings_amount / max(old_regime_tax, new_regime_tax)) * 100
            
            # Determine recommended regime
            recommended_regime = "new" if new_regime_tax < old_regime_tax else "old"
            
            # Create comparison details
            comparison_details = {
                "old_regime": {
                    "total_tax": old_regime_tax,
                    "deductions_allowed": True,
                    "standard_deduction": apply_standard_deduction(gross_income, "old")
                },
                "new_regime": {
                    "total_tax": new_regime_tax,
                    "deductions_allowed": False,
                    "standard_deduction": apply_standard_deduction(gross_income, "new")
                }
            }
            
            return TaxComparisonDTO(
                employee_id=employee_id,
                old_regime_tax=old_regime_tax,
                new_regime_tax=new_regime_tax,
                savings_amount=savings_amount,
                savings_percentage=savings_percentage,
                recommended_regime=recommended_regime,
                comparison_details=comparison_details
            )
            
        except Exception as e:
            logger.error(f"Error in legacy tax comparison for {employee_id}: {e}")
            raise
    
    async def calculate_lwp_adjustment_legacy(
        self,
        employee_id: str,
        tax_year: str,
        lwp_days: int,
        hostname: str
    ) -> Dict[str, Any]:
        """
        Calculate LWP adjustment using legacy functions.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            lwp_days: Number of LWP days
            hostname: Organization hostname
            
        Returns:
            LWP adjustment calculation results
        """
        try:
            logger.info(f"Calculating LWP adjustment using legacy service for {employee_id}")
            
            # Get LWP-adjusted salary
            lwp_data = calculate_lwp_adjusted_annual_salary(employee_id, hostname, tax_year)
            
            if not lwp_data:
                # No LWP data available, return zero adjustment
                return {
                    "employee_id": employee_id,
                    "lwp_days": 0,
                    "salary_reduction": 0,
                    "tax_savings": 0,
                    "lwp_adjustment_ratio": 1.0,
                    "method_used": "no_lwp_data"
                }
            
            # Calculate tax savings from LWP
            theoretical_salary = lwp_data.get("theoretical_annual_salary", 0)
            actual_salary = lwp_data.get("actual_annual_salary", 0)
            salary_reduction = theoretical_salary - actual_salary
            
            # Estimate tax savings (simplified calculation)
            tax_rate = 0.20  # Assume 20% marginal tax rate
            tax_savings = salary_reduction * tax_rate
            
            return {
                "employee_id": employee_id,
                "lwp_days": lwp_data.get("total_lwp_days", 0),
                "salary_reduction": salary_reduction,
                "tax_savings": tax_savings,
                "lwp_adjustment_ratio": lwp_data.get("lwp_adjustment_ratio", 1.0),
                "theoretical_annual_salary": theoretical_salary,
                "actual_annual_salary": actual_salary,
                "method_used": "legacy_calculation",
                "calculation_details": lwp_data
            }
            
        except Exception as e:
            logger.error(f"Error in legacy LWP adjustment for {employee_id}: {e}")
            raise
    
    async def get_salary_projection_legacy(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get salary projection using legacy functions.
        
        Args:
            employee_id: Employee identifier
            tax_year: Tax year
            hostname: Organization hostname
            
        Returns:
            Salary projection data or None
        """
        try:
            # This would integrate with salary history service if available
            # For now, return basic projection from taxation data
            taxation_data = get_or_create_taxation_by_emp_id(employee_id, hostname)
            
            if not taxation_data:
                return None
            
            salary = taxation_data.get("salary", {})
            basic = salary.get("basic", 0)
            
            return {
                "employee_id": employee_id,
                "tax_year": tax_year,
                "projected_annual_gross": basic * 12,
                "salary_changes_count": 0,
                "last_change_date": None,
                "projection_method": "static_legacy"
            }
            
        except Exception as e:
            logger.error(f"Error getting legacy salary projection for {employee_id}: {e}")
            return None
    
    def _calculate_regime_tax(
        self,
        income: float,
        regime: str,
        age: int,
        taxation_data: Dict[str, Any]
    ) -> float:
        """Calculate tax for a specific regime"""
        try:
            # Apply standard deduction
            standard_deduction = apply_standard_deduction(income, regime)
            taxable_income = max(0, income - standard_deduction)
            
            # Calculate regular tax
            regular_tax = compute_regular_tax(taxable_income, regime, age)
            
            # Apply 87A rebate
            tax_after_rebate = apply_87a_rebate(regular_tax, taxable_income, regime)
            
            # Calculate surcharge
            surcharge_result = compute_surcharge(tax_after_rebate, taxable_income)
            tax_with_surcharge = surcharge_result["total_tax"]
            
            # Add cess (4%)
            total_tax = tax_with_surcharge * 1.04
            
            return total_tax
            
        except Exception as e:
            logger.error(f"Error calculating regime tax: {e}")
            return 0.0
    
    def _generate_investment_suggestions(
        self,
        income: float,
        current_tax: float
    ) -> List[Dict[str, Any]]:
        """Generate basic investment suggestions"""
        suggestions = []
        
        # 80C suggestions
        if income > 300000:  # If eligible for deductions
            suggestions.append({
                "type": "80C",
                "title": "Section 80C Investments",
                "description": "Invest up to Rs. 1.5 lakh in PPF, ELSS, etc.",
                "max_amount": 150000,
                "tax_savings": 150000 * 0.20  # Assuming 20% tax bracket
            })
        
        # 80D suggestions
        suggestions.append({
            "type": "80D",
            "title": "Health Insurance",
            "description": "Health insurance premiums for self and family",
            "max_amount": 25000,
            "tax_savings": 25000 * 0.20
        })
        
        return suggestions


class LegacyTaxationCalculationRepository(TaxationCalculationRepository):
    """
    Implementation of TaxationCalculationRepository using legacy functions.
    
    This allows the new architecture to use legacy calculation logic
    while maintaining the SOLID interface.
    """
    
    def __init__(self):
        self.migration_service = TaxationMigrationService()
    
    async def calculate_tax(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str,
        force_recalculate: bool = False
    ) -> Dict[str, Any]:
        """Calculate tax using legacy service"""
        return await self.migration_service.calculate_tax_legacy(
            employee_id, tax_year, hostname, force_recalculate
        )
    
    async def calculate_tax_comparison(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> TaxComparisonDTO:
        """Calculate tax comparison using legacy service"""
        return await self.migration_service.calculate_tax_comparison_legacy(
            employee_id, tax_year, hostname
        )
    
    async def calculate_tax_projection(
        self,
        employee_id: str,
        projection_period: str,
        hostname: str
    ) -> TaxProjectionDTO:
        """Calculate tax projection using legacy service"""
        return await self.migration_service.calculate_tax_projection_legacy(
            employee_id, projection_period, hostname
        )
    
    async def calculate_lwp_adjustment(
        self,
        employee_id: str,
        tax_year: str,
        lwp_days: int,
        hostname: str
    ) -> Dict[str, Any]:
        """Calculate LWP adjustment using legacy service"""
        return await self.migration_service.calculate_lwp_adjustment_legacy(
            employee_id, tax_year, lwp_days, hostname
        )
    
    async def get_salary_projection(
        self,
        employee_id: str,
        tax_year: str,
        hostname: str
    ) -> Optional[Dict[str, Any]]:
        """Get salary projection using legacy service"""
        return await self.migration_service.get_salary_projection_legacy(
            employee_id, tax_year, hostname
        ) 