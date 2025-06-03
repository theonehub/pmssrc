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