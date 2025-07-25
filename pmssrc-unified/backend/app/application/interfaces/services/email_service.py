"""
Email Service Interface
Defines the contract for email operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date


class EmailService(ABC):
    """
    Email service interface following SOLID principles.
    
    Follows SOLID principles:
    - SRP: Only defines email operations
    - OCP: Can be implemented by different email providers
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for email operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    def send_welcome_email(
        self,
        to_email: str,
        employee_name: str,
        employee_id: str,
        date_of_joining: date
    ) -> bool:
        """
        Send welcome email to new employee.
        
        Args:
            to_email: Recipient email address
            employee_name: Employee's full name
            employee_id: Employee identifier
            date_of_joining: Employee's joining date
            
        Returns:
            True if email sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_salary_change_notification(
        self,
        to_email: str,
        employee_name: str,
        old_salary: float,
        new_salary: float,
        effective_date: date,
        reason: str
    ) -> bool:
        """
        Send salary change notification email.
        
        Args:
            to_email: Recipient email address
            employee_name: Employee's full name
            old_salary: Previous salary amount
            new_salary: New salary amount
            effective_date: Date when change becomes effective
            reason: Reason for salary change
            
        Returns:
            True if email sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_promotion_notification(
        self,
        to_email: str,
        employee_name: str,
        old_designation: str,
        new_designation: str,
        new_salary: float,
        effective_date: date
    ) -> bool:
        """
        Send promotion notification email.
        
        Args:
            to_email: Recipient email address
            employee_name: Employee's full name
            old_designation: Previous designation
            new_designation: New designation
            new_salary: New salary amount
            effective_date: Date when promotion becomes effective
            
        Returns:
            True if email sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_tax_calculation_notification(
        self,
        to_email: str,
        employee_name: str,
        tax_year: str,
        total_tax_liability: float,
        regime: str
    ) -> bool:
        """
        Send tax calculation notification email.
        
        Args:
            to_email: Recipient email address
            employee_name: Employee's full name
            tax_year: Tax year for calculation
            total_tax_liability: Calculated tax amount
            regime: Tax regime used
            
        Returns:
            True if email sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_form16_notification(
        self,
        to_email: str,
        employee_name: str,
        tax_year: str,
        form16_url: Optional[str] = None
    ) -> bool:
        """
        Send Form 16 availability notification.
        
        Args:
            to_email: Recipient email address
            employee_name: Employee's full name
            tax_year: Tax year for Form 16
            form16_url: URL to download Form 16 (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Send bulk email to multiple recipients.
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional)
            
        Returns:
            Dictionary mapping email addresses to success status
        """
        pass
    
    @abstractmethod
    def send_custom_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send custom email with optional attachments.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional)
            attachments: List of file paths to attach (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        pass


class EmailServiceError(Exception):
    """Base exception for email service operations"""
    pass


class EmailDeliveryError(EmailServiceError):
    """Exception raised when email delivery fails"""
    
    def __init__(self, email: str, reason: str):
        self.email = email
        self.reason = reason
        super().__init__(f"Failed to deliver email to {email}: {reason}")


class EmailConfigurationError(EmailServiceError):
    """Exception raised when email service is not properly configured"""
    pass


class EmailTemplateError(EmailServiceError):
    """Exception raised when email template processing fails"""
    
    def __init__(self, template_name: str, reason: str):
        self.template_name = template_name
        self.reason = reason
        super().__init__(f"Failed to process email template '{template_name}': {reason}") 