"""
Enhanced Taxation Service - Re-architected with Modern Patterns
Integrates event-driven architecture, strategy pattern, and lifecycle management
"""

from datetime import date, datetime
from typing import Dict, List, Optional, Any
import logging

from strategies.tax_calculation_strategies import (
    TaxCalculationEngine, TaxCalculationContext, TaxCalculationResult,
    TaxStrategyFactory
)
from events.tax_events import (
    TaxEventProcessor, TaxEventPublisher, EventStore, EventFactory
)
from services.employee_lifecycle_service import (
    EmployeeLifecycleService, NewJoinerProfile, ExitProfile, SalaryRevisionProfile
)
from models.salary_management import SalaryProjection, SalaryChangeRecord
from services.taxation_service import TaxationService
from services.payout_service import PayoutService

logger = logging.getLogger(__name__)


class EnhancedTaxationService:
    """
    Enhanced taxation service with re-architected components
    Provides a unified interface for all tax-related operations
    """
    
    def __init__(self, database_connection):
        self.db = database_connection
        self.logger = logging.getLogger("EnhancedTaxationService")
        
        # Initialize core services
        self.taxation_service = TaxationService(database_connection)
        self.payout_service = PayoutService(database_connection)
        
        # Initialize new architecture components
        self.tax_engine = TaxCalculationEngine()
        self.event_store = EventStore(database_connection)
        self.event_publisher = TaxEventPublisher(self.event_store)
        self.event_processor = TaxEventProcessor(
            self.event_publisher,
            self,  # salary service functionality
            self.tax_engine,
            self.payout_service,
            None  # will be set after lifecycle service creation
        )
        
        # Initialize lifecycle service
        self.lifecycle_service = EmployeeLifecycleService(
            self.taxation_service,
            self.payout_service,
            self.tax_engine,
            self.event_processor
        )
        
        # Update event processor with lifecycle service
        self.event_processor._register_handlers(
            self, self.tax_engine, self.payout_service, self.lifecycle_service
        )
        
        self.logger.info("Enhanced Taxation Service initialized successfully")
    
    # ==================== MAIN TAX CALCULATION METHODS ====================
    
    def calculate_employee_tax(self, employee_id: str, tax_year: Optional[str] = None,
                             regime: Optional[str] = None) -> TaxCalculationResult:
        """
        Calculate tax for an employee using the new strategy pattern
        """
        try:
            self.logger.info(f"Calculating tax for employee {employee_id}")
            
            # 1. Build tax calculation context
            context = self._build_tax_context(employee_id, tax_year, regime)
            
            # 2. Calculate tax using appropriate strategy
            result = self.tax_engine.calculate_tax(context)
            
            # 3. Store calculation result
            self._store_tax_calculation_result(result)
            
            # 4. Publish tax calculated event
            self._publish_tax_calculated_event(result)
            
            self.logger.info(f"Tax calculation completed for {employee_id}: {result.total_tax}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating tax for {employee_id}: {str(e)}")
            raise
    
    def compare_tax_regimes(self, employee_id: str, tax_year: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare tax liability between old and new regimes
        """
        try:
            self.logger.info(f"Comparing tax regimes for employee {employee_id}")
            
            # Build context for comparison
            context = self._build_tax_context(employee_id, tax_year)
            
            # Compare regimes
            comparison = self.tax_engine.compare_regimes(context)
            
            # Calculate savings and recommendation
            old_tax = comparison["old"].total_tax
            new_tax = comparison["new"].total_tax
            savings = old_tax - new_tax
            recommended_regime = "new" if new_tax < old_tax else "old"
            
            result = {
                "employee_id": employee_id,
                "comparison_date": datetime.now().isoformat(),
                "old_regime": comparison["old"].to_dict(),
                "new_regime": comparison["new"].to_dict(),
                "savings_with_new_regime": savings,
                "recommended_regime": recommended_regime,
                "savings_percentage": (savings / old_tax * 100) if old_tax > 0 else 0
            }
            
            self.logger.info(f"Regime comparison completed for {employee_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error comparing regimes for {employee_id}: {str(e)}")
            raise
    
    def calculate_monthly_tds(self, employee_id: str, month: str, year: str) -> Dict[str, Any]:
        """
        Calculate monthly TDS with all adjustments
        """
        try:
            self.logger.info(f"Calculating monthly TDS for {employee_id} - {month}/{year}")
            
            # Get annual tax calculation
            annual_tax = self.calculate_employee_tax(employee_id)
            
            # Calculate monthly TDS with adjustments
            monthly_tds = self._calculate_monthly_tds_with_adjustments(
                employee_id, annual_tax, month, year
            )
            
            self.logger.info(f"Monthly TDS calculated for {employee_id}: {monthly_tds['tds_amount']}")
            return monthly_tds
            
        except Exception as e:
            self.logger.error(f"Error calculating monthly TDS for {employee_id}: {str(e)}")
            raise
    
    # ==================== EMPLOYEE LIFECYCLE METHODS ====================
    
    def process_new_joiner(self, employee_id: str, join_date: date, annual_salary: float,
                          previous_employment: Optional[Dict[str, Any]] = None,
                          tax_regime_preference: str = "new") -> Dict[str, Any]:
        """
        Process new joiner with comprehensive tax setup
        """
        try:
            profile = NewJoinerProfile(
                employee_id=employee_id,
                join_date=join_date,
                annual_salary=annual_salary,
                previous_employment=previous_employment,
                tax_regime_preference=tax_regime_preference
            )
            
            return self.lifecycle_service.handle_new_joiner(profile)
            
        except Exception as e:
            self.logger.error(f"Error processing new joiner {employee_id}: {str(e)}")
            raise
    
    def process_employee_exit(self, employee_id: str, exit_date: date, exit_type: str,
                            settlement_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process employee exit with final settlement
        """
        try:
            profile = ExitProfile(
                employee_id=employee_id,
                exit_date=exit_date,
                exit_type=exit_type
            )
            
            # Add settlement details if provided
            if settlement_details:
                for key, value in settlement_details.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
            
            return self.lifecycle_service.handle_employee_exit(profile)
            
        except Exception as e:
            self.logger.error(f"Error processing employee exit {employee_id}: {str(e)}")
            raise
    
    def process_salary_revision(self, employee_id: str, revision_type: str, effective_date: date,
                              old_salary: Dict[str, float], new_salary: Dict[str, float],
                              is_retroactive: bool = False) -> Dict[str, Any]:
        """
        Process salary revision with tax implications
        """
        try:
            profile = SalaryRevisionProfile(
                employee_id=employee_id,
                revision_type=revision_type,
                effective_date=effective_date,
                old_salary_structure=old_salary,
                new_salary_structure=new_salary,
                is_retroactive=is_retroactive
            )
            
            return self.lifecycle_service.handle_salary_revision(profile)
            
        except Exception as e:
            self.logger.error(f"Error processing salary revision for {employee_id}: {str(e)}")
            raise
    
    def process_regime_change(self, employee_id: str, new_regime: str, 
                            effective_date: date) -> Dict[str, Any]:
        """
        Process mid-year tax regime change
        """
        try:
            return self.lifecycle_service.handle_mid_year_regime_change(
                employee_id, new_regime, effective_date
            )
            
        except Exception as e:
            self.logger.error(f"Error processing regime change for {employee_id}: {str(e)}")
            raise
    
    def process_lwp_scenario(self, employee_id: str, lwp_start: date, lwp_end: date,
                           lwp_type: str = "unpaid_leave") -> Dict[str, Any]:
        """
        Process Leave Without Pay scenario
        """
        try:
            return self.lifecycle_service.handle_lwp_scenario(
                employee_id, lwp_start, lwp_end, lwp_type
            )
            
        except Exception as e:
            self.logger.error(f"Error processing LWP for {employee_id}: {str(e)}")
            raise
    
    def process_bonus_payment(self, employee_id: str, bonus_amount: float,
                            bonus_type: str, payment_date: date) -> Dict[str, Any]:
        """
        Process bonus payment with tax implications
        """
        try:
            return self.lifecycle_service.handle_bonus_payment(
                employee_id, bonus_amount, bonus_type, payment_date
            )
            
        except Exception as e:
            self.logger.error(f"Error processing bonus for {employee_id}: {str(e)}")
            raise
    
    # ==================== BULK OPERATIONS ====================
    
    def bulk_calculate_taxes(self, employee_ids: List[str], 
                           tax_year: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate taxes for multiple employees
        """
        try:
            self.logger.info(f"Starting bulk tax calculation for {len(employee_ids)} employees")
            
            results = {}
            errors = {}
            
            for employee_id in employee_ids:
                try:
                    result = self.calculate_employee_tax(employee_id, tax_year)
                    results[employee_id] = result.to_dict()
                except Exception as e:
                    errors[employee_id] = str(e)
                    self.logger.error(f"Error in bulk calculation for {employee_id}: {str(e)}")
            
            summary = {
                "total_employees": len(employee_ids),
                "successful": len(results),
                "failed": len(errors),
                "success_rate": len(results) / len(employee_ids) * 100,
                "results": results,
                "errors": errors,
                "processing_date": datetime.now().isoformat()
            }
            
            self.logger.info(f"Bulk calculation completed: {len(results)} successful, {len(errors)} failed")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error in bulk tax calculation: {str(e)}")
            raise
    
    def bulk_regime_comparison(self, employee_ids: List[str]) -> Dict[str, Any]:
        """
        Compare tax regimes for multiple employees
        """
        try:
            self.logger.info(f"Starting bulk regime comparison for {len(employee_ids)} employees")
            
            results = {}
            summary_stats = {
                "total_employees": len(employee_ids),
                "new_regime_beneficial": 0,
                "old_regime_beneficial": 0,
                "total_potential_savings": 0.0
            }
            
            for employee_id in employee_ids:
                try:
                    comparison = self.compare_tax_regimes(employee_id)
                    results[employee_id] = comparison
                    
                    # Update summary stats
                    if comparison["recommended_regime"] == "new":
                        summary_stats["new_regime_beneficial"] += 1
                        summary_stats["total_potential_savings"] += comparison["savings_with_new_regime"]
                    else:
                        summary_stats["old_regime_beneficial"] += 1
                        
                except Exception as e:
                    self.logger.error(f"Error in regime comparison for {employee_id}: {str(e)}")
            
            return {
                "summary": summary_stats,
                "detailed_results": results,
                "processing_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in bulk regime comparison: {str(e)}")
            raise
    
    # ==================== REPORTING AND ANALYTICS ====================
    
    def generate_tax_analytics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate comprehensive tax analytics
        """
        try:
            self.logger.info("Generating tax analytics")
            
            # Implementation would include various analytics
            analytics = {
                "total_employees": self._get_total_employees(filters),
                "regime_distribution": self._get_regime_distribution(filters),
                "tax_liability_distribution": self._get_tax_liability_distribution(filters),
                "average_tax_rates": self._get_average_tax_rates(filters),
                "compliance_metrics": self._get_compliance_metrics(filters),
                "generated_at": datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating tax analytics: {str(e)}")
            raise
    
    def generate_compliance_report(self, report_type: str, 
                                 period: str) -> Dict[str, Any]:
        """
        Generate compliance reports (Form 16, TDS returns, etc.)
        """
        try:
            self.logger.info(f"Generating {report_type} compliance report for {period}")
            
            # Implementation would generate specific compliance reports
            report = {
                "report_type": report_type,
                "period": period,
                "generated_at": datetime.now().isoformat(),
                "data": self._generate_compliance_data(report_type, period)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {str(e)}")
            raise
    
    # ==================== EVENT PROCESSING ====================
    
    def process_pending_events(self) -> Dict[str, int]:
        """
        Process all pending tax events
        """
        try:
            self.logger.info("Processing pending tax events")
            return self.event_publisher.process_pending_events()
            
        except Exception as e:
            self.logger.error(f"Error processing pending events: {str(e)}")
            raise
    
    def get_employee_events(self, employee_id: str, 
                          event_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get events for a specific employee
        """
        try:
            # Convert string event types to enum if provided
            enum_types = None
            if event_types:
                from events.tax_events import TaxEventType
                enum_types = [TaxEventType(et) for et in event_types]
            
            events = self.event_store.get_events_by_employee(employee_id, enum_types)
            return [event.to_dict() for event in events]
            
        except Exception as e:
            self.logger.error(f"Error getting events for {employee_id}: {str(e)}")
            raise
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    def _build_tax_context(self, employee_id: str, tax_year: Optional[str] = None,
                          regime: Optional[str] = None) -> TaxCalculationContext:
        """
        Build comprehensive tax calculation context
        """
        # This would integrate with your existing data models
        # Placeholder implementation
        return TaxCalculationContext(
            employee_id=employee_id,
            tax_year=tax_year or self._get_current_tax_year(),
            calculation_date=datetime.now(),
            regime=regime or self._get_employee_regime(employee_id),
            age=self._get_employee_age(employee_id),
            is_govt_employee=self._is_govt_employee(employee_id)
        )
    
    def _store_tax_calculation_result(self, result: TaxCalculationResult) -> None:
        """Store tax calculation result in database"""
        # Implementation to store result
        pass
    
    def _publish_tax_calculated_event(self, result: TaxCalculationResult) -> None:
        """Publish tax calculated event"""
        from events.tax_events import TaxEvent, TaxEventType
        
        event = TaxEvent(
            event_type=TaxEventType.TAX_CALCULATED,
            employee_id=result.employee_id,
            metadata={
                "total_tax": result.total_tax,
                "regime": result.regime,
                "calculation_method": result.calculation_method
            }
        )
        
        self.event_publisher.publish(event)
    
    def _calculate_monthly_tds_with_adjustments(self, employee_id: str, 
                                              annual_tax: TaxCalculationResult,
                                              month: str, year: str) -> Dict[str, Any]:
        """Calculate monthly TDS with all adjustments"""
        # Implementation for monthly TDS calculation
        remaining_months = self._get_remaining_months_in_year(month, year)
        monthly_tds = annual_tax.total_tax / remaining_months if remaining_months > 0 else 0
        
        return {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "annual_tax": annual_tax.total_tax,
            "remaining_months": remaining_months,
            "tds_amount": monthly_tds,
            "calculation_date": datetime.now().isoformat()
        }
    
    def _get_current_tax_year(self) -> str:
        """Get current tax year"""
        now = datetime.now()
        if now.month >= 4:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
    def _get_employee_regime(self, employee_id: str) -> str:
        """Get employee's current tax regime"""
        # Implementation to fetch from database
        return "new"  # Default
    
    def _get_employee_age(self, employee_id: str) -> int:
        """Get employee age"""
        # Implementation to fetch from database
        return 30  # Default
    
    def _is_govt_employee(self, employee_id: str) -> bool:
        """Check if employee is government employee"""
        # Implementation to fetch from database
        return False  # Default
    
    def _get_remaining_months_in_year(self, month: str, year: str) -> int:
        """Get remaining months in tax year"""
        # Implementation to calculate remaining months
        return 12  # Placeholder
    
    # Analytics helper methods
    def _get_total_employees(self, filters: Optional[Dict[str, Any]]) -> int:
        """Get total employee count"""
        return 0  # Placeholder
    
    def _get_regime_distribution(self, filters: Optional[Dict[str, Any]]) -> Dict[str, int]:
        """Get regime distribution"""
        return {"old": 0, "new": 0}  # Placeholder
    
    def _get_tax_liability_distribution(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get tax liability distribution"""
        return {}  # Placeholder
    
    def _get_average_tax_rates(self, filters: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Get average tax rates"""
        return {}  # Placeholder
    
    def _get_compliance_metrics(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get compliance metrics"""
        return {}  # Placeholder
    
    def _generate_compliance_data(self, report_type: str, period: str) -> Dict[str, Any]:
        """Generate compliance report data"""
        return {}  # Placeholder 