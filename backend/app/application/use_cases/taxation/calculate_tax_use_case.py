"""
Calculate Tax Use Case
Handles tax calculation business logic
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date

from app.application.dto.taxation_dto import (
    TaxCalculationRequestDTO,
    TaxationResponseDTO,
    TaxBreakdownDTO,
    TaxationCalculationError,
    TaxationNotFoundError
)
from app.application.interfaces.repositories.taxation_repository import (
    TaxationQueryRepository,
    TaxationCommandRepository,
    TaxationCalculationRepository
)
from app.application.interfaces.services.notification_service import NotificationService
from app.domain.events.taxation_events import TaxationCalculated
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money


logger = logging.getLogger(__name__)


class CalculateTaxUseCase:
    """
    Use case for calculating employee tax.
    
    Follows SOLID principles:
    - SRP: Only handles tax calculation logic
    - OCP: Can be extended with new calculation methods
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for tax calculation
    - DIP: Depends on repository abstractions
    """
    
    def __init__(
        self,
        query_repository: TaxationQueryRepository,
        command_repository: TaxationCommandRepository,
        calculation_repository: TaxationCalculationRepository,
        notification_service: NotificationService
    ):
        self.query_repository = query_repository
        self.command_repository = command_repository
        self.calculation_repository = calculation_repository
        self.notification_service = notification_service
    
    async def execute(
        self,
        request: TaxCalculationRequestDTO,
        hostname: str
    ) -> TaxationResponseDTO:
        """
        Execute tax calculation for an employee.
        
        Args:
            request: Tax calculation request
            hostname: Organisation hostname
            
        Returns:
            Updated taxation response with calculated tax
            
        Raises:
            TaxationNotFoundError: If taxation record not found
            TaxationCalculationError: If calculation fails
        """
        try:
            logger.info(f"Starting tax calculation for employee: {request.employee_id}")
            
            # Validate request
            validation_errors = request.validate()
            if validation_errors:
                raise TaxationCalculationError(
                    f"Validation failed: {', '.join(validation_errors)}",
                    {"employee_id": request.employee_id, "errors": validation_errors}
                )
            
            # Get current taxation record
            taxation = await self._get_or_create_taxation_record(
                request.employee_id, 
                hostname
            )
            
            if not taxation:
                raise TaxationNotFoundError(request.employee_id)
            
            # Check if recalculation is needed
            if not request.force_recalculate and self._is_calculation_current(taxation):
                logger.info(f"Tax already calculated for {request.employee_id}, returning existing calculation")
                return taxation
            
            # Perform tax calculation
            calculation_result = await self._perform_tax_calculation(
                taxation,
                request.calculation_type,
                hostname
            )
            
            # Update taxation record with calculation results
            updated_taxation = await self._update_taxation_with_calculation(
                taxation,
                calculation_result,
                hostname,
                request.calculated_by
            )
            
            # Raise domain event
            await self._raise_tax_calculated_event(
                updated_taxation,
                calculation_result,
                request.calculated_by
            )
            
            # Send notifications if requested
            if request.calculation_type == "full":
                await self._send_calculation_notifications(
                    updated_taxation,
                    calculation_result
                )
            
            logger.info(f"Tax calculation completed for {request.employee_id}, total tax: {updated_taxation.total_tax}")
            return updated_taxation
            
        except (TaxationNotFoundError, TaxationCalculationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error calculating tax for {request.employee_id}: {e}")
            raise TaxationCalculationError(
                f"Unexpected error during tax calculation: {str(e)}",
                {"employee_id": request.employee_id, "error": str(e)}
            )
    
    async def calculate_with_projections(
        self,
        employee_id: str,
        hostname: str,
        calculated_by: str = ""
    ) -> Dict[str, Any]:
        """
        Calculate tax with salary projections and LWP adjustments.
        
        Args:
            employee_id: Employee identifier
            hostname: Organisation hostname
            calculated_by: User performing calculation
            
        Returns:
            Comprehensive calculation results including projections
        """
        try:
            logger.info(f"Calculating tax with projections for employee: {employee_id}")
            
            # Get current year
            current_year = self._get_current_tax_year()
            
            # Get or create taxation record
            taxation = await self._get_or_create_taxation_record(employee_id, hostname)
            if not taxation:
                raise TaxationNotFoundError(employee_id, current_year)
            
            # Get salary projection (considering mid-year changes)
            salary_projection = await self.calculation_repository.get_salary_projection(
                employee_id, 
                current_year, 
                hostname
            )
            
            # Calculate LWP adjustment
            lwp_adjustment = await self.calculation_repository.calculate_lwp_adjustment(
                employee_id,
                current_year,
                0,  # Will be calculated from payout records
                hostname
            )
            
            # Perform comprehensive tax calculation
            base_calculation = await self.calculation_repository.calculate_tax(
                employee_id,
                current_year,
                hostname,
                force_recalculate=True
            )
            
            # Combine all calculations
            comprehensive_result = {
                "base_calculation": base_calculation,
                "salary_projection": salary_projection,
                "lwp_adjustment": lwp_adjustment,
                "effective_tax": self._calculate_effective_tax(
                    base_calculation,
                    salary_projection,
                    lwp_adjustment
                ),
                "calculated_at": datetime.utcnow().isoformat(),
                "calculated_by": calculated_by
            }
            
            # Update taxation record
            await self.command_repository.update_tax_calculation(
                employee_id,
                current_year,
                comprehensive_result,
                hostname
            )
            
            logger.info(f"Comprehensive tax calculation completed for {employee_id}")
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Error in comprehensive tax calculation for {employee_id}: {e}")
            raise TaxationCalculationError(
                f"Comprehensive calculation failed: {str(e)}",
                {"employee_id": employee_id, "error": str(e)}
            )
    
    async def _get_or_create_taxation_record(
        self,
        employee_id: str,
        hostname: str
    ) -> Optional[TaxationResponseDTO]:
        """Get existing taxation record or create default one"""
        try:
            # Try to get current year record
            current_year = self._get_current_tax_year()
            taxation = await self.query_repository.get_taxation_by_employee(
                employee_id,
                current_year,
                hostname
            )
            
            if taxation:
                return taxation
            
            # Get current taxation (any year)
            taxation = await self.query_repository.get_current_taxation(
                employee_id,
                hostname
            )
            
            return taxation
            
        except Exception as e:
            logger.error(f"Error getting/creating taxation record for {employee_id}: {e}")
            return None
    
    def _is_calculation_current(self, taxation: TaxationResponseDTO) -> bool:
        """Check if tax calculation is current (within last 24 hours)"""
        if not taxation.calculated_at:
            return False
        
        try:
            calculated_time = datetime.fromisoformat(taxation.calculated_at.replace('Z', '+00:00'))
            time_diff = datetime.utcnow() - calculated_time.replace(tzinfo=None)
            return time_diff.total_seconds() < 86400  # 24 hours
        except:
            return False
    
    async def _perform_tax_calculation(
        self,
        taxation: TaxationResponseDTO,
        calculation_type: str,
        hostname: str
    ) -> Dict[str, Any]:
        """Perform the actual tax calculation"""
        try:
            if calculation_type == "quick":
                # Quick calculation without detailed breakdown
                return await self.calculation_repository.calculate_tax(
                    taxation.employee_id,
                    taxation.tax_year,
                    hostname,
                    force_recalculate=True
                )
            elif calculation_type == "projection":
                # Projection calculation
                projection = await self.calculation_repository.calculate_tax_projection(
                    taxation.employee_id,
                    "annual",
                    hostname
                )
                return {
                    "projection": projection.to_dict(),
                    "calculation_type": "projection"
                }
            else:
                # Full calculation with all components
                return await self.calculation_repository.calculate_tax(
                    taxation.employee_id,
                    taxation.tax_year,
                    hostname,
                    force_recalculate=True
                )
                
        except Exception as e:
            logger.error(f"Error performing tax calculation: {e}")
            raise TaxationCalculationError(
                f"Calculation failed: {str(e)}",
                {"employee_id": taxation.employee_id, "calculation_type": calculation_type}
            )
    
    async def _update_taxation_with_calculation(
        self,
        taxation: TaxationResponseDTO,
        calculation_result: Dict[str, Any],
        hostname: str,
        calculated_by: str
    ) -> TaxationResponseDTO:
        """Update taxation record with calculation results"""
        try:
            # Update the calculation results
            success = await self.command_repository.update_tax_calculation(
                taxation.employee_id,
                taxation.tax_year,
                calculation_result,
                hostname
            )
            
            if not success:
                raise TaxationCalculationError(
                    "Failed to update taxation record with calculation results"
                )
            
            # Get updated record
            updated_taxation = await self.query_repository.get_taxation_by_employee(
                taxation.employee_id,
                taxation.tax_year,
                hostname
            )
            
            if not updated_taxation:
                raise TaxationCalculationError(
                    "Failed to retrieve updated taxation record"
                )
            
            return updated_taxation
            
        except Exception as e:
            logger.error(f"Error updating taxation record: {e}")
            raise TaxationCalculationError(
                f"Failed to update taxation record: {str(e)}"
            )
    
    async def _raise_tax_calculated_event(
        self,
        taxation: TaxationResponseDTO,
        calculation_result: Dict[str, Any],
        calculated_by: str
    ):
        """Raise tax calculated domain event"""
        try:
            event = TaxationCalculated(
                employee_id=EmployeeId(taxation.employee_id),
                tax_year=taxation.tax_year,
                regime=taxation.regime,
                total_tax=Money.from_float(taxation.total_tax),
                taxable_income=Money.from_float(taxation.taxable_income),
                calculated_by=EmployeeId(calculated_by) if calculated_by else None
            )
            
            # In a full implementation, this would be handled by an event bus
            logger.info(f"Tax calculation event raised for {taxation.employee_id}")
            
        except Exception as e:
            logger.warning(f"Failed to raise tax calculated event: {e}")
    
    async def _send_calculation_notifications(
        self,
        taxation: TaxationResponseDTO,
        calculation_result: Dict[str, Any]
    ):
        """Send notifications about tax calculation"""
        try:
            # This would be implemented with actual notification logic
            logger.info(f"Sending tax calculation notifications for {taxation.employee_id}")
            
        except Exception as e:
            logger.warning(f"Failed to send calculation notifications: {e}")
    
    def _get_current_tax_year(self) -> str:
        """Get current tax year in Indian format"""
        current_date = date.today()
        if current_date.month >= 4:  # April onwards
            return f"{current_date.year}-{current_date.year + 1}"
        else:  # January to March
            return f"{current_date.year - 1}-{current_date.year}"
    
    def _calculate_effective_tax(
        self,
        base_calculation: Dict[str, Any],
        salary_projection: Optional[Dict[str, Any]],
        lwp_adjustment: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate effective tax considering all adjustments"""
        try:
            base_tax = base_calculation.get("total_tax", 0)
            
            # Apply salary projection adjustments
            if salary_projection:
                projected_tax = salary_projection.get("projected_tax", base_tax)
            else:
                projected_tax = base_tax
            
            # Apply LWP adjustments
            if lwp_adjustment:
                lwp_tax_savings = lwp_adjustment.get("tax_savings", 0)
                effective_tax = max(0, projected_tax - lwp_tax_savings)
            else:
                effective_tax = projected_tax
            
            return {
                "base_tax": base_tax,
                "projected_tax": projected_tax,
                "effective_tax": effective_tax,
                "lwp_savings": lwp_adjustment.get("tax_savings", 0) if lwp_adjustment else 0,
                "total_adjustments": projected_tax - base_tax
            }
            
        except Exception as e:
            logger.error(f"Error calculating effective tax: {e}")
            return {
                "base_tax": base_calculation.get("total_tax", 0),
                "projected_tax": base_calculation.get("total_tax", 0),
                "effective_tax": base_calculation.get("total_tax", 0),
                "lwp_savings": 0,
                "total_adjustments": 0
            } 