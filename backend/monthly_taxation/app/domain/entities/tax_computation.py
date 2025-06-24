"""
Tax Computation Domain Entity
Core entity for Indian income tax calculations
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from decimal import Decimal
from enum import Enum

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_computation_id import TaxComputationId
from app.domain.exceptions.tax_computation_exceptions import TaxComputationValidationError


class TaxRegime(Enum):
    """Indian Income Tax Regimes"""
    OLD_REGIME = "OLD_REGIME"
    NEW_REGIME = "NEW_REGIME"


class TaxSlab(Enum):
    """Income tax slabs for FY 2023-24"""
    SLAB_0 = "0"      # Up to ₹2.5 lakh - 0%
    SLAB_5 = "5"      # ₹2.5-5 lakh - 5%
    SLAB_10 = "10"    # ₹5-7.5 lakh - 10% (Old) / ₹5-7.5 lakh - 10% (New)
    SLAB_15 = "15"    # ₹7.5-10 lakh - 15% (Old) / ₹7.5-10 lakh - 15% (New)
    SLAB_20 = "20"    # ₹10-12.5 lakh - 20% (Old) / ₹10-12.5 lakh - 20% (New)
    SLAB_25 = "25"    # ₹12.5-15 lakh - 25% (Old) / ₹12.5-15 lakh - 25% (New)
    SLAB_30 = "30"    # Above ₹15 lakh - 30%


@dataclass
class ExemptionCalculation:
    """Calculation details for a specific exemption"""
    exemption_section: str
    eligible_amount: Decimal
    claimed_amount: Decimal
    allowed_amount: Decimal
    calculation_details: Dict[str, Any]
    
    def get_benefit_amount(self) -> Decimal:
        """Get the tax benefit from this exemption"""
        return self.allowed_amount


@dataclass
class DeductionCalculation:
    """Calculation details for deductions under Chapter VI-A"""
    section: str  # 80C, 80D, 80G, etc.
    eligible_amount: Decimal
    claimed_amount: Decimal
    allowed_amount: Decimal
    limit: Decimal
    calculation_details: Dict[str, Any]


@dataclass
class TaxSlabCalculation:
    """Tax calculation for a specific slab"""
    slab_rate: Decimal
    slab_min: Decimal
    slab_max: Optional[Decimal]
    taxable_income_in_slab: Decimal
    tax_amount: Decimal


@dataclass
class MonthlyTDSProjection:
    """Monthly TDS projection and actual deduction"""
    month: int
    year: int
    projected_tds: Decimal
    actual_tds: Decimal
    cumulative_tds: Decimal
    remaining_tax_liability: Decimal


@dataclass
class TaxComputation:
    """
    Domain entity for comprehensive income tax computation.
    
    Supports both Old and New tax regimes as per Indian Income Tax Act.
    """
    
    id: TaxComputationId
    employee_id: EmployeeId
    financial_year: str  # e.g., "2023-24"
    assessment_year: str  # e.g., "2024-25"
    tax_regime: TaxRegime
    computation_date: date
    
    # Income Components
    gross_salary: Decimal
    other_income: Decimal = Decimal('0')
    total_income: Decimal = Decimal('0')
    
    # Exemptions
    exemptions: List[ExemptionCalculation] = field(default_factory=list)
    total_exemptions: Decimal = Decimal('0')
    
    # Deductions
    standard_deduction: Decimal = Decimal('50000')  # FY 2023-24
    deductions: List[DeductionCalculation] = field(default_factory=list)
    total_deductions: Decimal = Decimal('0')
    
    # Taxable Income
    taxable_income: Decimal = Decimal('0')
    
    # Tax Calculation
    tax_slabs: List[TaxSlabCalculation] = field(default_factory=list)
    gross_tax: Decimal = Decimal('0')
    
    # Rebates and Cess
    rebate_87a: Decimal = Decimal('0')  # Rebate under section 87A
    health_education_cess: Decimal = Decimal('0')  # 4% cess
    net_tax: Decimal = Decimal('0')
    
    # TDS
    monthly_tds_projections: List[MonthlyTDSProjection] = field(default_factory=list)
    total_tds_deducted: Decimal = Decimal('0')
    
    # Final Liability
    final_tax_liability: Decimal = Decimal('0')
    refund_payable: Decimal = Decimal('0')
    additional_tax_due: Decimal = Decimal('0')
    
    # Metadata
    computed_by: Optional[str] = None
    is_finalized: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create(
        cls,
        id: TaxComputationId,
        employee_id: EmployeeId,
        financial_year: str,
        tax_regime: TaxRegime,
        gross_salary: Decimal,
        computed_by: str,
        other_income: Decimal = Decimal('0')
    ) -> 'TaxComputation':
        """Factory method to create new tax computation"""
        
        assessment_year = cls._get_assessment_year(financial_year)
        
        return cls(
            id=id,
            employee_id=employee_id,
            financial_year=financial_year,
            assessment_year=assessment_year,
            tax_regime=tax_regime,
            computation_date=date.today(),
            gross_salary=gross_salary,
            other_income=other_income,
            computed_by=computed_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def add_exemption(
        self,
        section: str,
        eligible_amount: Decimal,
        claimed_amount: Decimal,
        calculation_details: Dict[str, Any] = None
    ) -> 'TaxComputation':
        """Add an exemption calculation"""
        
        allowed_amount = min(eligible_amount, claimed_amount)
        
        exemption = ExemptionCalculation(
            exemption_section=section,
            eligible_amount=eligible_amount,
            claimed_amount=claimed_amount,
            allowed_amount=allowed_amount,
            calculation_details=calculation_details or {}
        )
        
        self.exemptions.append(exemption)
        self._recalculate_totals()
        return self
    
    def add_deduction(
        self,
        section: str,
        eligible_amount: Decimal,
        claimed_amount: Decimal,
        limit: Decimal,
        calculation_details: Dict[str, Any] = None
    ) -> 'TaxComputation':
        """Add a deduction under Chapter VI-A"""
        
        allowed_amount = min(min(eligible_amount, claimed_amount), limit)
        
        deduction = DeductionCalculation(
            section=section,
            eligible_amount=eligible_amount,
            claimed_amount=claimed_amount,
            allowed_amount=allowed_amount,
            limit=limit,
            calculation_details=calculation_details or {}
        )
        
        self.deductions.append(deduction)
        self._recalculate_totals()
        return self
    
    def calculate_tax(self) -> 'TaxComputation':
        """Perform complete tax calculation"""
        
        # Step 1: Calculate total income
        self.total_income = self.gross_salary + self.other_income
        
        # Step 2: Calculate total exemptions
        self.total_exemptions = sum(exemption.allowed_amount for exemption in self.exemptions)
        
        # Step 3: Calculate total deductions
        self.total_deductions = sum(deduction.allowed_amount for deduction in self.deductions)
        if self.tax_regime == TaxRegime.OLD_REGIME:
            self.total_deductions += self.standard_deduction
        
        # Step 4: Calculate taxable income
        taxable_before_deductions = self.total_income - self.total_exemptions
        if self.tax_regime == TaxRegime.NEW_REGIME:
            self.taxable_income = max(Decimal('0'), taxable_before_deductions - self.standard_deduction)
        else:
            self.taxable_income = max(Decimal('0'), taxable_before_deductions - self.total_deductions)
        
        # Step 5: Calculate tax as per slabs
        self._calculate_tax_slabs()
        
        # Step 6: Calculate rebate under 87A
        self._calculate_rebate_87a()
        
        # Step 7: Calculate cess
        self.health_education_cess = (self.gross_tax - self.rebate_87a) * Decimal('0.04')
        
        # Step 8: Calculate net tax
        self.net_tax = self.gross_tax - self.rebate_87a + self.health_education_cess
        
        # Step 9: Calculate final liability
        self.final_tax_liability = max(Decimal('0'), self.net_tax - self.total_tds_deducted)
        
        if self.net_tax < self.total_tds_deducted:
            self.refund_payable = self.total_tds_deducted - self.net_tax
        else:
            self.additional_tax_due = self.final_tax_liability
        
        self.updated_at = datetime.utcnow()
        return self
    
    def project_monthly_tds(self, annual_tax: Decimal) -> List[MonthlyTDSProjection]:
        """Project monthly TDS deductions"""
        monthly_tax = annual_tax / 12
        projections = []
        
        for month in range(1, 13):
            projection = MonthlyTDSProjection(
                month=month,
                year=int(self.financial_year.split('-')[0]) + (1 if month >= 4 else 0),
                projected_tds=monthly_tax,
                actual_tds=Decimal('0'),  # To be updated with actual deductions
                cumulative_tds=monthly_tax * month,
                remaining_tax_liability=annual_tax - (monthly_tax * month)
            )
            projections.append(projection)
        
        self.monthly_tds_projections = projections
        return projections
    
    def update_actual_tds(self, month: int, year: int, actual_amount: Decimal) -> 'TaxComputation':
        """Update actual TDS deducted for a month"""
        for projection in self.monthly_tds_projections:
            if projection.month == month and projection.year == year:
                projection.actual_tds = actual_amount
                break
        
        # Recalculate total TDS
        self.total_tds_deducted = sum(p.actual_tds for p in self.monthly_tds_projections)
        
        # Recalculate final liability
        if self.net_tax > 0:
            self.final_tax_liability = max(Decimal('0'), self.net_tax - self.total_tds_deducted)
            if self.net_tax < self.total_tds_deducted:
                self.refund_payable = self.total_tds_deducted - self.net_tax
                self.additional_tax_due = Decimal('0')
            else:
                self.additional_tax_due = self.final_tax_liability
                self.refund_payable = Decimal('0')
        
        self.updated_at = datetime.utcnow()
        return self
    
    def finalize_computation(self, finalized_by: str) -> 'TaxComputation':
        """Finalize the tax computation"""
        if not self.is_finalized:
            self.is_finalized = True
            self.computed_by = finalized_by
            self.updated_at = datetime.utcnow()
        return self
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """Get a summary of tax computation"""
        return {
            "employee_id": str(self.employee_id.value),
            "financial_year": self.financial_year,
            "tax_regime": self.tax_regime.value,
            "gross_salary": float(self.gross_salary),
            "total_income": float(self.total_income),
            "total_exemptions": float(self.total_exemptions),
            "total_deductions": float(self.total_deductions),
            "taxable_income": float(self.taxable_income),
            "gross_tax": float(self.gross_tax),
            "rebate_87a": float(self.rebate_87a),
            "health_education_cess": float(self.health_education_cess),
            "net_tax": float(self.net_tax),
            "total_tds_deducted": float(self.total_tds_deducted),
            "final_tax_liability": float(self.final_tax_liability),
            "refund_payable": float(self.refund_payable),
            "additional_tax_due": float(self.additional_tax_due),
            "is_finalized": self.is_finalized
        }
    
    def _calculate_tax_slabs(self):
        """Calculate tax as per income tax slabs"""
        self.tax_slabs.clear()
        self.gross_tax = Decimal('0')
        
        if self.tax_regime == TaxRegime.NEW_REGIME:
            slabs = self._get_new_regime_slabs()
        else:
            slabs = self._get_old_regime_slabs()
        
        remaining_income = self.taxable_income
        
        for slab_min, slab_max, rate in slabs:
            if remaining_income <= 0:
                break
            
            if remaining_income > slab_min:
                if slab_max:
                    taxable_in_slab = min(remaining_income - slab_min, slab_max - slab_min)
                else:
                    taxable_in_slab = remaining_income - slab_min
                
                tax_in_slab = taxable_in_slab * (rate / 100)
                
                slab_calc = TaxSlabCalculation(
                    slab_rate=rate,
                    slab_min=slab_min,
                    slab_max=slab_max,
                    taxable_income_in_slab=taxable_in_slab,
                    tax_amount=tax_in_slab
                )
                
                self.tax_slabs.append(slab_calc)
                self.gross_tax += tax_in_slab
    
    def _calculate_rebate_87a(self):
        """Calculate rebate under section 87A"""
        # Rebate of ₹12,500 if total income is up to ₹5 lakh
        if self.total_income <= Decimal('500000'):
            self.rebate_87a = min(self.gross_tax, Decimal('12500'))
        else:
            self.rebate_87a = Decimal('0')
    
    def _get_new_regime_slabs(self) -> List[tuple]:
        """Get tax slabs for new regime (FY 2023-24)"""
        return [
            (Decimal('0'), Decimal('250000'), Decimal('0')),
            (Decimal('250000'), Decimal('500000'), Decimal('5')),
            (Decimal('500000'), Decimal('750000'), Decimal('10')),
            (Decimal('750000'), Decimal('1000000'), Decimal('15')),
            (Decimal('1000000'), Decimal('1250000'), Decimal('20')),
            (Decimal('1250000'), Decimal('1500000'), Decimal('25')),
            (Decimal('1500000'), None, Decimal('30'))
        ]
    
    def _get_old_regime_slabs(self) -> List[tuple]:
        """Get tax slabs for old regime (FY 2023-24)"""
        return [
            (Decimal('0'), Decimal('250000'), Decimal('0')),
            (Decimal('250000'), Decimal('500000'), Decimal('5')),
            (Decimal('500000'), Decimal('1000000'), Decimal('20')),
            (Decimal('1000000'), None, Decimal('30'))
        ]
    
    def _recalculate_totals(self):
        """Recalculate totals when exemptions/deductions change"""
        self.total_exemptions = sum(exemption.allowed_amount for exemption in self.exemptions)
        self.total_deductions = sum(deduction.allowed_amount for deduction in self.deductions)
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def _get_assessment_year(financial_year: str) -> str:
        """Convert financial year to assessment year"""
        fy_start = int(financial_year.split('-')[0])
        ay_start = fy_start + 1
        ay_end = ay_start + 1
        return f"{ay_start}-{str(ay_end)[2:]}"
    
    def is_new(self) -> bool:
        """Check if this is a new computation"""
        return self.created_at is None 