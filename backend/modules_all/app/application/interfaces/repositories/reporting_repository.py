"""
Reporting Repository Interface
Abstract repository interface for reporting operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

from app.domain.entities.report import Report
from app.domain.value_objects.report_id import ReportId
from app.application.dto.reporting_dto import ReportSearchFiltersDTO


class ReportingRepository(ABC):
    """
    Abstract repository interface for reporting operations.
    
    Follows SOLID principles:
    - SRP: Only handles data persistence concerns
    - OCP: Can be extended with new implementations
    - LSP: All implementations must follow this contract
    - ISP: Focused interface for reporting data operations
    - DIP: Depends on abstractions, not concretions
    """
    
    @abstractmethod
    async def save(self, report: Report, hostname: str) -> Report:
        """
        Save report to organisation-specific database.
        
        Args:
            report: Report entity to save
            hostname: Organisation hostname for database selection
            
        Returns:
            Saved report entity
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, report_id: ReportId, hostname: str) -> Optional[Report]:
        """
        Get report by ID from organisation-specific database.
        
        Args:
            report_id: Report ID to search for
            hostname: Organisation hostname for database selection
            
        Returns:
            Report entity if found, None otherwise
            
        Raises:
            RepositoryError: If get operation fails
        """
        pass
    
    @abstractmethod
    async def find_with_filters(
        self, 
        filters: ReportSearchFiltersDTO, 
        hostname: str
    ) -> Tuple[List[Report], int]:
        """
        Find reports with filters from organisation-specific database.
        
        Args:
            filters: Search filters and pagination
            hostname: Organisation hostname for database selection
            
        Returns:
            Tuple of (reports list, total count)
            
        Raises:
            RepositoryError: If search operation fails
        """
        pass
    
    @abstractmethod
    async def delete(self, report_id: ReportId, hostname: str) -> bool:
        """
        Delete report from organisation-specific database.
        
        Args:
            report_id: Report ID to delete
            hostname: Organisation hostname for database selection
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            RepositoryError: If delete operation fails
        """
        pass
    
    @abstractmethod
    async def get_reports_by_type(
        self, 
        report_type: str, 
        hostname: str,
        limit: int = 10
    ) -> List[Report]:
        """
        Get recent reports by type.
        
        Args:
            report_type: Type of reports to retrieve
            hostname: Organisation hostname for database selection
            limit: Maximum number of reports to return
            
        Returns:
            List of reports
            
        Raises:
            RepositoryError: If operation fails
        """
        pass
    
    @abstractmethod
    async def get_reports_by_status(
        self, 
        status: str, 
        hostname: str,
        limit: int = 10
    ) -> List[Report]:
        """
        Get reports by status.
        
        Args:
            status: Status of reports to retrieve
            hostname: Organisation hostname for database selection
            limit: Maximum number of reports to return
            
        Returns:
            List of reports
            
        Raises:
            RepositoryError: If operation fails
        """
        pass
    
    @abstractmethod
    async def get_user_reports(
        self, 
        created_by: str, 
        hostname: str,
        limit: int = 10
    ) -> List[Report]:
        """
        Get reports created by specific user.
        
        Args:
            created_by: User ID who created the reports
            hostname: Organisation hostname for database selection
            limit: Maximum number of reports to return
            
        Returns:
            List of reports
            
        Raises:
            RepositoryError: If operation fails
        """
        pass
    
    @abstractmethod
    async def cleanup_old_reports(
        self, 
        hostname: str,
        days_old: int = 30
    ) -> int:
        """
        Clean up old completed reports.
        
        Args:
            hostname: Organisation hostname for database selection
            days_old: Number of days after which to clean up reports
            
        Returns:
            Number of reports cleaned up
            
        Raises:
            RepositoryError: If cleanup operation fails
        """
        pass 