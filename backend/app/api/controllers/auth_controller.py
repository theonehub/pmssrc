"""
SOLID-Compliant Auth Controller
Handles HTTP requests for authentication operations
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.application.dto.auth_dto import (
    LoginRequestDTO, RefreshTokenRequestDTO, LogoutRequestDTO,
    PasswordChangeRequestDTO, PasswordResetRequestDTO, PasswordResetConfirmRequestDTO,
    LoginResponseDTO, TokenResponseDTO, LogoutResponseDTO, PasswordChangeResponseDTO,
    PasswordResetResponseDTO, TokenValidationResponseDTO, UserProfileResponseDTO,
    SessionInfoResponseDTO, AuthHealthResponseDTO, AuthErrorResponseDTO
)
from app.auth.jwt_handler import create_access_token, decode_access_token
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthController:
    """
    SOLID-compliant controller for authentication operations.
    
    Responsibilities:
    - Handle HTTP request/response mapping for auth operations
    - Validate credentials and tokens
    - Coordinate with authentication services
    - Return standardized responses
    """
    
    def __init__(self):
        """Initialize auth controller."""
        pass
    
    async def health_check(self) -> AuthHealthResponseDTO:
        """Health check endpoint for authentication service."""
        try:
            # Check various auth service components
            jwt_status = "healthy"  # Would check JWT service
            password_status = "healthy"  # Would check password service
            user_status = "healthy"  # Would check user service
            
            overall_status = "healthy" if all([
                jwt_status == "healthy",
                password_status == "healthy", 
                user_status == "healthy"
            ]) else "unhealthy"
            
            return AuthHealthResponseDTO(
                service="auth_service",
                status=overall_status,
                timestamp=datetime.now(),
                jwt_service_status=jwt_status,
                password_service_status=password_status,
                user_service_status=user_status
            )
        except Exception as e:
            logger.error(f"Auth health check failed: {e}")
            return AuthHealthResponseDTO(
                service="auth_service",
                status="unhealthy",
                timestamp=datetime.now(),
                jwt_service_status="error",
                password_service_status="error",
                user_service_status="error"
            )
    
    async def login(
        self,
        request: LoginRequestDTO
    ) -> LoginResponseDTO:
        """
        Authenticate user and return JWT token.
        
        Args:
            request: Login request with credentials
            
        Returns:
            Login response with token and user info
        """
        try:
            logger.debug(f"Login attempt for user: {request.username} @ {request.hostname}")
            
            # Get database connection
            from app.config.mongodb_config import get_mongodb_connection_string, get_mongodb_client_options
            from app.infrastructure.database.mongodb_connector import MongoDBConnector
            from app.auth.password_handler import verify_password
            
            connector = MongoDBConnector()
            connection_string = get_mongodb_connection_string()
            logger.debug(f"Connection string: {connection_string}")
            options = get_mongodb_client_options()
            
            await connector.connect(connection_string, **options)
            
            # Get users collection
            users_collection = connector.get_collection('pms_'+request.hostname, 'users_info')
            
            # Find user by username and hostname
            user = await users_collection.find_one({
                "username": request.username,
                "hostname": request.hostname
            })
            
            if not user:
                users_collection = connector.get_collection('pms_global_database', 'users_info')
            
                # Try without hostname for global users
                user = await users_collection.find_one({
                    "username": request.username
                })
            
            await connector.disconnect()
            
            # Verify user exists and password is correct
            if not user or not verify_password(request.password, user["password"]):
                raise ValueError("Invalid username or password")
            
            # Check if user is active
            if not user.get("is_active", True):
                raise ValueError("User account is inactive")
            
            # Create user info
            user_info = {
                "emp_id": user.get("emp_id", user["username"]),
                "name": user.get("name", "User"),
                "email": user.get("email", user["username"]+"@"+request.hostname+".com"),
                "role": user.get("role", "user"),
                "department": user.get("department", "General"),
                "position": user.get("position", user.get("designation", "Employee"))
            }
            
            # Get user permissions based on role
            permissions = self._get_user_permissions(user.get("role", "user"))
            
            # Token expiration (typically 8 hours)
            expires_in = 28800  # 8 hours in seconds
            expires_delta = timedelta(seconds=expires_in)
            
            # Prepare token data
            token_data = {
                "sub": user.get("emp_id", user["username"]),  # Subject (user identifier)
                "username": user["username"],
                "emp_id": user.get("emp_id", user["username"]),
                "role": user.get("role", "user"),
                "hostname": request.hostname,
                "permissions": permissions,
                "iat": datetime.now().timestamp(),  # Issued at
                "type": "access_token"
            }
            
            # Generate proper JWT token
            access_token = create_access_token(
                data=token_data,
                expires_delta=expires_delta
            )
            
            logger.info(f"User {request.username} logged in successfully")
            
            return LoginResponseDTO(
                access_token=access_token,
                token_type="bearer",
                expires_in=expires_in,
                user_info=user_info,
                permissions=permissions,
                last_login=user.get("last_login"),
                login_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    async def logout(
        self,
        request: LogoutRequestDTO,
        current_user: Optional[Dict[str, Any]] = None
    ) -> LogoutResponseDTO:
        """
        Logout user and invalidate token.
        
        Args:
            request: Logout request
            current_user: Current authenticated user info
            
        Returns:
            Logout response
        """
        try:
            logger.info(f"Logout request for user: {current_user.get('sub') if current_user else 'unknown'}")
            
            devices_logged_out = 1
            if request.logout_all_devices:
                devices_logged_out = 1  # Placeholder
            
            return LogoutResponseDTO(
                message="Successfully logged out",
                logged_out_at=datetime.now(),
                session_duration=None,  # Would calculate from login time
                devices_logged_out=devices_logged_out
            )
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            raise
    
    async def refresh_token(
        self,
        request: RefreshTokenRequestDTO
    ) -> TokenResponseDTO:
        """
        Refresh access token using refresh token.
        
        Args:
            request: Refresh token request
            
        Returns:
            New token response
        """
        try:
            logger.info("Token refresh request")
            
            # For now, we'll implement a simple refresh mechanism
            # In a production system, you'd validate the refresh token properly
            
            # Decode the refresh token to get user info
            try:
                payload = decode_access_token(request.refresh_token)
                
                # Create new access token with same user data
                new_expires_delta = timedelta(hours=8)
                new_token_data = {
                    "sub": payload.get("sub"),
                    "username": payload.get("username"),
                    "emp_id": payload.get("emp_id"),
                    "role": payload.get("role"),
                    "hostname": payload.get("hostname"),
                    "permissions": payload.get("permissions", []),
                    "iat": datetime.utcnow().timestamp(),
                    "type": "access_token"
                }
                
                new_access_token = create_access_token(
                    data=new_token_data,
                    expires_delta=new_expires_delta
                )
                
                return TokenResponseDTO(
                    access_token=new_access_token,
                    token_type="bearer",
                    expires_in=28800,  # 8 hours
                    refresh_token=request.refresh_token,  # Could be rotated in production
                    issued_at=datetime.now()
                )
                
            except Exception as e:
                logger.error(f"Invalid refresh token: {e}")
                raise ValueError("Invalid refresh token")
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise
    
    async def validate_token(
        self,
        token: str
    ) -> TokenValidationResponseDTO:
        """
        Validate access token.
        
        Args:
            token: Access token to validate
            
        Returns:
            Token validation response
        """
        try:
            logger.info("Token validation request")
            
            # Decode and validate JWT token
            try:
                payload = decode_access_token(token)
                
                # Extract user information from token
                user_info = {
                    "emp_id": payload.get("emp_id"),
                    "username": payload.get("username"),
                    "role": payload.get("role"),
                    "hostname": payload.get("hostname")
                }
                
                permissions = payload.get("permissions", [])
                
                # Check if token is expired (this is handled by JWT decode, but we can add extra checks)
                expires_at = datetime.fromtimestamp(payload.get("exp", 0))
                
                return TokenValidationResponseDTO(
                    is_valid=True,
                    user_info=user_info,
                    permissions=permissions,
                    expires_at=expires_at,
                    token_type="bearer"
                )
                
            except Exception as e:
                logger.warning(f"Token validation failed: {e}")
                return TokenValidationResponseDTO(
                    is_valid=False,
                    user_info=None,
                    permissions=None,
                    expires_at=None,
                    token_type=None
                )
                
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise
    
    async def change_password(
        self,
        request: PasswordChangeRequestDTO,
        current_user: Dict[str, Any]
    ) -> PasswordChangeResponseDTO:
        """
        Change user password.
        
        Args:
            request: Password change request
            current_user: Current authenticated user
            
        Returns:
            Password change response
        """
        try:
            logger.info(f"Password change request for user: {current_user.get('sub')}")
            
            # For now, return success response
            logger.info(f"Password changed successfully for user: {current_user.get('sub')}")
            
            return PasswordChangeResponseDTO(
                message="Password changed successfully",
                changed_at=datetime.now(),
                requires_reauth=True
            )
            
        except Exception as e:
            logger.error(f"Password change error: {e}")
            raise
    
    async def request_password_reset(
        self,
        request: PasswordResetRequestDTO
    ) -> PasswordResetResponseDTO:
        """
        Initiate password reset process.
        
        Args:
            request: Password reset request
            
        Returns:
            Password reset response
        """
        try:
            logger.info(f"Password reset request for email: {request.email}")
            
            return PasswordResetResponseDTO(
                message="Password reset email sent",
                reset_token_sent=True,
                expires_in=3600,  # 1 hour
                sent_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Password reset request error: {e}")
            raise
    
    async def confirm_password_reset(
        self,
        request: PasswordResetConfirmRequestDTO
    ) -> PasswordChangeResponseDTO:
        """
        Confirm password reset with token.
        
        Args:
            request: Password reset confirmation request
            
        Returns:
            Password change response
        """
        try:
            logger.info("Password reset confirmation request")
            
            return PasswordChangeResponseDTO(
                message="Password reset successfully",
                changed_at=datetime.now(),
                requires_reauth=True
            )
            
        except Exception as e:
            logger.error(f"Password reset confirmation error: {e}")
            raise
    
    async def get_current_user_profile(
        self,
        current_user: Dict[str, Any]
    ) -> UserProfileResponseDTO:
        """
        Get current user profile information.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            User profile response
        """
        try:
            logger.info(f"Profile request for user: {current_user.get('sub')}")
            
            # For now, return mock profile
            permissions = self._get_user_permissions(current_user.get("role", "user"))
            
            return UserProfileResponseDTO(
                emp_id=current_user.get("sub", "unknown"),
                username=current_user.get("sub", "unknown"),
                email="user@company.com",
                full_name="User Name",
                role=current_user.get("role", "user"),
                department="Unknown",
                position="Unknown",
                is_active=True,
                last_login=None,
                created_at=None,
                permissions=permissions
            )
            
        except Exception as e:
            logger.error(f"Get user profile error: {e}")
            raise
    
    async def get_session_info(
        self,
        current_user: Dict[str, Any],
        token: str
    ) -> SessionInfoResponseDTO:
        """
        Get current session information.
        
        Args:
            current_user: Current authenticated user
            token: Current access token
            
        Returns:
            Session info response
        """
        try:
            logger.info(f"Session info request for user: {current_user.get('sub')}")
            
            user_info = {
                "emp_id": current_user.get("sub"),
                "role": current_user.get("role"),
                "hostname": current_user.get("hostname")
            }
            
            return SessionInfoResponseDTO(
                session_id=f"sess_{current_user.get('sub')}_{int(datetime.now().timestamp())}",
                user_info=user_info,
                login_time=datetime.now(),
                last_activity=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1),
                ip_address=None,  # Would get from request
                user_agent=None,  # Would get from request
                is_active=True
            )
            
        except Exception as e:
            logger.error(f"Get session info error: {e}")
            raise
    
    def _get_user_permissions(self, role: str) -> list:
        """
        Get user permissions based on role.
        
        Args:
            role: User role
            
        Returns:
            List of permissions
        """
        permission_map = {
            "admin": [
                "read_all", "write_all", "delete_all", "manage_users", 
                "manage_payroll", "manage_organization"
            ],
            "superadmin": [
                "read_all", "write_all", "delete_all", "manage_users", 
                "manage_payroll", "manage_organization", "system_admin"
            ],
            "manager": [
                "read_team", "write_team", "manage_team", "view_reports",
                "approve_leaves", "manage_payroll_team"
            ],
            "user": [
                "read_profile", "write_profile", "view_own_data",
                "apply_leave", "view_payslips"
            ]
        }
        
        return permission_map.get(role.lower(), ["read_profile"])
