"""
Payslip Repository Interfaces
Repository interfaces for payslip operations following CQRS pattern
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from io import BytesIO

from app.domain.value_objects.payroll_value_objects import PayslipMetadata
from app.application.dto.payroll_dto import PayslipFormatEnum


class PayslipCommandRepository(ABC):
    """Command repository interface for payslip write operations"""
    
    @abstractmethod
    async def save_generated_payslip(self, payslip_metadata: PayslipMetadata,
                                   file_content: BytesIO, hostname: str) -> str:
        """
        Save generated payslip file and metadata
        
        Args:
            payslip_metadata: Payslip metadata
            file_content: Generated file content
            hostname: Organisation hostname
            
        Returns:
            Payslip ID
            
        Raises:
            PayslipSaveError: If saving fails
            StorageError: If file storage fails
        """
        pass
    
    @abstractmethod
    async def update_payslip_metadata(self, payslip_id: str, 
                                    update_data: Dict[str, Any],
                                    hostname: str) -> bool:
        """
        Update payslip metadata
        
        Args:
            payslip_id: Payslip ID
            update_data: Metadata to update
            hostname: Organisation hostname
            
        Returns:
            True if successful
            
        Raises:
            PayslipNotFoundError: If payslip doesn't exist
        """
        pass
    
    @abstractmethod
    async def update_email_status(self, payslip_id: str, email_status: str,
                                email_sent_at: datetime, recipient_email: str,
                                hostname: str) -> bool:
        """
        Update email status for payslip
        
        Args:
            payslip_id: Payslip ID
            email_status: Email status (sent, failed, etc.)
            email_sent_at: Timestamp when email was sent
            recipient_email: Email recipient
            hostname: Organisation hostname
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def increment_download_count(self, payslip_id: str,
                                     hostname: str) -> bool:
        """
        Increment download count for payslip
        
        Args:
            payslip_id: Payslip ID
            hostname: Organisation hostname
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def bulk_save_payslips(self, payslips_data: List[Dict[str, Any]],
                               hostname: str) -> List[str]:
        """
        Save multiple payslips in bulk
        
        Args:
            payslips_data: List of payslip data with metadata and content
            hostname: Organisation hostname
            
        Returns:
            List of created payslip IDs
            
        Raises:
            BulkOperationError: If some saves fail
        """
        pass
    
    @abstractmethod
    async def delete_payslip(self, payslip_id: str, hostname: str,
                           deleted_by: str) -> bool:
        """
        Delete payslip file and metadata
        
        Args:
            payslip_id: Payslip ID
            hostname: Organisation hostname
            deleted_by: User deleting the payslip
            
        Returns:
            True if successful
            
        Raises:
            PayslipNotFoundError: If payslip doesn't exist
        """
        pass


class PayslipQueryRepository(ABC):
    """Query repository interface for payslip read operations"""
    
    @abstractmethod
    async def get_by_id(self, payslip_id: str, hostname: str) -> Optional[PayslipMetadata]:
        """
        Get payslip metadata by ID
        
        Args:
            payslip_id: Payslip ID
            hostname: Organisation hostname
            
        Returns:
            Payslip metadata if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_payout_id(self, payout_id: str, hostname: str) -> Optional[PayslipMetadata]:
        """
        Get payslip metadata by payout ID
        
        Args:
            payout_id: Payout ID
            hostname: Organisation hostname
            
        Returns:
            Payslip metadata if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_employee_payslips(self, employee_id: str, year: int,
                                  hostname: str) -> List[PayslipMetadata]:
        """
        Get all payslips for an employee in a year
        
        Args:
            employee_id: Employee ID
            year: Year
            hostname: Organisation hostname
            
        Returns:
            List of payslip metadata
        """
        pass
    
    @abstractmethod
    async def get_monthly_payslips(self, month: int, year: int,
                                 hostname: str, 
                                 format_filter: Optional[PayslipFormatEnum] = None) -> List[PayslipMetadata]:
        """
        Get all payslips for a specific month
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            format_filter: Optional format filter
            
        Returns:
            List of payslip metadata
        """
        pass
    
    @abstractmethod
    async def search_payslips(self, filters: Dict[str, Any],
                            hostname: str) -> Dict[str, Any]:
        """
        Search payslips with filters and pagination
        
        Args:
            filters: Search filters including pagination
            hostname: Organisation hostname
            
        Returns:
            Dictionary with 'payslips', 'total_count', 'page', 'page_size'
        """
        pass
    
    @abstractmethod
    async def get_payslip_file(self, payslip_id: str, hostname: str) -> Optional[BytesIO]:
        """
        Get payslip file content
        
        Args:
            payslip_id: Payslip ID
            hostname: Organisation hostname
            
        Returns:
            File content as BytesIO if found, None otherwise
            
        Raises:
            PayslipNotFoundError: If payslip doesn't exist
            FileNotFoundError: If file is missing from storage
        """
        pass
    
    @abstractmethod
    async def check_payslip_exists(self, payout_id: str, format: PayslipFormatEnum,
                                 hostname: str) -> bool:
        """
        Check if payslip already exists for payout and format
        
        Args:
            payout_id: Payout ID
            format: Payslip format
            hostname: Organisation hostname
            
        Returns:
            True if payslip exists
        """
        pass
    
    @abstractmethod
    async def get_payslip_download_stats(self, payslip_id: str,
                                       hostname: str) -> Dict[str, Any]:
        """
        Get download statistics for payslip
        
        Args:
            payslip_id: Payslip ID
            hostname: Organisation hostname
            
        Returns:
            Download statistics
        """
        pass
    
    @abstractmethod
    async def get_bulk_generation_status(self, batch_id: str,
                                       hostname: str) -> Dict[str, Any]:
        """
        Get status of bulk payslip generation
        
        Args:
            batch_id: Batch ID
            hostname: Organisation hostname
            
        Returns:
            Bulk generation status
        """
        pass


class PayslipStorageRepository(ABC):
    """Repository interface for payslip file storage operations"""
    
    @abstractmethod
    async def store_file(self, file_content: BytesIO, file_path: str,
                       content_type: str) -> bool:
        """
        Store payslip file
        
        Args:
            file_content: File content
            file_path: Storage path
            content_type: MIME content type
            
        Returns:
            True if successful
            
        Raises:
            StorageError: If storage fails
        """
        pass
    
    @abstractmethod
    async def retrieve_file(self, file_path: str) -> Optional[BytesIO]:
        """
        Retrieve payslip file
        
        Args:
            file_path: Storage path
            
        Returns:
            File content if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete payslip file
        
        Args:
            file_path: Storage path
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information
        
        Args:
            file_path: Storage path
            
        Returns:
            File information (size, modified date, etc.) if found
        """
        pass
    
    @abstractmethod
    async def generate_download_url(self, file_path: str,
                                  expiry_minutes: int = 60) -> Optional[str]:
        """
        Generate temporary download URL
        
        Args:
            file_path: Storage path
            expiry_minutes: URL expiry time in minutes
            
        Returns:
            Temporary download URL if successful
        """
        pass
    
    @abstractmethod
    async def cleanup_old_files(self, older_than_days: int,
                              hostname: str) -> int:
        """
        Cleanup old payslip files
        
        Args:
            older_than_days: Delete files older than this many days
            hostname: Organisation hostname
            
        Returns:
            Number of files deleted
        """
        pass


class PayslipAnalyticsRepository(ABC):
    """Repository interface for payslip analytics and reporting"""
    
    @abstractmethod
    async def get_generation_stats(self, month: int, year: int,
                                 hostname: str) -> Dict[str, Any]:
        """
        Get payslip generation statistics
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Generation statistics
        """
        pass
    
    @abstractmethod
    async def get_email_delivery_stats(self, month: int, year: int,
                                     hostname: str) -> Dict[str, Any]:
        """
        Get email delivery statistics
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Email delivery statistics
        """
        pass
    
    @abstractmethod
    async def get_download_analytics(self, start_date: datetime, end_date: datetime,
                                   hostname: str) -> Dict[str, Any]:
        """
        Get download analytics
        
        Args:
            start_date: Start date
            end_date: End date
            hostname: Organisation hostname
            
        Returns:
            Download analytics
        """
        pass
    
    @abstractmethod
    async def get_format_distribution(self, month: int, year: int,
                                    hostname: str) -> Dict[str, int]:
        """
        Get format distribution statistics
        
        Args:
            month: Month (1-12)
            year: Year
            hostname: Organisation hostname
            
        Returns:
            Format distribution
        """
        pass
    
    @abstractmethod
    async def get_employee_access_patterns(self, employee_id: str,
                                         hostname: str) -> Dict[str, Any]:
        """
        Get employee access patterns
        
        Args:
            employee_id: Employee ID
            hostname: Organisation hostname
            
        Returns:
            Access patterns data
        """
        pass


class PayslipTemplateRepository(ABC):
    """Repository interface for payslip template operations"""
    
    @abstractmethod
    async def create_template(self, template_data: Dict[str, Any],
                            hostname: str, created_by: str) -> str:
        """
        Create payslip template
        
        Args:
            template_data: Template configuration
            hostname: Organisation hostname
            created_by: User creating the template
            
        Returns:
            Template ID
        """
        pass
    
    @abstractmethod
    async def get_template(self, template_id: str, hostname: str) -> Optional[Dict[str, Any]]:
        """
        Get payslip template
        
        Args:
            template_id: Template ID
            hostname: Organisation hostname
            
        Returns:
            Template data if found
        """
        pass
    
    @abstractmethod
    async def get_default_template(self, format: PayslipFormatEnum,
                                 hostname: str) -> Optional[Dict[str, Any]]:
        """
        Get default template for format
        
        Args:
            format: Payslip format
            hostname: Organisation hostname
            
        Returns:
            Default template data if found
        """
        pass
    
    @abstractmethod
    async def update_template(self, template_id: str, update_data: Dict[str, Any],
                            hostname: str, updated_by: str) -> bool:
        """
        Update payslip template
        
        Args:
            template_id: Template ID
            update_data: Update data
            hostname: Organisation hostname
            updated_by: User making the update
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def list_templates(self, hostname: str, 
                           format_filter: Optional[PayslipFormatEnum] = None) -> List[Dict[str, Any]]:
        """
        List available templates
        
        Args:
            hostname: Organisation hostname
            format_filter: Optional format filter
            
        Returns:
            List of template metadata
        """
        pass 