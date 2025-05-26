"""
Company Leave Repository Interfaces
Defines contracts for company leave data persistence operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.entities.company_leave import CompanyLeave
from domain.value_objects.leave_type import LeaveType


class CompanyLeaveCommandRepository(ABC):
    """
    Command repository interface for company leave write operations.
    
    Follows SOLID principles:
    - SRP: Only handles company leave write operations
    - OCP: Can be implemented by different storage systems
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for command operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    def save(self, company_leave: CompanyLeave) -> bool:
        """
        Save company leave record.
        
        Args:
            company_leave: CompanyLeave entity to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def update(self, company_leave: CompanyLeave) -> bool:
        """
        Update existing company leave record.
        
        Args:
            company_leave: CompanyLeave entity to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, company_leave_id: str) -> bool:
        """
        Delete company leave record.
        
        Args:
            company_leave_id: Company leave identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class CompanyLeaveQueryRepository(ABC):
    """
    Query repository interface for company leave read operations.
    """
    
    @abstractmethod
    def get_by_id(self, company_leave_id: str) -> Optional[CompanyLeave]:
        """
        Get company leave by ID.
        
        Args:
            company_leave_id: Company leave identifier
            
        Returns:
            CompanyLeave entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_by_leave_type_code(self, leave_type_code: str) -> Optional[CompanyLeave]:
        """
        Get company leave by leave type code.
        
        Args:
            leave_type_code: Leave type code (e.g., "CL", "SL")
            
        Returns:
            CompanyLeave entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all_active(self) -> List[CompanyLeave]:
        """
        Get all active company leaves.
        
        Returns:
            List of active CompanyLeave entities
        """
        pass
    
    @abstractmethod
    def get_all(self, include_inactive: bool = False) -> List[CompanyLeave]:
        """
        Get all company leaves.
        
        Args:
            include_inactive: Whether to include inactive leaves
            
        Returns:
            List of CompanyLeave entities
        """
        pass
    
    @abstractmethod
    def get_applicable_for_employee(
        self,
        employee_gender: Optional[str] = None,
        employee_category: Optional[str] = None,
        is_on_probation: bool = False
    ) -> List[CompanyLeave]:
        """
        Get company leaves applicable for employee.
        
        Args:
            employee_gender: Employee gender
            employee_category: Employee category
            is_on_probation: Whether employee is on probation
            
        Returns:
            List of applicable CompanyLeave entities
        """
        pass
    
    @abstractmethod
    def exists_by_leave_type_code(self, leave_type_code: str) -> bool:
        """
        Check if company leave exists for leave type code.
        
        Args:
            leave_type_code: Leave type code
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def count_active(self) -> int:
        """
        Count active company leaves.
        
        Returns:
            Number of active company leaves
        """
        pass


class CompanyLeaveAnalyticsRepository(ABC):
    """
    Analytics repository interface for company leave reporting and analytics.
    """
    
    @abstractmethod
    def get_leave_type_usage_stats(
        self,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get leave type usage statistics.
        
        Args:
            from_date: Start date for analysis
            to_date: End date for analysis
            
        Returns:
            List of usage statistics per leave type
        """
        pass
    
    @abstractmethod
    def get_policy_compliance_report(self) -> List[Dict[str, Any]]:
        """
        Get policy compliance report.
        
        Returns:
            List of compliance metrics per leave type
        """
        pass
    
    @abstractmethod
    def get_leave_trends(
        self,
        period: str = "monthly"  # "daily", "weekly", "monthly", "quarterly"
    ) -> List[Dict[str, Any]]:
        """
        Get leave application trends.
        
        Args:
            period: Aggregation period
            
        Returns:
            List of trend data
        """
        pass 