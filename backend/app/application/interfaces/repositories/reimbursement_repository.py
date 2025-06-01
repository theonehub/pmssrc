"""
Reimbursement Repository Interfaces
Repository abstractions for reimbursement operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.domain.entities.reimbursement_type_entity import ReimbursementTypeEntity
from app.domain.entities.reimbursement import Reimbursement
from app.application.dto.reimbursement_dto import (
    ReimbursementSearchFiltersDTO,
    ReimbursementStatisticsDTO
)


# Reimbursement Type Repositories

class ReimbursementTypeCommandRepository(ABC):
    """
    Repository interface for reimbursement type write operations.
    
    Follows Interface Segregation Principle by focusing only on command operations.
    """
    
    @abstractmethod
    async def save(self, reimbursement_type: ReimbursementTypeEntity) -> ReimbursementTypeEntity:
        """Save a new reimbursement type"""
        pass
    
    @abstractmethod
    async def update(self, reimbursement_type: ReimbursementTypeEntity) -> ReimbursementTypeEntity:
        """Update an existing reimbursement type"""
        pass
    
    @abstractmethod
    async def delete(self, type_id: str) -> bool:
        """Delete a reimbursement type (soft delete)"""
        pass
    
    @abstractmethod
    async def activate(self, type_id: str, updated_by: str) -> bool:
        """Activate a reimbursement type"""
        pass
    
    @abstractmethod
    async def deactivate(self, type_id: str, updated_by: str, reason: Optional[str] = None) -> bool:
        """Deactivate a reimbursement type"""
        pass


class ReimbursementTypeQueryRepository(ABC):
    """
    Repository interface for reimbursement type read operations.
    
    Follows Interface Segregation Principle by focusing only on query operations.
    """
    
    @abstractmethod
    async def get_by_id(self, type_id: str) -> Optional[ReimbursementTypeEntity]:
        """Get reimbursement type by ID"""
        pass
    
    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[ReimbursementTypeEntity]:
        """Get reimbursement type by code"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[ReimbursementTypeEntity]:
        """Get all reimbursement types"""
        pass
    
    @abstractmethod
    async def get_active(self) -> List[ReimbursementTypeEntity]:
        """Get all active reimbursement types"""
        pass
    
    @abstractmethod
    async def get_by_category(self, category: str) -> List[ReimbursementTypeEntity]:
        """Get reimbursement types by category"""
        pass
    
    @abstractmethod
    async def search(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[ReimbursementTypeEntity]:
        """Search reimbursement types with filters"""
        pass
    
    @abstractmethod
    async def exists_by_code(self, code: str, exclude_id: Optional[str] = None) -> bool:
        """Check if reimbursement type code exists"""
        pass


class ReimbursementTypeAnalyticsRepository(ABC):
    """
    Repository interface for reimbursement type analytics operations.
    
    Follows Interface Segregation Principle by focusing only on analytics.
    """
    
    @abstractmethod
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for reimbursement types"""
        pass
    
    @abstractmethod
    async def get_category_breakdown(self) -> Dict[str, int]:
        """Get breakdown by category"""
        pass
    
    @abstractmethod
    async def get_approval_level_distribution(self) -> Dict[str, int]:
        """Get distribution by approval level"""
        pass


# Reimbursement Request Repositories

class ReimbursementCommandRepository(ABC):
    """
    Repository interface for reimbursement write operations.
    
    Follows Interface Segregation Principle by focusing only on command operations.
    """
    
    @abstractmethod
    async def save(self, reimbursement: Reimbursement) -> Reimbursement:
        """Save a new reimbursement request"""
        pass
    
    @abstractmethod
    async def update(self, reimbursement: Reimbursement) -> Reimbursement:
        """Update an existing reimbursement request"""
        pass
    
    @abstractmethod
    async def delete(self, request_id: str) -> bool:
        """Delete a reimbursement request (soft delete)"""
        pass
    
    @abstractmethod
    async def submit_request(self, request_id: str, submitted_by: str) -> bool:
        """Submit reimbursement request for approval"""
        pass
    
    @abstractmethod
    async def approve_request(
        self,
        request_id: str,
        approved_by: str,
        approved_amount: Optional[Decimal] = None,
        approval_level: str = "manager",
        comments: Optional[str] = None
    ) -> bool:
        """Approve reimbursement request"""
        pass
    
    @abstractmethod
    async def reject_request(
        self,
        request_id: str,
        rejected_by: str,
        rejection_reason: str
    ) -> bool:
        """Reject reimbursement request"""
        pass
    
    @abstractmethod
    async def cancel_request(
        self,
        request_id: str,
        cancelled_by: str,
        cancellation_reason: Optional[str] = None
    ) -> bool:
        """Cancel reimbursement request"""
        pass
    
    @abstractmethod
    async def process_payment(
        self,
        request_id: str,
        paid_by: str,
        payment_method: str,
        payment_reference: Optional[str] = None,
        bank_details: Optional[str] = None
    ) -> bool:
        """Process payment for approved reimbursement"""
        pass
    
    @abstractmethod
    async def upload_receipt(
        self,
        request_id: str,
        file_path: str,
        file_name: str,
        file_size: int,
        uploaded_by: str
    ) -> bool:
        """Upload receipt for reimbursement"""
        pass
    
    @abstractmethod
    async def bulk_approve(
        self,
        request_ids: List[str],
        approved_by: str,
        approval_criteria: str
    ) -> Dict[str, bool]:
        """Bulk approve multiple reimbursement requests"""
        pass


class ReimbursementQueryRepository(ABC):
    """
    Repository interface for reimbursement read operations.
    
    Follows Interface Segregation Principle by focusing only on query operations.
    """
    
    @abstractmethod
    async def get_by_id(self, request_id: str) -> Optional[Reimbursement]:
        """Get reimbursement by ID"""
        pass
    
    @abstractmethod
    async def get_by_employee_id(self, employee_id: str) -> List[Reimbursement]:
        """Get reimbursements by employee ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Reimbursement]:
        """Get all reimbursements"""
        pass
    
    @abstractmethod
    async def get_by_status(self, status: str) -> List[Reimbursement]:
        """Get reimbursements by status"""
        pass
    
    @abstractmethod
    async def get_pending_approval(self) -> List[Reimbursement]:
        """Get reimbursements pending approval"""
        pass
    
    @abstractmethod
    async def get_approved(self) -> List[Reimbursement]:
        """Get approved reimbursements"""
        pass
    
    @abstractmethod
    async def get_paid(self) -> List[Reimbursement]:
        """Get paid reimbursements"""
        pass
    
    @abstractmethod
    async def get_by_reimbursement_type(self, type_id: str) -> List[Reimbursement]:
        """Get reimbursements by type"""
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Reimbursement]:
        """Get reimbursements within date range"""
        pass
    
    @abstractmethod
    async def search(self, filters: ReimbursementSearchFiltersDTO) -> List[Reimbursement]:
        """Search reimbursements with filters"""
        pass
    
    @abstractmethod
    async def get_employee_reimbursements_by_period(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime,
        reimbursement_type_id: Optional[str] = None
    ) -> List[Reimbursement]:
        """Get employee reimbursements for a specific period"""
        pass
    
    @abstractmethod
    async def get_total_amount_by_employee_and_type(
        self,
        employee_id: str,
        reimbursement_type_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """Get total reimbursement amount for employee by type and period"""
        pass


class ReimbursementAnalyticsRepository(ABC):
    """
    Repository interface for reimbursement analytics operations.
    
    Follows Interface Segregation Principle by focusing only on analytics.
    """
    
    @abstractmethod
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ReimbursementStatisticsDTO:
        """Get reimbursement statistics"""
        pass
    
    @abstractmethod
    async def get_employee_statistics(
        self,
        employee_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics for specific employee"""
        pass
    
    @abstractmethod
    async def get_category_wise_spending(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Decimal]:
        """Get spending breakdown by category"""
        pass
    
    @abstractmethod
    async def get_monthly_trends(
        self,
        months: int = 12
    ) -> Dict[str, Dict[str, Any]]:
        """Get monthly spending trends"""
        pass
    
    @abstractmethod
    async def get_approval_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get approval metrics and turnaround times"""
        pass
    
    @abstractmethod
    async def get_top_spenders(
        self,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top spending employees"""
        pass
    
    @abstractmethod
    async def get_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get compliance report with policy violations"""
        pass
    
    @abstractmethod
    async def get_payment_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get payment method analytics"""
        pass


class ReimbursementReportRepository(ABC):
    """
    Repository interface for reimbursement reporting operations.
    
    Follows Interface Segregation Principle by focusing only on reporting.
    """
    
    @abstractmethod
    async def generate_employee_report(
        self,
        employee_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate detailed employee reimbursement report"""
        pass
    
    @abstractmethod
    async def generate_department_report(
        self,
        department: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate department-wise reimbursement report"""
        pass
    
    @abstractmethod
    async def generate_tax_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate tax-related reimbursement report"""
        pass
    
    @abstractmethod
    async def generate_audit_trail(
        self,
        request_id: str
    ) -> List[Dict[str, Any]]:
        """Generate audit trail for a reimbursement request"""
        pass
    
    @abstractmethod
    async def export_to_excel(
        self,
        filters: ReimbursementSearchFiltersDTO,
        file_path: str
    ) -> str:
        """Export reimbursement data to Excel"""
        pass


# Composite Repository Interface

class ReimbursementRepository(ABC):
    """
    Composite repository interface combining all reimbursement operations.
    
    This can be used when you need access to multiple repository types
    in a single use case, but generally prefer the segregated interfaces.
    """
    
    @property
    @abstractmethod
    def reimbursement_types(self) -> ReimbursementTypeQueryRepository:
        """Get reimbursement type query repository"""
        pass
    
    @property
    @abstractmethod
    def reimbursement_type_commands(self) -> ReimbursementTypeCommandRepository:
        """Get reimbursement type command repository"""
        pass
    
    @property
    @abstractmethod
    def reimbursements(self) -> ReimbursementQueryRepository:
        """Get reimbursement query repository"""
        pass
    
    @property
    @abstractmethod
    def reimbursement_commands(self) -> ReimbursementCommandRepository:
        """Get reimbursement command repository"""
        pass
    
    @property
    @abstractmethod
    def analytics(self) -> ReimbursementAnalyticsRepository:
        """Get analytics repository"""
        pass
    
    @property
    @abstractmethod
    def reports(self) -> ReimbursementReportRepository:
        """Get reports repository"""
        pass 