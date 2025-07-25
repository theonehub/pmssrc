"""
Notification Service Interface
Defines the contract for notification operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date


class NotificationService(ABC):
    """
    Notification service interface following SOLID principles.
    
    Follows SOLID principles:
    - SRP: Only defines notification operations
    - OCP: Can be implemented by different notification providers
    - LSP: Any implementation can be substituted
    - ISP: Focused interface for notification operations
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    @abstractmethod
    def send_notification(
        self,
        recipient: str,
        subject: str,
        message: str,
        notification_type: str = "email",
        template: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a notification to a recipient.
        
        Args:
            recipient: Recipient identifier (email, phone, etc.)
            subject: Notification subject
            message: Notification message
            notification_type: Type of notification (email, sms, push)
            template: Template name to use (optional)
            template_data: Data for template rendering (optional)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_bulk_notification(
        self,
        recipients: List[str],
        subject: str,
        message: str,
        notification_type: str = "email",
        template: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """
        Send bulk notifications to multiple recipients.
        
        Args:
            recipients: List of recipient identifiers
            subject: Notification subject
            message: Notification message
            notification_type: Type of notification (email, sms, push)
            template: Template name to use (optional)
            template_data: Data for template rendering (optional)
            
        Returns:
            Dictionary mapping recipients to success status
        """
        pass
    
    @abstractmethod
    def send_employee_welcome_notification(
        self,
        employee_email: str,
        employee_name: str,
        employee_id: str,
        date_of_joining: date
    ) -> bool:
        """
        Send welcome notification to new employee.
        
        Args:
            employee_email: Employee's email address
            employee_name: Employee's full name
            employee_id: Employee identifier
            date_of_joining: Employee's joining date
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_leave_application_notification(
        self,
        manager_email: str,
        employee_name: str,
        leave_type: str,
        start_date: date,
        end_date: date,
        reason: str
    ) -> bool:
        """
        Send leave application notification to manager.
        
        Args:
            manager_email: Manager's email address
            employee_name: Employee's full name
            leave_type: Type of leave
            start_date: Leave start date
            end_date: Leave end date
            reason: Reason for leave
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_leave_approval_notification(
        self,
        employee_email: str,
        employee_name: str,
        leave_type: str,
        start_date: date,
        end_date: date,
        status: str,
        comments: Optional[str] = None
    ) -> bool:
        """
        Send leave approval/rejection notification to employee.
        
        Args:
            employee_email: Employee's email address
            employee_name: Employee's full name
            leave_type: Type of leave
            start_date: Leave start date
            end_date: Leave end date
            status: Approval status (approved/rejected)
            comments: Approval comments (optional)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_reimbursement_notification(
        self,
        recipient_email: str,
        employee_name: str,
        reimbursement_type: str,
        amount: float,
        status: str,
        comments: Optional[str] = None
    ) -> bool:
        """
        Send reimbursement notification.
        
        Args:
            recipient_email: Recipient's email address
            employee_name: Employee's full name
            reimbursement_type: Type of reimbursement
            amount: Reimbursement amount
            status: Status of reimbursement
            comments: Additional comments (optional)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_salary_change_notification(
        self,
        employee_email: str,
        employee_name: str,
        old_salary: float,
        new_salary: float,
        effective_date: date,
        reason: str
    ) -> bool:
        """
        Send salary change notification.
        
        Args:
            employee_email: Employee's email address
            employee_name: Employee's full name
            old_salary: Previous salary amount
            new_salary: New salary amount
            effective_date: Date when change becomes effective
            reason: Reason for salary change
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_promotion_notification(
        self,
        employee_email: str,
        employee_name: str,
        old_designation: str,
        new_designation: str,
        new_salary: float,
        effective_date: date
    ) -> bool:
        """
        Send promotion notification.
        
        Args:
            employee_email: Employee's email address
            employee_name: Employee's full name
            old_designation: Previous designation
            new_designation: New designation
            new_salary: New salary amount
            effective_date: Date when promotion becomes effective
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_attendance_reminder(
        self,
        employee_email: str,
        employee_name: str,
        reminder_type: str = "checkin"
    ) -> bool:
        """
        Send attendance reminder notification.
        
        Args:
            employee_email: Employee's email address
            employee_name: Employee's full name
            reminder_type: Type of reminder (checkin, checkout)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def send_system_notification(
        self,
        recipient_email: str,
        subject: str,
        message: str,
        priority: str = "normal"
    ) -> bool:
        """
        Send system notification.
        
        Args:
            recipient_email: Recipient's email address
            subject: Notification subject
            message: Notification message
            priority: Priority level (low, normal, high, urgent)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        pass


class NotificationServiceError(Exception):
    """Base exception for notification service operations"""
    pass


class NotificationDeliveryError(NotificationServiceError):
    """Exception raised when notification delivery fails"""
    
    def __init__(self, recipient: str, reason: str):
        self.recipient = recipient
        self.reason = reason
        super().__init__(f"Failed to deliver notification to {recipient}: {reason}")


class NotificationConfigurationError(NotificationServiceError):
    """Exception raised when notification service is misconfigured"""
    
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Notification service configuration error: {reason}")


class NotificationTemplateError(NotificationServiceError):
    """Exception raised when notification template is invalid"""
    
    def __init__(self, template_name: str, reason: str):
        self.template_name = template_name
        self.reason = reason
        super().__init__(f"Template error for '{template_name}': {reason}") 