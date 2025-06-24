"""
Personal Income Declarations
Wrapper entity for employee self-declared income from other sources
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import date

from app.domain.value_objects.money import Money
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome


@dataclass
class PersonalIncomeDeclaration:
    """
    Employee personal income declaration for income from other sources.
    Uses existing OtherIncome computation logic.
    """
    
    # Employee identifiers
    employee_id: EmployeeId
    organization_id: str
    tax_year: str
    
    # Declaration status
    declaration_status: str = "draft"  # draft, submitted, approved, rejected
    
    # House Property Income (employee declared)
    house_property_declarations: Dict[str, Any] = field(default_factory=dict)
    
    # Capital Gains (employee declared)
    capital_gains_declarations: Dict[str, float] = field(default_factory=dict)
    
    # Interest Income (employee declared)
    interest_income_declarations: Dict[str, float] = field(default_factory=dict)
    
    # Dividend Income (employee declared)
    dividend_income: float = 0.0
    
    # Business/Professional Income (employee declared)
    business_professional_income: float = 0.0
    
    # Other Miscellaneous Income (employee declared)
    other_miscellaneous_income: float = 0.0
    
    # Gifts Received (employee declared)
    gifts_received: float = 0.0
    
    # Declaration metadata
    declared_by: str = ""
    declared_at: Optional[str] = None
    submitted_at: Optional[str] = None
    approved_by: str = ""
    approved_at: Optional[str] = None
    
    # Proof documents tracking
    proof_documents_uploaded: Dict[str, List[str]] = field(default_factory=dict)
    
    def create_other_income(self) -> OtherIncome:
        """
        Create OtherIncome entity using existing computation logic.
        Employee declarations are used to populate the other income.
        """
        
        # House Property Income (if declared)
        house_property_income = None
        if self.house_property_declarations:
            house_data = self.house_property_declarations
            house_property_income = HousePropertyIncome(
                annual_rent_received=Money.from_float(house_data.get('annual_rent', 0)),
                municipal_taxes_paid=Money.from_float(house_data.get('municipal_taxes', 0)),
                standard_deduction_30_percent=house_data.get('standard_deduction_30_percent', True),
                interest_on_home_loan=Money.from_float(house_data.get('home_loan_interest', 0)),
                other_expenses=Money.from_float(house_data.get('other_expenses', 0)),
                is_self_occupied=house_data.get('is_self_occupied', False),
                is_deemed_let_out=house_data.get('is_deemed_let_out', False),
                property_type=house_data.get('property_type', 'Residential'),
                number_of_properties=house_data.get('number_of_properties', 1)
            )
        
        # Capital Gains Income (if declared)
        capital_gains_income = None
        if self.capital_gains_declarations:
            cg_data = self.capital_gains_declarations
            capital_gains_income = CapitalGainsIncome(
                # Short Term Capital Gains
                stcg_15_percent_equity=Money.from_float(cg_data.get('stcg_15_percent_equity', 0)),
                stcg_111a_equity_stt=Money.from_float(cg_data.get('stcg_111a_equity_stt', 0)),
                stcg_slab_rate_equity=Money.from_float(cg_data.get('stcg_slab_rate_equity', 0)),
                stcg_slab_rate_non_equity=Money.from_float(cg_data.get('stcg_slab_rate_non_equity', 0)),
                
                # Long Term Capital Gains
                ltcg_10_percent_equity=Money.from_float(cg_data.get('ltcg_10_percent_equity', 0)),
                ltcg_112a_equity_stt=Money.from_float(cg_data.get('ltcg_112a_equity_stt', 0)),
                ltcg_20_percent_with_indexation=Money.from_float(cg_data.get('ltcg_20_percent_with_indexation', 0)),
                ltcg_20_percent_without_indexation=Money.from_float(cg_data.get('ltcg_20_percent_without_indexation', 0)),
                
                # Exemptions
                exemption_54_residential_property=Money.from_float(cg_data.get('exemption_54', 0)),
                exemption_54f_residential_property=Money.from_float(cg_data.get('exemption_54f', 0)),
                exemption_54ec_bonds=Money.from_float(cg_data.get('exemption_54ec', 0)),
                exemption_38_compulsory_acquisition=Money.from_float(cg_data.get('exemption_38', 0)),
                exemption_54b_agricultural_land=Money.from_float(cg_data.get('exemption_54b', 0))
            )
        
        # Create OtherIncome entity using existing computation logic - NO CHANGES
        return OtherIncome(
            house_property_income=house_property_income,
            capital_gains_income=capital_gains_income,
            dividend_income=Money.from_float(self.dividend_income),
            business_professional_income=Money.from_float(self.business_professional_income),
            other_miscellaneous_income=Money.from_float(self.other_miscellaneous_income),
            gifts_received=Money.from_float(self.gifts_received),
            
            # Interest income components
            savings_bank_interest=Money.from_float(self.interest_income_declarations.get('savings_interest', 0)),
            fd_interest_taxable=Money.from_float(self.interest_income_declarations.get('fd_interest', 0)),
            bond_interest=Money.from_float(self.interest_income_declarations.get('bond_interest', 0)),
            post_office_interest_taxable=Money.from_float(self.interest_income_declarations.get('post_office_interest', 0)),
            other_interest_income=Money.from_float(self.interest_income_declarations.get('other_interest', 0))
        )
    
    def get_income_summary(self) -> Dict[str, Any]:
        """Get employee income declaration summary."""
        return {
            "employee_info": {
                "employee_id": str(self.employee_id),
                "organization_id": self.organization_id,
                "tax_year": self.tax_year
            },
            "declaration_status": self.declaration_status,
            "house_property_income": {
                "annual_rent": self.house_property_declarations.get('annual_rent', 0),
                "net_income_estimated": self.house_property_declarations.get('annual_rent', 0) * 0.7  # Rough estimate
            },
            "capital_gains_income": {
                "total_stcg": sum([
                    self.capital_gains_declarations.get('stcg_15_percent_equity', 0),
                    self.capital_gains_declarations.get('stcg_111a_equity_stt', 0),
                    self.capital_gains_declarations.get('stcg_slab_rate_equity', 0),
                    self.capital_gains_declarations.get('stcg_slab_rate_non_equity', 0)
                ]),
                "total_ltcg": sum([
                    self.capital_gains_declarations.get('ltcg_10_percent_equity', 0),
                    self.capital_gains_declarations.get('ltcg_112a_equity_stt', 0),
                    self.capital_gains_declarations.get('ltcg_20_percent_with_indexation', 0),
                    self.capital_gains_declarations.get('ltcg_20_percent_without_indexation', 0)
                ])
            },
            "other_income": {
                "dividend_income": self.dividend_income,
                "business_professional_income": self.business_professional_income,
                "other_miscellaneous_income": self.other_miscellaneous_income,
                "gifts_received": self.gifts_received
            },
            "interest_income": {
                "total_interest": sum(self.interest_income_declarations.values())
            },
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
    
    def update_house_property_income(self, property_data: Dict[str, Any]) -> bool:
        """Update house property income declaration."""
        self.house_property_declarations.update(property_data)
        return True
    
    def update_capital_gains(self, cg_type: str, amount: float) -> bool:
        """Update specific capital gains."""
        valid_cg_types = [
            'stcg_15_percent_equity', 'stcg_111a_equity_stt', 'stcg_slab_rate_equity',
            'stcg_slab_rate_non_equity', 'ltcg_10_percent_equity', 'ltcg_112a_equity_stt',
            'ltcg_20_percent_with_indexation', 'ltcg_20_percent_without_indexation',
            'exemption_54', 'exemption_54f', 'exemption_54ec', 'exemption_38', 'exemption_54b'
        ]
        
        if cg_type in valid_cg_types:
            self.capital_gains_declarations[cg_type] = amount
            return True
        return False
    
    def update_interest_income(self, interest_type: str, amount: float) -> bool:
        """Update specific interest income."""
        valid_interest_types = [
            'savings_interest', 'fd_interest', 'bond_interest', 'post_office_interest', 'other_interest'
        ]
        
        if interest_type in valid_interest_types:
            self.interest_income_declarations[interest_type] = amount
            return True
        return False
    
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
            return True
        return False
    
    def validate_declaration(self) -> List[str]:
        """Validate employee income declaration."""
        warnings = []
        
        # Check house property income
        if self.house_property_declarations.get('annual_rent', 0) > 0:
            if not self.house_property_declarations.get('municipal_taxes'):
                warnings.append("Municipal taxes information required for house property income")
            
            if not self.proof_documents_uploaded.get('house_property'):
                warnings.append("Rent receipts/agreement required for house property income")
        
        # Check capital gains
        total_cg = sum(self.capital_gains_declarations.values())
        if total_cg > 0:
            if not self.proof_documents_uploaded.get('capital_gains'):
                warnings.append("Capital gains transaction statements required")
        
        # Check dividend income
        if self.dividend_income > 0:
            if not self.proof_documents_uploaded.get('dividend_income'):
                warnings.append("Dividend statements required")
        
        # Check business income
        if self.business_professional_income > 0:
            if not self.proof_documents_uploaded.get('business_income'):
                warnings.append("Business income computation and P&L required")
        
        # Check interest income
        total_interest = sum(self.interest_income_declarations.values())
        if total_interest > 10000:  # Above 80TTA limit
            if not self.proof_documents_uploaded.get('interest_income'):
                warnings.append("Interest certificates required for income above ₹10,000")
        
        # Check gifts
        if self.gifts_received > 50000:  # Above taxable limit
            if not self.proof_documents_uploaded.get('gifts'):
                warnings.append("Gift documentation required for gifts above ₹50,000")
        
        return warnings 