"""
Employee Lifecycle Service
Handles complex employee lifecycle scenarios with tax implications
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from decimal import Decimal

from domain.entities.salary_management import (
    SalaryChangeRecord, SalaryProjection, LWPAdjustment,
    SalaryChangeReason, SalaryChangeStatus
)
# LEGACY: strategies.tax_calculation_strategies has been removed
# TODO: Replace with SOLID taxation services when needed
# from strategies.tax_calculation_strategies import (
#     TaxCalculationEngine, TaxCalculationContext, TaxCalculationResult
# )
from events.tax_events import TaxEventProcessor, EventFactory
# MIGRATION: Replace legacy taxation_service imports with SOLID architecture
from infrastructure.services.taxation_migration_service import (
    TaxationMigrationService,
    LegacyTaxationCalculationRepository
)
# PayoutService replaced by payroll migration service - using individual functions as needed

logger = logging.getLogger(__name__)


@dataclass
class NewJoinerProfile:
    """Profile for new joiner with tax implications"""
    employee_id: str
    join_date: date
    annual_salary: float
    previous_employment: Optional[Dict[str, Any]] = None
    tax_regime_preference: str = "new"
    age: int = 25
    is_govt_employee: bool = False
    
    # Previous employment details
    previous_employer_name: Optional[str] = None
    previous_employment_start: Optional[date] = None
    previous_employment_end: Optional[date] = None
    previous_gross_salary: float = 0.0
    previous_tds_deducted: float = 0.0
    previous_pf_contribution: float = 0.0
    
    # Investment declarations
    has_existing_investments: bool = False
    investment_declarations: Dict[str, float] = None
    
    def __post_init__(self):
        if self.investment_declarations is None:
            self.investment_declarations = {}


@dataclass
class ExitProfile:
    """Profile for employee exit with settlement calculations"""
    employee_id: str
    exit_date: date
    exit_type: str  # resignation, termination, retirement, death
    notice_period_days: int = 0
    notice_period_served: int = 0
    
    # Settlement components
    pending_salary_days: int = 0
    leave_encashment_days: int = 0
    bonus_amount: float = 0.0
    gratuity_amount: float = 0.0
    pf_withdrawal_amount: float = 0.0
    
    # Recovery components
    notice_period_recovery: float = 0.0
    other_recoveries: float = 0.0
    
    # Tax implications
    requires_form16_part_b: bool = True
    final_tds_calculation: bool = True


@dataclass
class SalaryRevisionProfile:
    """Profile for salary revision scenarios"""
    employee_id: str
    revision_type: str  # hike, promotion, transfer, correction
    effective_date: date
    old_salary_structure: Dict[str, float]
    new_salary_structure: Dict[str, float]
    is_retroactive: bool = False
    retroactive_from_date: Optional[date] = None
    
    # Additional components
    promotion_bonus: float = 0.0
    one_time_payments: Dict[str, float] = None
    
    def __post_init__(self):
        if self.one_time_payments is None:
            self.one_time_payments = {}


class EmployeeLifecycleService:
    """Service for handling employee lifecycle events"""
    
    def __init__(self, taxation_service: TaxationMigrationService, 
                 hostname: str,  # Replace PayoutService with hostname for payroll functions
                 tax_engine: TaxCalculationEngine,
                 event_processor: TaxEventProcessor):
        self.taxation_service = taxation_service
        self.hostname = hostname
        self.tax_engine = tax_engine
        self.event_processor = event_processor
        self.logger = logging.getLogger("EmployeeLifecycleService")
    
    def handle_new_joiner(self, profile: NewJoinerProfile) -> Dict[str, Any]:
        """Handle new joiner with comprehensive tax setup"""
        try:
            self.logger.info(f"Processing new joiner: {profile.employee_id}")
            
            # 1. Calculate pro-rated annual projection
            projection = self._calculate_new_joiner_projection(profile)
            
            # 2. Handle previous employment tax implications
            previous_tax_impact = self._handle_previous_employment(profile)
            
            # 3. Set up tax calculation context
            context = self._create_tax_context_for_new_joiner(profile, projection, previous_tax_impact)
            
            # 4. Calculate optimal tax regime
            regime_comparison = self.tax_engine.compare_regimes(context)
            optimal_regime = self._determine_optimal_regime(regime_comparison)
            
            # 5. Set up monthly TDS
            monthly_tds = self._calculate_monthly_tds_for_new_joiner(
                context, optimal_regime, profile.join_date
            )
            
            # 6. Create initial payout records
            payout_setup = self._setup_initial_payouts(profile, monthly_tds)
            
            # 7. Generate compliance documents
            compliance_docs = self._generate_new_joiner_compliance_docs(profile, context)
            
            # 8. Publish event
            self.event_processor.process_new_joiner(
                profile.employee_id,
                profile.join_date,
                profile.annual_salary,
                profile.previous_tds_deducted
            )
            
            result = {
                "employee_id": profile.employee_id,
                "status": "success",
                "projection": projection,
                "previous_tax_impact": previous_tax_impact,
                "regime_comparison": {k: v.to_dict() for k, v in regime_comparison.items()},
                "recommended_regime": optimal_regime,
                "monthly_tds": monthly_tds,
                "payout_setup": payout_setup,
                "compliance_documents": compliance_docs,
                "processing_date": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed new joiner: {profile.employee_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing new joiner {profile.employee_id}: {str(e)}")
            raise
    
    def handle_employee_exit(self, profile: ExitProfile) -> Dict[str, Any]:
        """Handle employee exit with final settlement"""
        try:
            self.logger.info(f"Processing employee exit: {profile.employee_id}")
            
            # 1. Calculate final settlement components
            settlement = self._calculate_final_settlement(profile)
            
            # 2. Calculate final tax liability
            final_tax = self._calculate_final_tax_on_exit(profile, settlement)
            
            # 3. Generate Form 16 Part B
            form16_data = self._generate_form16_part_b(profile, settlement, final_tax)
            
            # 4. Calculate final TDS adjustment
            tds_adjustment = self._calculate_final_tds_adjustment(profile, final_tax)
            
            # 5. Process final payout
            final_payout = self._process_final_payout(profile, settlement, tds_adjustment)
            
            # 6. Update employee status
            self._update_employee_exit_status(profile)
            
            # 7. Generate compliance reports
            compliance_reports = self._generate_exit_compliance_reports(profile, settlement)
            
            result = {
                "employee_id": profile.employee_id,
                "status": "success",
                "settlement_details": settlement,
                "final_tax_calculation": final_tax,
                "form16_data": form16_data,
                "tds_adjustment": tds_adjustment,
                "final_payout": final_payout,
                "compliance_reports": compliance_reports,
                "processing_date": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed employee exit: {profile.employee_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing employee exit {profile.employee_id}: {str(e)}")
            raise
    
    def handle_salary_revision(self, profile: SalaryRevisionProfile) -> Dict[str, Any]:
        """Handle salary revision with tax implications"""
        try:
            self.logger.info(f"Processing salary revision for: {profile.employee_id}")
            
            # 1. Calculate salary change impact
            salary_impact = self._calculate_salary_change_impact(profile)
            
            # 2. Handle retroactive payments if applicable
            retroactive_impact = None
            if profile.is_retroactive:
                retroactive_impact = self._calculate_retroactive_impact(profile)
            
            # 3. Recalculate annual tax projection
            new_projection = self._recalculate_annual_projection(profile, salary_impact)
            
            # 4. Calculate catch-up tax
            catch_up_tax = self._calculate_catch_up_tax_for_revision(profile, new_projection)
            
            # 5. Update future payouts
            payout_updates = self._update_payouts_for_revision(profile, catch_up_tax)
            
            # 6. Generate revision documents
            revision_docs = self._generate_revision_documents(profile, salary_impact)
            
            # 7. Publish salary change event
            self.event_processor.process_salary_change(
                profile.employee_id,
                sum(profile.old_salary_structure.values()) * 12,
                sum(profile.new_salary_structure.values()) * 12,
                profile.effective_date,
                profile.revision_type
            )
            
            result = {
                "employee_id": profile.employee_id,
                "status": "success",
                "salary_impact": salary_impact,
                "retroactive_impact": retroactive_impact,
                "new_projection": new_projection,
                "catch_up_tax": catch_up_tax,
                "payout_updates": payout_updates,
                "revision_documents": revision_docs,
                "processing_date": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed salary revision: {profile.employee_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing salary revision {profile.employee_id}: {str(e)}")
            raise
    
    def handle_mid_year_regime_change(self, employee_id: str, new_regime: str, 
                                    effective_date: date) -> Dict[str, Any]:
        """Handle mid-year tax regime change"""
        try:
            self.logger.info(f"Processing regime change for {employee_id} to {new_regime}")
            
            # 1. Get current tax calculation
            current_context = self._get_current_tax_context(employee_id)
            old_regime = current_context.regime
            
            # 2. Calculate tax impact of regime change
            regime_impact = self._calculate_regime_change_impact(
                current_context, new_regime, effective_date
            )
            
            # 3. Recalculate remaining year tax
            remaining_months = self._get_remaining_months(effective_date)
            new_monthly_tds = regime_impact["new_annual_tax"] / remaining_months
            
            # 4. Update future payouts
            payout_updates = self.payout_service.update_future_payouts_tds(
                employee_id, new_monthly_tds
            )
            
            # 5. Generate regime change documentation
            regime_docs = self._generate_regime_change_docs(
                employee_id, old_regime, new_regime, regime_impact
            )
            
            # 6. Publish regime change event
            self.event_processor.process_regime_change(employee_id, old_regime, new_regime)
            
            result = {
                "employee_id": employee_id,
                "status": "success",
                "old_regime": old_regime,
                "new_regime": new_regime,
                "effective_date": effective_date.isoformat(),
                "regime_impact": regime_impact,
                "new_monthly_tds": new_monthly_tds,
                "payout_updates": payout_updates,
                "documentation": regime_docs,
                "processing_date": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed regime change for {employee_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing regime change for {employee_id}: {str(e)}")
            raise
    
    def handle_lwp_scenario(self, employee_id: str, lwp_start: date, 
                          lwp_end: date, lwp_type: str) -> Dict[str, Any]:
        """Handle Leave Without Pay scenarios"""
        try:
            self.logger.info(f"Processing LWP for {employee_id} from {lwp_start} to {lwp_end}")
            
            # 1. Calculate LWP impact on salary
            lwp_impact = self._calculate_lwp_impact(employee_id, lwp_start, lwp_end, lwp_type)
            
            # 2. Recalculate annual projection with LWP
            adjusted_projection = self._recalculate_projection_with_lwp(employee_id, lwp_impact)
            
            # 3. Calculate tax adjustment
            tax_adjustment = self._calculate_tax_adjustment_for_lwp(employee_id, adjusted_projection)
            
            # 4. Update affected payouts
            payout_updates = self._update_payouts_for_lwp(employee_id, lwp_impact, tax_adjustment)
            
            # 5. Generate LWP documentation
            lwp_docs = self._generate_lwp_documentation(employee_id, lwp_impact, tax_adjustment)
            
            result = {
                "employee_id": employee_id,
                "status": "success",
                "lwp_period": f"{lwp_start} to {lwp_end}",
                "lwp_type": lwp_type,
                "lwp_impact": lwp_impact,
                "adjusted_projection": adjusted_projection,
                "tax_adjustment": tax_adjustment,
                "payout_updates": payout_updates,
                "documentation": lwp_docs,
                "processing_date": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed LWP for {employee_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing LWP for {employee_id}: {str(e)}")
            raise
    
    def handle_bonus_payment(self, employee_id: str, bonus_amount: float, 
                           bonus_type: str, payment_date: date) -> Dict[str, Any]:
        """Handle bonus payments with tax implications"""
        try:
            self.logger.info(f"Processing bonus payment for {employee_id}: {bonus_amount}")
            
            # 1. Determine bonus tax treatment
            tax_treatment = self._determine_bonus_tax_treatment(bonus_type, bonus_amount)
            
            # 2. Calculate tax on bonus
            bonus_tax = self._calculate_bonus_tax(employee_id, bonus_amount, tax_treatment)
            
            # 3. Calculate TDS on bonus
            bonus_tds = self._calculate_bonus_tds(employee_id, bonus_amount, bonus_tax)
            
            # 4. Update annual tax projection
            updated_projection = self._update_projection_with_bonus(employee_id, bonus_amount)
            
            # 5. Adjust future TDS if needed
            tds_adjustment = self._calculate_future_tds_adjustment_for_bonus(
                employee_id, updated_projection
            )
            
            # 6. Process bonus payout
            bonus_payout = self._process_bonus_payout(
                employee_id, bonus_amount, bonus_tds, payment_date
            )
            
            result = {
                "employee_id": employee_id,
                "status": "success",
                "bonus_amount": bonus_amount,
                "bonus_type": bonus_type,
                "tax_treatment": tax_treatment,
                "bonus_tax": bonus_tax,
                "bonus_tds": bonus_tds,
                "updated_projection": updated_projection,
                "tds_adjustment": tds_adjustment,
                "bonus_payout": bonus_payout,
                "processing_date": datetime.now().isoformat()
            }
            
            self.logger.info(f"Successfully processed bonus payment for {employee_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing bonus payment for {employee_id}: {str(e)}")
            raise
    
    # Private helper methods
    
    def _calculate_new_joiner_projection(self, profile: NewJoinerProfile) -> Dict[str, Any]:
        """Calculate pro-rated salary projection for new joiner"""
        join_date = profile.join_date
        tax_year_end = date(join_date.year + 1 if join_date.month >= 4 else join_date.year, 3, 31)
        
        # Calculate remaining days in tax year
        remaining_days = (tax_year_end - join_date).days + 1
        total_days_in_year = 365
        
        # Pro-rate annual salary
        pro_rated_annual = profile.annual_salary * (remaining_days / total_days_in_year)
        
        return {
            "annual_salary": profile.annual_salary,
            "join_date": join_date.isoformat(),
            "tax_year_end": tax_year_end.isoformat(),
            "remaining_days": remaining_days,
            "pro_rated_annual": pro_rated_annual,
            "monthly_gross": profile.annual_salary / 12
        }
    
    def _handle_previous_employment(self, profile: NewJoinerProfile) -> Dict[str, Any]:
        """Handle previous employment tax implications"""
        if not profile.previous_employment:
            return {"has_previous_employment": False}
        
        # Calculate tax already paid in current financial year
        previous_tax_year_income = profile.previous_gross_salary
        previous_tds = profile.previous_tds_deducted
        
        return {
            "has_previous_employment": True,
            "previous_employer": profile.previous_employer_name,
            "previous_gross_salary": previous_tax_year_income,
            "previous_tds_deducted": previous_tds,
            "previous_pf_contribution": profile.previous_pf_contribution,
            "requires_form12ba": True,
            "tax_credit_available": previous_tds
        }
    
    def _create_tax_context_for_new_joiner(self, profile: NewJoinerProfile, 
                                         projection: Dict[str, Any],
                                         previous_tax: Dict[str, Any]) -> TaxCalculationContext:
        """Create tax calculation context for new joiner"""
        # This would integrate with your existing models
        # Placeholder implementation
        return TaxCalculationContext(
            employee_id=profile.employee_id,
            tax_year=self._get_current_tax_year(),
            calculation_date=datetime.now(),
            regime=profile.tax_regime_preference,
            age=profile.age,
            is_govt_employee=profile.is_govt_employee,
            previous_tax_paid=previous_tax.get("previous_tds_deducted", 0.0)
        )
    
    def _determine_optimal_regime(self, regime_comparison: Dict[str, TaxCalculationResult]) -> str:
        """Determine optimal tax regime based on comparison"""
        old_tax = regime_comparison["old"].total_tax
        new_tax = regime_comparison["new"].total_tax
        
        return "new" if new_tax < old_tax else "old"
    
    def _calculate_monthly_tds_for_new_joiner(self, context: TaxCalculationContext,
                                            regime: str, join_date: date) -> Dict[str, float]:
        """Calculate monthly TDS for new joiner"""
        remaining_months = self._get_remaining_months(join_date)
        
        # Calculate annual tax
        context.regime = regime
        tax_result = self.tax_engine.calculate_tax(context)
        
        # Distribute over remaining months
        monthly_tds = tax_result.total_tax / remaining_months if remaining_months > 0 else 0
        
        return {
            "annual_tax": tax_result.total_tax,
            "remaining_months": remaining_months,
            "monthly_tds": monthly_tds,
            "regime_used": regime
        }
    
    def _get_remaining_months(self, from_date: date) -> int:
        """Get remaining months in tax year from given date"""
        tax_year_end = date(from_date.year + 1 if from_date.month >= 4 else from_date.year, 3, 31)
        
        # Calculate remaining months
        if from_date.day == 1:
            remaining_months = (tax_year_end.year - from_date.year) * 12 + (tax_year_end.month - from_date.month) + 1
        else:
            remaining_months = (tax_year_end.year - from_date.year) * 12 + (tax_year_end.month - from_date.month)
        
        return max(0, remaining_months)
    
    def _get_current_tax_year(self) -> str:
        """Get current tax year string"""
        now = datetime.now()
        if now.month >= 4:
            return f"{now.year}-{now.year + 1}"
        else:
            return f"{now.year - 1}-{now.year}"
    
    def _setup_initial_payouts(self, profile: NewJoinerProfile, monthly_tds: Dict[str, float]) -> Dict[str, Any]:
        """Setup initial payout records for new joiner"""
        # Placeholder implementation
        return {
            "payouts_created": True,
            "monthly_tds_setup": monthly_tds["monthly_tds"],
            "start_month": profile.join_date.strftime("%Y-%m")
        }
    
    def _generate_new_joiner_compliance_docs(self, profile: NewJoinerProfile, 
                                           context: TaxCalculationContext) -> List[str]:
        """Generate compliance documents for new joiner"""
        docs = ["Employee Tax Setup Form", "TDS Declaration"]
        
        if profile.previous_employment:
            docs.append("Form 12BA Request")
            docs.append("Previous Employment Certificate")
        
        return docs
    
    # Additional helper methods would be implemented similarly...
    # For brevity, I'm showing the structure and key methods
    
    def _calculate_final_settlement(self, profile: ExitProfile) -> Dict[str, Any]:
        """Calculate final settlement components"""
        # Implementation for final settlement calculation
        pass
    
    def _calculate_salary_change_impact(self, profile: SalaryRevisionProfile) -> Dict[str, Any]:
        """Calculate impact of salary change"""
        # Implementation for salary change impact
        pass
    
    def _get_current_tax_context(self, employee_id: str) -> TaxCalculationContext:
        """Get current tax context for employee"""
        # Implementation to fetch current context
        pass 