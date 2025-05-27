"""
Authenticate User Use Case
Handles the business logic for user authentication and login
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

from domain.entities.user import User
from domain.value_objects.user_credentials import UserStatus
from application.dto.user_dto import (
    UserLoginRequestDTO, UserLoginResponseDTO,
    UserAuthenticationError, UserBusinessRuleError
)
from application.interfaces.repositories.user_repository import (
    UserCommandRepository, UserQueryRepository
)
from application.interfaces.services.user_service import (
    UserNotificationService
)


logger = logging.getLogger(__name__)


class AuthenticateUserUseCase:
    """
    Use case for authenticating a user.
    
    Follows SOLID principles:
    - SRP: Only handles user authentication logic
    - OCP: Can be extended with new authentication methods
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. User must exist
    2. User must be active
    3. User must not be locked
    4. Password must be correct
    5. Login attempts are tracked
    6. Account locks after failed attempts
    7. Login activity is logged
    8. Session tokens are generated
    """
    
    def __init__(
        self,
        command_repository: UserCommandRepository,
        query_repository: UserQueryRepository,
        notification_service: UserNotificationService
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.notification_service = notification_service
    
    async def execute(self, request: UserLoginRequestDTO) -> UserLoginResponseDTO:
        """
        Execute the authenticate user use case.
        
        Args:
            request: User login request DTO
            
        Returns:
            User login response DTO with tokens and user info
            
        Raises:
            UserAuthenticationError: If authentication fails
            UserBusinessRuleError: If user cannot login (locked, inactive, etc.)
        """
        logger.info(f"Authenticating user: {request.email}")
        
        # Step 1: Get user by email
        user = await self._get_user_by_email(request.email)
        
        # Step 2: Check if user can login
        await self._check_login_eligibility(user)
        
        # Step 3: Authenticate password
        authentication_result = await self._authenticate_password(user, request.password)
        
        if not authentication_result.success:
            # Handle failed authentication
            await self._handle_failed_authentication(user, request)
            raise UserAuthenticationError(
                "Invalid credentials",
                "authentication_failed"
            )
        
        # Step 4: Handle successful authentication
        await self._handle_successful_authentication(user, request)
        
        # Step 5: Generate tokens
        tokens = await self._generate_tokens(user)
        
        # Step 6: Send notifications (non-blocking)
        try:
            await self._send_login_notifications(user, request)
        except Exception as e:
            logger.warning(f"Failed to send login notifications: {e}")
        
        # Step 7: Convert to response DTO
        response = self._convert_to_response_dto(user, tokens)
        
        logger.info(f"User authenticated successfully: {user.employee_id}")
        return response
    
    async def _get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        user = await self.query_repository.get_by_email(email)
        
        if not user:
            raise UserAuthenticationError(
                "Invalid credentials",
                "user_not_found"
            )
        
        return user
    
    async def _check_login_eligibility(self, user: User) -> None:
        """Check if user can login"""
        if not user.is_active():
            raise UserBusinessRuleError(
                "User account is not active",
                "account_inactive"
            )
        
        if user.is_locked():
            raise UserBusinessRuleError(
                "User account is locked",
                "account_locked"
            )
        
        if user.status == UserStatus.SUSPENDED:
            raise UserBusinessRuleError(
                "User account is suspended",
                "account_suspended"
            )
    
    async def _authenticate_password(self, user: User, password: str) -> dict:
        """Authenticate user password"""
        try:
            result = user.authenticate(password)
            return {
                "success": result,
                "user": user
            }
        except Exception as e:
            logger.warning(f"Authentication error for user {user.employee_id}: {e}")
            return {
                "success": False,
                "user": user,
                "error": str(e)
            }
    
    async def _handle_failed_authentication(self, user: User, request: UserLoginRequestDTO) -> None:
        """Handle failed authentication attempt"""
        # User entity handles login attempt tracking and account locking
        # The authenticate method already increments failed attempts
        
        # Save updated user state
        await self.command_repository.save(user)
        
        logger.warning(
            f"Failed authentication attempt for user {user.employee_id} "
            f"from IP {request.ip_address}"
        )
    
    async def _handle_successful_authentication(self, user: User, request: UserLoginRequestDTO) -> None:
        """Handle successful authentication"""
        # Reset failed login attempts and update last login
        user.reset_failed_login_attempts()
        user.update_last_login(
            ip_address=request.ip_address,
            user_agent=request.user_agent
        )
        
        # Save updated user state
        await self.command_repository.save(user)
        
        logger.info(
            f"Successful authentication for user {user.employee_id} "
            f"from IP {request.ip_address}"
        )
    
    async def _generate_tokens(self, user: User) -> dict:
        """Generate authentication tokens"""
        # This would typically use a JWT service or similar
        # For now, we'll create a simple token structure
        
        access_token_expiry = datetime.utcnow() + timedelta(hours=8)
        refresh_token_expiry = datetime.utcnow() + timedelta(days=30)
        
        return {
            "access_token": f"access_token_for_{user.employee_id}_{int(datetime.utcnow().timestamp())}",
            "refresh_token": f"refresh_token_for_{user.employee_id}_{int(datetime.utcnow().timestamp())}",
            "token_type": "Bearer",
            "expires_in": 28800,  # 8 hours in seconds
            "access_token_expiry": access_token_expiry.isoformat(),
            "refresh_token_expiry": refresh_token_expiry.isoformat()
        }
    
    async def _send_login_notifications(self, user: User, request: UserLoginRequestDTO) -> None:
        """Send login notifications"""
        login_details = {
            "ip_address": request.ip_address,
            "user_agent": request.user_agent,
            "login_time": datetime.utcnow().isoformat(),
            "location": request.location,
            "device_info": request.device_info
        }
        
        # Check for suspicious login activity
        if await self._is_suspicious_login(user, request):
            await self.notification_service.send_login_alert_notification(user, login_details)
    
    async def _is_suspicious_login(self, user: User, request: UserLoginRequestDTO) -> bool:
        """Check if login is suspicious"""
        # Simple heuristics for suspicious login detection
        # In a real implementation, this would be more sophisticated
        
        # Check if login from new IP address
        # Check if login from new location
        # Check if login at unusual time
        # etc.
        
        return False  # Placeholder implementation
    
    def _convert_to_response_dto(self, user: User, tokens: dict) -> UserLoginResponseDTO:
        """Convert to login response DTO"""
        return UserLoginResponseDTO(
            # Tokens
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            
            # User Information
            user_id=str(user.employee_id),
            employee_id=str(user.employee_id),
            name=user.name,
            email=user.email,
            role=user.role.value,
            status=user.status.value,
            
            # Permissions
            permissions=user.permissions.get_all_permissions(),
            
            # Profile Information
            department=user.department,
            designation=user.designation,
            profile_completion_percentage=user.calculate_profile_completion(),
            
            # Login Information
            last_login=user.last_login.isoformat() if user.last_login else None,
            login_count=user.login_count,
            
            # Security Information
            password_expires_at=user.password.expires_at.isoformat() if user.password.expires_at else None,
            must_change_password=user.password.is_expired(),
            
            # Session Information
            session_expires_at=tokens["access_token_expiry"],
            refresh_expires_at=tokens["refresh_token_expiry"]
        ) 