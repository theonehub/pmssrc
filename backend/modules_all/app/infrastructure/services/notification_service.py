"""
Notification Service Implementation
SOLID-compliant service for sending notifications
"""

import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from app.domain.entities.user import User

logger = logging.getLogger(__name__)


class NotificationService(ABC):
    """
    Abstract notification service interface.
    
    Follows SOLID principles:
    - SRP: Only handles notification operations
    - OCP: Can be extended with new notification types
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for notification operations
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    async def send_user_created_notification(self, user: User) -> bool:
        """Send notification when user is created."""
        pass
    
    @abstractmethod
    async def send_user_updated_notification(self, user: User) -> bool:
        """Send notification when user is updated."""
        pass
    
    @abstractmethod
    async def send_password_changed_notification(
        self, 
        user: User, 
        is_self_change: bool
    ) -> bool:
        """Send notification when password is changed."""
        pass
    
    @abstractmethod
    async def send_role_changed_notification(
        self, 
        user: User, 
        old_role: str, 
        new_role: str,
        reason: str
    ) -> bool:
        """Send notification when role is changed."""
        pass
    
    @abstractmethod
    async def send_status_change_notification(
        self, 
        user: User, 
        old_status: str, 
        new_status: str,
        reason: Optional[str] = None
    ) -> bool:
        """Send notification when status changes."""
        pass
    
    @abstractmethod
    async def send_login_alert_notification(
        self, 
        user: User, 
        login_details: Dict[str, Any]
    ) -> bool:
        """Send notification for login activity."""
        pass
    
    @abstractmethod
    async def send_profile_completion_reminder(self, user: User) -> bool:
        """Send reminder for profile completion."""
        pass
    
    @abstractmethod
    async def send_password_reset_email(self, email: str, temp_password: str) -> bool:
        """Send password reset email."""
        pass
    
    @abstractmethod
    async def send_admin_notification(
        self, 
        subject: str, 
        template: str = None,
        data: Dict[str, Any] = None
    ) -> bool:
        """Send generic notification to administrators."""
        pass
    
    @abstractmethod
    async def notify_holiday_created(self, holiday) -> bool:
        """Send notification when a public holiday is created."""
        pass
    
    @abstractmethod
    async def notify_holiday_updated(self, holiday) -> bool:
        """Send notification when a public holiday is updated."""
        pass
    
    @abstractmethod
    async def notify_holiday_deleted(self, holiday_id: str) -> bool:
        """Send notification when a public holiday is deleted."""
        pass


class EmailNotificationService(NotificationService):
    """
    Email-based notification service implementation.
    
    Implements the NotificationService interface using email delivery.
    """
    
    def __init__(self, email_service=None):
        """
        Initialize email notification service.
        
        Args:
            email_service: Email service for sending emails
        """
        self.email_service = email_service
        self.from_email = "noreply@pms.com"
        self.admin_email = "admin@pms.com"
    
    async def send_user_created_notification(self, user: User) -> bool:
        """Send notification when user is created."""
        try:
            subject = "Welcome to PMS - Account Created"
            body = f"""
            Dear {user.name},
            
            Your account has been successfully created in the PMS system.
            
            Employee ID: {user.employee_id}
            Email: {user.email.value}
            Department: {user.department}
            Role: {user.credentials.role.value}
            
            Please contact your administrator for login credentials.
            
            Best regards,
            PMS Team
            """
            
            # Send email to user
            await self._send_email(user.email.value, subject, body)
            
            # Send notification to admin
            admin_subject = f"New User Created: {user.name}"
            admin_body = f"""
            A new user has been created in the system:
            
            Name: {user.name}
            Employee ID: {user.employee_id}
            Email: {user.email.value}
            Department: {user.department}
            Role: {user.credentials.role.value}
            Created by: {user.created_by}
            """
            
            await self._send_email(self.admin_email, admin_subject, admin_body)
            
            logger.info(f"User created notification sent for: {user.employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending user created notification: {e}")
            return False
    
    async def send_user_updated_notification(self, user: User) -> bool:
        """Send notification when user is updated."""
        try:
            subject = "PMS Account Updated"
            body = f"""
            Dear {user.name},
            
            Your account information has been updated in the PMS system.
            
            If you did not request this change, please contact your administrator immediately.
            
            Best regards,
            PMS Team
            """
            
            await self._send_email(user.email.value, subject, body)
            logger.info(f"User updated notification sent for: {user.employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending user updated notification: {e}")
            return False
    
    async def send_password_changed_notification(
        self, 
        user: User, 
        is_self_change: bool
    ) -> bool:
        """Send notification when password is changed."""
        try:
            if is_self_change:
                subject = "Password Changed Successfully"
                body = f"""
                Dear {user.name},
                
                Your password has been successfully changed.
                
                If you did not make this change, please contact your administrator immediately.
                
                Best regards,
                PMS Team
                """
            else:
                subject = "Password Reset by Administrator"
                body = f"""
                Dear {user.name},
                
                Your password has been reset by an administrator.
                
                Please log in with your new credentials and change your password.
                
                Best regards,
                PMS Team
                """
            
            await self._send_email(user.email.value, subject, body)
            logger.info(f"Password changed notification sent for: {user.employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password changed notification: {e}")
            return False
    
    async def send_role_changed_notification(
        self, 
        user: User, 
        old_role: str, 
        new_role: str,
        reason: str
    ) -> bool:
        """Send notification when role is changed."""
        try:
            subject = "Role Changed in PMS"
            body = f"""
            Dear {user.name},
            
            Your role has been changed in the PMS system.
            
            Previous Role: {old_role}
            New Role: {new_role}
            Reason: {reason}
            
            Your permissions may have changed. Please contact your administrator if you have any questions.
            
            Best regards,
            PMS Team
            """
            
            await self._send_email(user.email.value, subject, body)
            logger.info(f"Role changed notification sent for: {user.employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending role changed notification: {e}")
            return False
    
    async def send_status_change_notification(
        self, 
        user: User, 
        old_status: str, 
        new_status: str,
        reason: Optional[str] = None
    ) -> bool:
        """Send notification when status changes."""
        try:
            subject = "Account Status Changed"
            body = f"""
            Dear {user.name},
            
            Your account status has been changed in the PMS system.
            
            Previous Status: {old_status}
            New Status: {new_status}
            """
            
            if reason:
                body += f"\nReason: {reason}"
            
            body += """
            
            Please contact your administrator if you have any questions.
            
            Best regards,
            PMS Team
            """
            
            await self._send_email(user.email.value, subject, body)
            logger.info(f"Status change notification sent for: {user.employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending status change notification: {e}")
            return False
    
    async def send_admin_notification(
        self, 
        subject: str, 
        template: str = None,
        data: Dict[str, Any] = None
    ) -> bool:
        """Send generic notification to administrators."""
        try:
            # Create body from data if template specified
            if template and data:
                if template == "reimbursement_type_created":
                    body = f"""
                    Dear Administrator,
                    
                    A new reimbursement type has been created in the system:
                    
                    Type ID: {data.get('reimbursement_type_id', 'N/A')}
                    Name: {data.get('category_name', 'N/A')}
                    Max Limit: {data.get('max_limit', 'N/A')}
                    Created by: {data.get('created_by', 'N/A')}
                    
                    Please review the new reimbursement type configuration.
                    
                    Best regards,
                    PMS System
                    """
                else:
                    # Generic template
                    body = f"Notification: {subject}\n\nData: {data}"
            else:
                body = f"Administrative notification: {subject}"
            
            await self._send_email(self.admin_email, subject, body)
            logger.info(f"Admin notification sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False
    
    async def send_login_alert_notification(
        self, 
        user: User, 
        login_details: Dict[str, Any]
    ) -> bool:
        """Send notification for suspicious login activity."""
        try:
            subject = "Security Alert - New Login Detected"
            body = f"""
            Dear {user.name},
            
            A new login to your PMS account has been detected.
            
            Login Details:
            - Time: {login_details.get('timestamp', 'Unknown')}
            - IP Address: {login_details.get('ip_address', 'Unknown')}
            - Location: {login_details.get('location', 'Unknown')}
            - Device: {login_details.get('device', 'Unknown')}
            
            If this was not you, please contact your administrator immediately and change your password.
            
            Best regards,
            PMS Team
            """
            
            await self._send_email(user.email.value, subject, body)
            logger.info(f"Login alert notification sent for: {user.employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending login alert notification: {e}")
            return False
    
    async def send_profile_completion_reminder(self, user: User) -> bool:
        """Send reminder for profile completion."""
        try:
            completion_percentage = user.profile_completion_percentage
            subject = "Complete Your PMS Profile"
            body = f"""
            Dear {user.name},
            
            Your PMS profile is {completion_percentage:.1f}% complete.
            
            Please log in to complete your profile information:
            - Upload profile photo
            - Add PAN and Aadhar documents
            - Update contact information
            - Complete salary details
            
            A complete profile helps ensure accurate payroll processing and better system experience.
            
            Best regards,
            PMS Team
            """
            
            await self._send_email(user.email.value, subject, body)
            logger.info(f"Profile completion reminder sent for: {user.employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending profile completion reminder: {e}")
            return False
    
    async def send_password_reset_email(self, email: str, temp_password: str) -> bool:
        """Send password reset email."""
        try:
            subject = "Password Reset - PMS"
            body = f"""
            Dear User,
            
            Your password has been reset as requested.
            
            Temporary Password: {temp_password}
            
            Please log in with this temporary password and change it immediately for security.
            
            Best regards,
            PMS Team
            """
            
            await self._send_email(email, subject, body)
            logger.info(f"Password reset email sent to: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False
    
    async def send_organisation_created_notification(self, organisation) -> bool:
        """Send notification when organisation is created."""
        try:
            subject = "New Organisation Created in PMS"
            body = f"""
            A new organisation has been created in the PMS system:
            
            Name: {organisation.name}
            Organisation ID: {organisation.organisation_id}
            Type: {organisation.organisation_type.value}
            Email: {organisation.contact_info.email if organisation.contact_info else 'N/A'}
            Phone: {organisation.contact_info.phone if organisation.contact_info else 'N/A'}
            City: {organisation.address.city if organisation.address else 'N/A'}
            State: {organisation.address.state if organisation.address else 'N/A'}
            Country: {organisation.address.country if organisation.address else 'N/A'}
            Created by: {organisation.created_by or 'System'}
            
            Please review and take necessary actions.
            
            Best regards,
            PMS Team
            """
            
            # Send notification to admin
            await self._send_email(self.admin_email, subject, body)
            
            logger.info(f"Organisation created notification sent for: {organisation.organisation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending organisation created notification: {e}")
            return False
    
    async def send_organisation_updated_notification(
        self, 
        organisation, 
        updated_fields: List[str]
    ) -> bool:
        """Send notification when organisation is updated."""
        try:
            subject = f"Organisation Updated: {organisation.name}"
            body = f"""
            An organisation has been updated in the PMS system:
            
            Name: {organisation.name}
            Organisation ID: {organisation.organisation_id}
            Updated Fields: {', '.join(updated_fields)}
            Updated by: {organisation.updated_by or 'System'}
            
            Please review the changes if necessary.
            
            Best regards,
            PMS Team
            """
            
            # Send notification to admin
            await self._send_email(self.admin_email, subject, body)
            
            logger.info(f"Organisation updated notification sent for: {organisation.organisation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending organisation updated notification: {e}")
            return False
    
    # Missing abstract methods implementation
    
    async def send_notification(
        self,
        recipient: str,
        subject: str,
        message: str,
        notification_type: str = "email",
        template: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send generic notification."""
        try:
            await self._send_email(recipient, subject, message)
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def send_bulk_notification(
        self,
        recipients: List[str],
        subject: str,
        message: str,
        notification_type: str = "email",
        template: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Send bulk notifications."""
        results = {}
        for recipient in recipients:
            try:
                success = await self.send_notification(recipient, subject, message, notification_type, template, template_data)
                results[recipient] = success
            except Exception as e:
                logger.error(f"Error sending bulk notification to {recipient}: {e}")
                results[recipient] = False
        return results
    
    async def send_employee_welcome_notification(
        self,
        employee_email: str,
        employee_name: str,
        employee_id: str,
        date_of_joining
    ) -> bool:
        """Send welcome notification to new employee."""
        try:
            subject = "Welcome to the Company!"
            body = f"""
            Dear {employee_name},
            
            Welcome to our company! Your account has been created.
            
            Employee ID: {employee_id}
            Date of Joining: {date_of_joining}
            
            Please contact HR for your login credentials.
            
            Best regards,
            HR Team
            """
            await self._send_email(employee_email, subject, body)
            return True
        except Exception as e:
            logger.error(f"Error sending welcome notification: {e}")
            return False
    
    async def send_leave_application_notification(
        self,
        manager_email: str,
        employee_name: str,
        leave_type: str,
        start_date,
        end_date,
        reason: str
    ) -> bool:
        """Send leave application notification to manager."""
        try:
            subject = f"Leave Application from {employee_name}"
            body = f"""
            Dear Manager,
            
            {employee_name} has applied for leave:
            
            Leave Type: {leave_type}
            Start Date: {start_date}
            End Date: {end_date}
            Reason: {reason}
            
            Please review and approve/reject the application.
            
            Best regards,
            PMS System
            """
            await self._send_email(manager_email, subject, body)
            return True
        except Exception as e:
            logger.error(f"Error sending leave application notification: {e}")
            return False
    
    async def send_leave_approval_notification(
        self,
        employee_email: str,
        employee_name: str,
        leave_type: str,
        start_date,
        end_date,
        status: str,
        comments: Optional[str] = None
    ) -> bool:
        """Send leave approval/rejection notification to employee."""
        try:
            subject = f"Leave Application {status.title()}"
            body = f"""
            Dear {employee_name},
            
            Your leave application has been {status}:
            
            Leave Type: {leave_type}
            Start Date: {start_date}
            End Date: {end_date}
            Status: {status.title()}
            """
            if comments:
                body += f"\nComments: {comments}"
            
            body += """
            
            Best regards,
            HR Team
            """
            await self._send_email(employee_email, subject, body)
            return True
        except Exception as e:
            logger.error(f"Error sending leave approval notification: {e}")
            return False
    
    async def send_reimbursement_notification(
        self,
        recipient_email: str,
        employee_name: str,
        reimbursement_type: str,
        amount: float,
        status: str,
        comments: Optional[str] = None
    ) -> bool:
        """Send reimbursement notification."""
        try:
            subject = f"Reimbursement Request {status.title()}: {reimbursement_type}"
            body = f"""
            Dear {employee_name},
            
            Your reimbursement request has been {status}:
            
            Type: {reimbursement_type}
            Amount: ₹{amount:,.2f}
            Status: {status.title()}
            """
            if comments:
                body += f"\nComments: {comments}"
            
            body += """
            
            Best regards,
            Finance Team
            """
            await self._send_email(recipient_email, subject, body)
            logger.info(f"Reimbursement notification sent to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending reimbursement notification: {e}")
            return False
    
    async def send_salary_change_notification(
        self,
        employee_email: str,
        employee_name: str,
        old_salary: float,
        new_salary: float,
        effective_date,
        reason: str
    ) -> bool:
        """Send salary change notification."""
        try:
            subject = "Salary Change Notification"
            body = f"""
            Dear {employee_name},
            
            Your salary has been updated:
            
            Previous Salary: ₹{old_salary:,.2f}
            New Salary: ₹{new_salary:,.2f}
            Effective Date: {effective_date}
            Reason: {reason}
            
            Best regards,
            HR Team
            """
            await self._send_email(employee_email, subject, body)
            return True
        except Exception as e:
            logger.error(f"Error sending salary change notification: {e}")
            return False
    
    async def send_promotion_notification(
        self,
        employee_email: str,
        employee_name: str,
        old_designation: str,
        new_designation: str,
        new_salary: float,
        effective_date
    ) -> bool:
        """Send promotion notification."""
        try:
            subject = "Congratulations on Your Promotion!"
            body = f"""
            Dear {employee_name},
            
            Congratulations! You have been promoted:
            
            Previous Designation: {old_designation}
            New Designation: {new_designation}
            New Salary: ₹{new_salary:,.2f}
            Effective Date: {effective_date}
            
            Best regards,
            HR Team
            """
            await self._send_email(employee_email, subject, body)
            return True
        except Exception as e:
            logger.error(f"Error sending promotion notification: {e}")
            return False
    
    async def send_attendance_reminder(
        self,
        employee_email: str,
        employee_name: str,
        reminder_type: str = "checkin"
    ) -> bool:
        """Send attendance reminder notification."""
        try:
            if reminder_type == "checkin":
                subject = "Check-in Reminder"
                body = f"""
                Dear {employee_name},
                
                This is a reminder to check in for today.
                
                Best regards,
                HR Team
                """
            else:
                subject = "Check-out Reminder"
                body = f"""
                Dear {employee_name},
                
                This is a reminder to check out for today.
                
                Best regards,
                HR Team
                """
            await self._send_email(employee_email, subject, body)
            return True
        except Exception as e:
            logger.error(f"Error sending attendance reminder: {e}")
            return False
    
    async def send_system_notification(
        self,
        recipient_email: str,
        subject: str,
        message: str,
        priority: str = "normal"
    ) -> bool:
        """Send system notification."""
        try:
            priority_prefix = f"[{priority.upper()}] " if priority != "normal" else ""
            full_subject = f"{priority_prefix}{subject}"
            await self._send_email(recipient_email, full_subject, message)
            return True
        except Exception as e:
            logger.error(f"Error sending system notification: {e}")
            return False
    
    async def notify_holiday_created(self, holiday) -> bool:
        """Send notification when a public holiday is created."""
        try:
            subject = "New Public Holiday Created"
            body = f"""
            A new public holiday has been created in the PMS system:
            
            Holiday Name: {holiday.name}
            Date: {holiday.date if hasattr(holiday, 'date') else holiday.holiday_date}
            Description: {holiday.description or 'N/A'}
            
            Please update your calendars accordingly.
            
            Best regards,
            HR Team
            """
            
            # Send notification to admin
            await self._send_email(self.admin_email, subject, body)
            
            logger.info(f"Holiday created notification sent for: {holiday.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending holiday created notification: {e}")
            return False
    
    async def notify_holiday_updated(self, holiday) -> bool:
        """Send notification when a public holiday is updated."""
        try:
            subject = "Public Holiday Updated"
            body = f"""
            A public holiday has been updated in the PMS system:
            
            Holiday Name: {holiday.name}
            Date: {holiday.date if hasattr(holiday, 'date') else holiday.holiday_date}
            Description: {holiday.description or 'N/A'}
            
            Please update your calendars accordingly.
            
            Best regards,
            HR Team
            """
            
            # Send notification to admin
            await self._send_email(self.admin_email, subject, body)
            
            logger.info(f"Holiday updated notification sent for: {holiday.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending holiday updated notification: {e}")
            return False
    
    async def notify_holiday_deleted(self, holiday_id: str) -> bool:
        """Send notification when a public holiday is deleted."""
        try:
            subject = "Public Holiday Deleted"
            body = f"""
            A public holiday has been deleted from the PMS system:
            
            Holiday ID: {holiday_id}
            
            Please update your calendars accordingly.
            
            Best regards,
            HR Team
            """
            
            # Send notification to admin
            await self._send_email(self.admin_email, subject, body)
            
            logger.info(f"Holiday deleted notification sent for ID: {holiday_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending holiday deleted notification: {e}")
            return False
    
    async def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        Send email using configured email service.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            if self.email_service:
                # Use actual email service
                return await self.email_service.send_email(
                    from_email=self.from_email,
                    to_email=to_email,
                    subject=subject,
                    body=body
                )
            else:
                # Log email for development/testing
                logger.info(f"EMAIL TO: {to_email}")
                logger.info(f"SUBJECT: {subject}")
                logger.info(f"BODY: {body}")
                return True
                
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False


class SMSNotificationService(NotificationService):
    """
    SMS-based notification service implementation.
    
    Implements the NotificationService interface using SMS delivery.
    """
    
    def __init__(self, sms_service=None):
        """
        Initialize SMS notification service.
        
        Args:
            sms_service: SMS service for sending messages
        """
        self.sms_service = sms_service
    
    async def send_user_created_notification(self, user: User) -> bool:
        """Send SMS when user is created."""
        try:
            message = f"Welcome to PMS! Your account has been created. Employee ID: {user.employee_id}"
            await self._send_sms(user.mobile, message)
            return True
        except Exception as e:
            logger.error(f"Error sending user created SMS: {e}")
            return False
    
    async def send_password_changed_notification(
        self, 
        user: User, 
        is_self_change: bool
    ) -> bool:
        """Send SMS when password is changed."""
        try:
            if is_self_change:
                message = "Your PMS password has been changed successfully."
            else:
                message = "Your PMS password has been reset by administrator. Please log in and change it."
            
            await self._send_sms(user.mobile, message)
            return True
        except Exception as e:
            logger.error(f"Error sending password changed SMS: {e}")
            return False
    
    async def _send_sms(self, mobile: str, message: str) -> bool:
        """Send SMS using configured SMS service."""
        try:
            if self.sms_service:
                return await self.sms_service.send_sms(mobile, message)
            else:
                logger.info(f"SMS TO: {mobile}")
                logger.info(f"MESSAGE: {message}")
                return True
        except Exception as e:
            logger.error(f"Error sending SMS to {mobile}: {e}")
            return False
    
    # Implement other abstract methods with SMS logic...
    async def send_user_updated_notification(self, user: User) -> bool:
        return True
    
    async def send_role_changed_notification(self, user: User, old_role: str, new_role: str, reason: str) -> bool:
        return True
    
    async def send_status_change_notification(self, user: User, old_status: str, new_status: str, reason: Optional[str] = None) -> bool:
        return True
    
    async def send_login_alert_notification(self, user: User, login_details: Dict[str, Any]) -> bool:
        return True
    
    async def send_profile_completion_reminder(self, user: User) -> bool:
        return True
    
    async def send_password_reset_email(self, email: str, temp_password: str) -> bool:
        return True
    
    async def send_admin_notification(
        self, 
        subject: str, 
        template: str = None,
        data: Dict[str, Any] = None
    ) -> bool:
        """Send admin notification via SMS (placeholder)."""
        return True
    
    async def notify_holiday_created(self, holiday) -> bool:
        """Send SMS notification when a public holiday is created."""
        try:
            message = f"New holiday created: {holiday.name} on {holiday.date if hasattr(holiday, 'date') else holiday.holiday_date}"
            return await self._send_sms("admin_mobile", message)
        except Exception as e:
            logger.error(f"Error sending holiday created SMS: {e}")
            return False
    
    async def notify_holiday_updated(self, holiday) -> bool:
        """Send SMS notification when a public holiday is updated."""
        try:
            message = f"Holiday updated: {holiday.name} on {holiday.date if hasattr(holiday, 'date') else holiday.holiday_date}"
            return await self._send_sms("admin_mobile", message)
        except Exception as e:
            logger.error(f"Error sending holiday updated SMS: {e}")
            return False
    
    async def notify_holiday_deleted(self, holiday_id: str) -> bool:
        """Send SMS notification when a public holiday is deleted."""
        try:
            message = f"Holiday deleted: {holiday_id}"
            return await self._send_sms("admin_mobile", message)
        except Exception as e:
            logger.error(f"Error sending holiday deleted SMS: {e}")
            return False


class CompositeNotificationService(NotificationService):
    """
    Composite notification service that can send notifications via multiple channels.
    
    Follows the Composite pattern to combine multiple notification services.
    """
    
    def __init__(self, services: list[NotificationService]):
        """
        Initialize composite service with multiple notification services.
        
        Args:
            services: List of notification services to use
        """
        self.services = services
    
    async def send_user_created_notification(self, user: User) -> bool:
        """Send notification via all configured services."""
        results = []
        for service in self.services:
            try:
                result = await service.send_user_created_notification(user)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in notification service {type(service).__name__}: {e}")
                results.append(False)
        
        # Return True if at least one service succeeded
        return any(results)
    
    async def send_password_changed_notification(
        self, 
        user: User, 
        is_self_change: bool
    ) -> bool:
        """Send notification via all configured services."""
        results = []
        for service in self.services:
            try:
                result = await service.send_password_changed_notification(user, is_self_change)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in notification service {type(service).__name__}: {e}")
                results.append(False)
        
        return any(results)
    
    # Implement other methods following the same pattern...
    async def send_user_updated_notification(self, user: User) -> bool:
        results = [await service.send_user_updated_notification(user) for service in self.services]
        return any(results)
    
    async def send_role_changed_notification(self, user: User, old_role: str, new_role: str, reason: str) -> bool:
        results = [await service.send_role_changed_notification(user, old_role, new_role, reason) for service in self.services]
        return any(results)
    
    async def send_status_change_notification(self, user: User, old_status: str, new_status: str, reason: Optional[str] = None) -> bool:
        results = [await service.send_status_change_notification(user, old_status, new_status, reason) for service in self.services]
        return any(results)
    
    async def send_login_alert_notification(self, user: User, login_details: Dict[str, Any]) -> bool:
        results = [await service.send_login_alert_notification(user, login_details) for service in self.services]
        return any(results)
    
    async def send_profile_completion_reminder(self, user: User) -> bool:
        results = [await service.send_profile_completion_reminder(user) for service in self.services]
        return any(results)
    
    async def send_password_reset_email(self, email: str, temp_password: str) -> bool:
        results = [await service.send_password_reset_email(email, temp_password) for service in self.services]
        return any(results)
    
    async def send_admin_notification(
        self, 
        subject: str, 
        template: str = None,
        data: Dict[str, Any] = None
    ) -> bool:
        """Send admin notification via all configured services."""
        results = [await service.send_admin_notification(subject, template, data) for service in self.services]
        return any(results)
    
    async def notify_holiday_created(self, holiday) -> bool:
        """Send holiday created notification via all configured services."""
        results = []
        for service in self.services:
            try:
                result = await service.notify_holiday_created(holiday)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in notification service {type(service).__name__}: {e}")
                results.append(False)
        return any(results)
    
    async def notify_holiday_updated(self, holiday) -> bool:
        """Send holiday updated notification via all configured services."""
        results = []
        for service in self.services:
            try:
                result = await service.notify_holiday_updated(holiday)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in notification service {type(service).__name__}: {e}")
                results.append(False)
        return any(results)
    
    async def notify_holiday_deleted(self, holiday_id: str) -> bool:
        """Send holiday deleted notification via all configured services."""
        results = []
        for service in self.services:
            try:
                result = await service.notify_holiday_deleted(holiday_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in notification service {type(service).__name__}: {e}")
                results.append(False)
        return any(results) 