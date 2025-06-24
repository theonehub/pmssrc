"""
Personal Investment Declarations
Wrapper entity for employee self-declared investments and deductions
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import date

from app.domain.value_objects.money import Money
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.entities.taxation.deductions import (
    TaxDeductions, DeductionSection80C, DeductionSection80CCC, DeductionSection80CCD,
    DeductionSection80D, DeductionSection80DD, DeductionSection80DDB, DeductionSection80E,
    DeductionSection80EEB, DeductionSection80G, DeductionSection80GGC, DeductionSection80U,
    DeductionSection80TTA_TTB, OtherDeductions,
    DisabilityPercentage, RelationType
)


@dataclass
class PersonalInvestmentDeclaration:
    """
    Employee personal investment declaration.
    Uses existing TaxDeductions computation logic.
    """
    
    # Employee identifiers
    employee_id: EmployeeId
    organization_id: str
    tax_year: str
    
    # Declaration status
    declaration_status: str = "draft"  # draft, submitted, approved, rejected
    
    # Section 80C Investments (employee declared)
    section_80c_investments: Dict[str, float] = field(default_factory=dict)
    
    # Section 80D Health Insurance (employee declared)
    health_insurance_declarations: Dict[str, Any] = field(default_factory=dict)
    
    # Section 80CCD NPS (employee declared)
    nps_declarations: Dict[str, float] = field(default_factory=dict)
    
    # Section 80E Education Loan (employee declared)
    education_loan_interest: float = 0.0
    
    # Section 80G Donations (employee declared)
    charitable_donations: Dict[str, float] = field(default_factory=dict)
    
    # Section 80EEB Electric Vehicle Loan (employee declared)
    ev_loan_declarations: Dict[str, Any] = field(default_factory=dict)
    
    # Section 80U/80DD Disability (employee declared)
    disability_declarations: Dict[str, Any] = field(default_factory=dict)
    
    # Section 80DDB Medical Treatment (employee declared)
    medical_treatment_declarations: Dict[str, Any] = field(default_factory=dict)
    
    # Section 80TTA/TTB Interest (employee declared)
    interest_income_declarations: Dict[str, float] = field(default_factory=dict)
    
    # Other deductions (employee declared)
    other_investment_declarations: Dict[str, float] = field(default_factory=dict)
    
    # Declaration metadata
    declared_by: str = ""
    declared_at: Optional[str] = None
    submitted_at: Optional[str] = None
    approved_by: str = ""
    approved_at: Optional[str] = None
    
    # Proof documents tracking
    proof_documents_uploaded: Dict[str, List[str]] = field(default_factory=dict)
    
    def create_tax_deductions(self, employee_age: int = 30) -> TaxDeductions:
        """
        Create TaxDeductions entity using existing computation logic.
        Employee declarations are used to populate the deduction sections.
        """
        
        # Section 80C - Employee investments
        section_80c = DeductionSection80C(
            life_insurance_premium=Money.from_float(self.section_80c_investments.get('lic_premium', 0)),
            epf_contribution=Money.from_float(self.section_80c_investments.get('epf_employee', 0)),
            ppf_contribution=Money.from_float(self.section_80c_investments.get('ppf', 0)),
            nsc_investment=Money.from_float(self.section_80c_investments.get('nsc', 0)),
            tax_saving_fd=Money.from_float(self.section_80c_investments.get('tax_saving_fd', 0)),
            elss_investment=Money.from_float(self.section_80c_investments.get('elss', 0)),
            home_loan_principal=Money.from_float(self.section_80c_investments.get('home_loan_principal', 0)),
            tuition_fees=Money.from_float(self.section_80c_investments.get('tuition_fees', 0)),
            ulip_premium=Money.from_float(self.section_80c_investments.get('ulip', 0)),
            sukanya_samriddhi=Money.from_float(self.section_80c_investments.get('sukanya_samriddhi', 0)),
            stamp_duty_property=Money.from_float(self.section_80c_investments.get('stamp_duty', 0)),
            senior_citizen_savings=Money.from_float(self.section_80c_investments.get('senior_citizen_savings', 0)),
            other_80c_investments=Money.from_float(self.section_80c_investments.get('others', 0))
        )
        
        # Section 80CCC - Employee pension fund
        section_80ccc = DeductionSection80CCC(
            pension_fund_contribution=Money.from_float(self.section_80c_investments.get('pension_fund', 0))
        )
        
        # Section 80CCD - Employee NPS
        section_80ccd = DeductionSection80CCD(
            employee_nps_contribution=Money.from_float(self.nps_declarations.get('employee_nps', 0)),
            additional_nps_contribution=Money.from_float(self.nps_declarations.get('additional_nps', 0)),
            employer_nps_contribution=Money.from_float(self.nps_declarations.get('employer_nps', 0))
        )
        
        # Section 80D - Employee health insurance
        health_data = self.health_insurance_declarations
        section_80d = DeductionSection80D(
            self_family_premium=Money.from_float(health_data.get('self_family_premium', 0)),
            parent_premium=Money.from_float(health_data.get('parent_premium', 0)),
            preventive_health_checkup=Money.from_float(health_data.get('preventive_checkup', 0)),
            parent_age=health_data.get('parent_age', 55)
        )
        
        # Section 80E - Employee education loan
        section_80e = None
        if self.education_loan_interest > 0:
            section_80e = DeductionSection80E(
                education_loan_interest=Money.from_float(self.education_loan_interest),
                relation=RelationType.SELF
            )
        
        # Section 80EEB - Employee EV loan
        section_80eeb = None
        if self.ev_loan_declarations:
            ev_data = self.ev_loan_declarations
            section_80eeb = DeductionSection80EEB(
                ev_loan_interest=Money.from_float(ev_data.get('interest_amount', 0)),
                ev_purchase_date=date.fromisoformat(ev_data['purchase_date']) if ev_data.get('purchase_date') else None
            )
        
        # Section 80G - Employee donations
        section_80g = None
        if self.charitable_donations:
            section_80g = DeductionSection80G(
                pm_relief_fund=Money.from_float(self.charitable_donations.get('pm_relief_fund', 0)),
                national_defence_fund=Money.from_float(self.charitable_donations.get('national_defence_fund', 0)),
                cm_relief_fund=Money.from_float(self.charitable_donations.get('cm_relief_fund', 0)),
                govt_charitable_donations=Money.from_float(self.charitable_donations.get('govt_charitable', 0)),
                other_charitable_donations=Money.from_float(self.charitable_donations.get('other_charitable', 0)),
                swachh_bharat_kosh=Money.from_float(self.charitable_donations.get('swachh_bharat_kosh', 0)),
                clean_ganga_fund=Money.from_float(self.charitable_donations.get('clean_ganga_fund', 0)),
                # Add other donation categories as needed
            )
        
        # Section 80GGC - Employee political donations
        section_80ggc = None
        if self.other_investment_declarations.get('political_donation', 0) > 0:
            section_80ggc = DeductionSection80GGC(
                political_party_contribution=Money.from_float(self.other_investment_declarations['political_donation'])
            )
        
        # Section 80U - Employee disability
        section_80u = None
        if self.disability_declarations.get('self_disability'):
            disability_data = self.disability_declarations['self_disability']
            section_80u = DeductionSection80U(
                disability_percentage=DisabilityPercentage(disability_data['percentage'])
            )
        
        # Section 80DD - Employee dependent disability
        section_80dd = None
        if self.disability_declarations.get('dependent_disability'):
            dependent_data = self.disability_declarations['dependent_disability']
            section_80dd = DeductionSection80DD(
                relation=RelationType(dependent_data['relation']),
                disability_percentage=DisabilityPercentage(dependent_data['percentage'])
            )
        
        # Section 80DDB - Employee medical treatment
        section_80ddb = None
        if self.medical_treatment_declarations:
            medical_data = self.medical_treatment_declarations
            section_80ddb = DeductionSection80DDB(
                dependent_age=medical_data.get('dependent_age', employee_age),
                medical_expenses=Money.from_float(medical_data.get('medical_expenses', 0)),
                relation=RelationType(medical_data.get('relation', 'Self'))
            )
        
        # Section 80TTA/TTB - Employee interest income
        section_80tta_ttb = None
        if self.interest_income_declarations:
            interest_data = self.interest_income_declarations
            section_80tta_ttb = DeductionSection80TTA_TTB(
                savings_interest=Money.from_float(interest_data.get('savings_interest', 0)),
                fd_interest=Money.from_float(interest_data.get('fd_interest', 0)),
                rd_interest=Money.from_float(interest_data.get('rd_interest', 0)),
                post_office_interest=Money.from_float(interest_data.get('post_office_interest', 0)),
                age=employee_age
            )
        
        # Other deductions
        other_deductions = OtherDeductions(
            education_loan_interest=Money.from_float(self.education_loan_interest),
            charitable_donations=Money.from_float(sum(self.charitable_donations.values())),
            savings_interest=Money.from_float(self.interest_income_declarations.get('savings_interest', 0)),
            nps_contribution=Money.from_float(self.nps_declarations.get('additional_nps', 0)),
            other_deductions=Money.from_float(self.other_investment_declarations.get('others', 0))
        )
        
        # Create TaxDeductions entity using existing computation logic - NO CHANGES
        return TaxDeductions(
            section_80c=section_80c,
            section_80ccc=section_80ccc,
            section_80ccd=section_80ccd,
            section_80d=section_80d,
            section_80dd=section_80dd,
            section_80ddb=section_80ddb,
            section_80e=section_80e,
            section_80eeb=section_80eeb,
            section_80g=section_80g,
            section_80ggc=section_80ggc,
            section_80u=section_80u,
            section_80tta_ttb=section_80tta_ttb,
            other_deductions=other_deductions
        )
    
    def get_investment_summary(self) -> Dict[str, Any]:
        """Get employee investment declaration summary."""
        return {
            "employee_info": {
                "employee_id": str(self.employee_id),
                "organization_id": self.organization_id,
                "tax_year": self.tax_year
            },
            "declaration_status": self.declaration_status,
            "section_80c_total": sum(self.section_80c_investments.values()),
            "health_insurance_total": sum(v for v in self.health_insurance_declarations.values() if isinstance(v, (int, float))),
            "nps_total": sum(self.nps_declarations.values()),
            "charitable_donations_total": sum(self.charitable_donations.values()),
            "education_loan_interest": self.education_loan_interest,
            "interest_income_total": sum(self.interest_income_declarations.values()),
            "proof_documents_status": {
                section: len(docs) for section, docs in self.proof_documents_uploaded.items()
            },
            "declaration_metadata": {
                "declared_by": self.declared_by,
                "declared_at": self.declared_at,
                "submitted_at": self.submitted_at,
                "approved_by": self.approved_by,
                "approved_at": self.approved_at
            }
        }
    
    def update_section_80c_investment(self, investment_type: str, amount: float) -> bool:
        """Update specific 80C investment."""
        valid_investments = [
            'lic_premium', 'epf_employee', 'ppf', 'nsc', 'tax_saving_fd', 'elss',
            'home_loan_principal', 'tuition_fees', 'ulip', 'sukanya_samriddhi',
            'stamp_duty', 'senior_citizen_savings', 'pension_fund', 'others'
        ]
        
        if investment_type in valid_investments:
            self.section_80c_investments[investment_type] = amount
            return True
        return False
    
    def update_health_insurance(self, insurance_data: Dict[str, Any]) -> bool:
        """Update health insurance declarations."""
        self.health_insurance_declarations.update(insurance_data)
        return True
    
    def add_proof_document(self, section: str, document_id: str) -> bool:
        """Add proof document for a section."""
        if section not in self.proof_documents_uploaded:
            self.proof_documents_uploaded[section] = []
        
        if document_id not in self.proof_documents_uploaded[section]:
            self.proof_documents_uploaded[section].append(document_id)
            return True
        return False
    
    def submit_declaration(self, submitted_by: str) -> bool:
        """Submit declaration for approval."""
        if self.declaration_status == "draft":
            self.declaration_status = "submitted"
            self.submitted_at = str(date.today())
            self.declared_by = submitted_by
            return True
        return False
    
    def approve_declaration(self, approved_by: str) -> bool:
        """Approve employee declaration."""
        if self.declaration_status == "submitted":
            self.declaration_status = "approved"
            self.approved_at = str(date.today())
            self.approved_by = approved_by
            return True
        return False
    
    def reject_declaration(self, rejected_by: str, reason: str = "") -> bool:
        """Reject employee declaration."""
        if self.declaration_status == "submitted":
            self.declaration_status = "rejected"
            self.approved_by = rejected_by
            self.approved_at = str(date.today())
            # Could add rejection reason tracking
            return True
        return False
    
    def validate_declaration(self) -> List[str]:
        """Validate employee investment declaration."""
        warnings = []
        
        # Check 80C limit
        total_80c = sum(self.section_80c_investments.values())
        if total_80c > 150000:
            warnings.append(f"Section 80C investments exceed limit: ₹{total_80c:,.2f} > ₹1,50,000")
        
        # Check health insurance details
        if self.health_insurance_declarations.get('parent_premium', 0) > 0:
            if not self.health_insurance_declarations.get('parent_age'):
                warnings.append("Parent age required for parent health insurance premium")
        
        # Check proof documents
        if total_80c > 0 and not self.proof_documents_uploaded.get('section_80c'):
            warnings.append("Proof documents required for Section 80C investments")
        
        if self.health_insurance_declarations.get('self_family_premium', 0) > 0:
            if not self.proof_documents_uploaded.get('section_80d'):
                warnings.append("Health insurance premium receipts required")
        
        if self.education_loan_interest > 0:
            if not self.proof_documents_uploaded.get('section_80e'):
                warnings.append("Education loan interest certificate required")
        
        return warnings 