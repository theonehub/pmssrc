"""
Create User Use Case
Handles the business logic for creating a new user
"""

import logging
from typing import List, Dict
from datetime import datetime

from app.domain.entities.user import User
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.user_credentials import (
    UserRole, UserStatus, Gender
)
from app.domain.value_objects.user_permissions import UserPermissions
from app.domain.value_objects.personal_details import PersonalDetails
from app.domain.value_objects.user_documents import UserDocuments
from app.application.dto.user_dto import (
    CreateUserRequestDTO, UserResponseDTO,
    UserValidationError, UserConflictError,
    UserBusinessRuleError,
    PersonalDetailsResponseDTO,
    UserPermissionsResponseDTO,
    UserDocumentsResponseDTO
)
from app.application.interfaces.repositories.user_repository import (
    UserCommandRepository, UserQueryRepository
)
from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveQueryRepository
)
from app.application.interfaces.services.user_service import (
    UserValidationService, UserNotificationService
)
from app.auth.auth_dependencies import CurrentUser


logger = logging.getLogger(__name__)


class CreateUserUseCase:
    """
    Use case for creating a new user.
    
    Follows SOLID principles:
    - SRP: Only handles user creation logic
    - OCP: Can be extended with new validation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories, services)
    
    Business Rules:
    1. Employee ID must be unique
    2. Email must be unique
    3. Mobile number must be unique (if provided)
    4. PAN number must be unique (if provided)
    5. All required fields must be provided
    6. Password must meet security requirements
    7. Personal details must be valid
    8. User role must be valid
    9. Manager must exist (if assigned)
    """
    
    def __init__(
        self,
        command_repository: UserCommandRepository,
        query_repository: UserQueryRepository,
        validation_service: UserValidationService,
        notification_service: UserNotificationService,
        company_leave_query_repository: CompanyLeaveQueryRepository
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.validation_service = validation_service
        self.notification_service = notification_service
        self.company_leave_query_repository = company_leave_query_repository
    
    async def execute(self, request: CreateUserRequestDTO, current_user: CurrentUser) -> UserResponseDTO:
        """
        Execute the create user use case.
        
        Args:
            request: User creation request DTO
            current_user: Current authenticated user with organisation context
        Returns:
            Created user response DTO
            
        Raises:
            UserValidationError: If request data is invalid
            UserConflictError: If user already exists
            UserBusinessRuleError: If business rules are violated
        """
        logger.info(f"Creating user: {request.email} in organisation: {current_user.hostname}")
        
        # Step 1: Validate request data
        await self._validate_request(request)
        
        # Step 2: Check uniqueness constraints
        await self._check_uniqueness_constraints(request, current_user)
        
        # Step 3: Create value objects
        employee_id = EmployeeId(request.employee_id)
        personal_details = self._create_personal_details(request)
        documents = self._create_user_documents(request)
        
        # Step 3.5: Calculate initial leave balance based on company policies
        initial_leave_balances = await self._calculate_initial_leave_balance(
            UserRole(request.role.lower()), current_user
        )
        
        # Step 4: Create user entity
        user = User.create_new_user(
            employee_id=employee_id,
            name=request.name,
            email=request.email,
            password=request.password,
            role=UserRole(request.role.lower()),
            personal_details=personal_details,
            department=request.department,
            designation=request.designation,
            location=request.location,
            manager_id=EmployeeId(request.manager_id) if request.manager_id else None,
            date_of_joining=request.date_of_joining,
            created_by=request.created_by
        )
        
        # Step 4.5: Set documents and leave balances after user creation
        user.update_documents(documents, user.created_by or "system")
        # Set initial leave balances for each leave type
        for leave_name, balance in initial_leave_balances.items():
            user.update_leave_balance(leave_name, int(balance))
        
        # Step 5: Validate business rules
        await self._validate_business_rules(user)
        
        # Step 6: Save user
        saved_user = await self.command_repository.save(user, current_user.hostname)
        
        # Step 7: Send notifications (non-blocking)
        try:
            await self.notification_service.send_user_created_notification(saved_user)
        except Exception as e:
            logger.warning(f"Failed to send user created notification: {e}")
        
        # Step 8: Convert to response DTO
        response = self._convert_to_response_dto(saved_user)
        
        logger.info(f"User created successfully: {saved_user.employee_id}")
        return response
    
    async def _validate_request(self, request: CreateUserRequestDTO) -> None:
        """Validate the request data"""
        validation_errors = await self.validation_service.validate_user_data(request)
        
        if validation_errors:
            raise UserValidationError(
                "User creation data is invalid",
                validation_errors
            )
    
    async def _check_uniqueness_constraints(self, request: CreateUserRequestDTO, current_user: CurrentUser) -> None:
        """Check uniqueness constraints"""
        uniqueness_result = await self.validation_service.validate_uniqueness_constraints(
            email=request.email,
            mobile=request.mobile,
            pan_number=request.pan_number,  
            current_user=current_user
        )
        
        if uniqueness_result.get("email_exists") or uniqueness_result.get("mobile_exists") or uniqueness_result.get("pan_exists"):
            raise UserConflictError(
                "User conflicts with existing data " + str(uniqueness_result),
                "uniqueness"
            )
    
    def _create_personal_details(self, request: CreateUserRequestDTO) -> PersonalDetails:
        """Create personal details value object"""
        try:
            return PersonalDetails(
                gender=Gender(request.gender.lower()),
                date_of_birth=datetime.fromisoformat(request.date_of_birth).date(),
                date_of_joining=datetime.fromisoformat(request.date_of_joining).date(),
                mobile=request.mobile,
                pan_number=request.pan_number,
                aadhar_number=request.aadhar_number,
                uan_number=request.uan_number,
                esi_number=request.esi_number
            )
        except ValueError as e:
            raise UserValidationError(f"Invalid personal details: {e}")
    
    def _create_user_documents(self, request: CreateUserRequestDTO) -> UserDocuments:
        """Create user documents value object"""
        try:
            return UserDocuments(
                photo_path=request.photo_path,
                pan_document_path=request.pan_document_path,
                aadhar_document_path=request.aadhar_document_path
            )
        except ValueError as e:
            raise UserValidationError(f"Invalid user documents: {e}")
    
    async def _validate_business_rules(self, user: User) -> None:
        """Validate business rules"""
        business_rule_errors = await self.validation_service.validate_business_rules(user)
        
        if business_rule_errors:
            raise UserBusinessRuleError(
                "User violates business rules",
                "business_rules"
            )
    
    async def _calculate_initial_leave_balance(self, role: UserRole, current_user: CurrentUser) -> Dict[str, float]:
        """
        Calculate initial leave balance based on company leave policies.
        
        Args:
            role: User role
            current_user: Current authenticated user with organisation context
            
        Returns:
            Dictionary with leave_name as key and computed_monthly_allocation as value
        """
        try:
            # Fetch active company leave policies for the organisation
            company_leaves = await self.company_leave_query_repository.get_all_active(current_user.hostname)
            
            initial_balances = {}
            
            if company_leaves:
                # Use company leave policies to set initial balances
                for company_leave in company_leaves:
                    # Use leave_name as key and computed_monthly_allocation as value
                    initial_balances[company_leave.leave_name] = float(company_leave.computed_monthly_allocation)
                
                logger.info(f"Calculated initial leave balances from company policies for organisation {current_user.hostname}: {initial_balances}")
            else:
                # Fallback to default leave balances if no company policies found
                logger.warning(f"No company leave policies found for organisation {current_user.hostname}, using default balances")
                
                initial_balances = {
                    "Sick Leave": 0
                }
            
            return initial_balances
            
        except Exception as e:
            logger.warning(f"Error calculating initial leave balances, using default: {e}")
            # Default fallback with standard leave types
            return {
                "Sick Leave": 0
            }
    

    def _convert_to_response_dto(self, user: User) -> UserResponseDTO:
        """Convert user entity to response DTO"""
        return UserResponseDTO(
            employee_id=str(user.employee_id),
            name=user.name,
            email=user.email,
            status=user.status.value,
            
            # Personal Details
            personal_details=PersonalDetailsResponseDTO(
                gender=user.personal_details.gender.value,
                date_of_birth=user.personal_details.date_of_birth.isoformat(),
                date_of_joining=user.personal_details.date_of_joining.isoformat(),
                mobile=user.personal_details.mobile,
                pan_number=user.personal_details.pan_number,
                aadhar_number=user.personal_details.get_masked_aadhar(),
                uan_number=user.personal_details.uan_number,
                esi_number=user.personal_details.esi_number,
            ),
            
            # Employment Information
            department=user.department,
            designation=user.designation,
            location=user.location,
            manager_id=str(user.manager_id) if user.manager_id else None,
            date_of_joining=user.personal_details.date_of_joining.isoformat() if user.personal_details.date_of_joining else user.date_of_joining,
            date_of_leaving=user.date_of_leaving,
            
            # Authorization
            permissions=UserPermissionsResponseDTO(
                role=user.permissions.role.value,
                custom_permissions=user.permissions.custom_permissions,
                resource_permissions=user.permissions.resource_permissions,
                can_manage_users=user.permissions.can_manage_users(),
                can_view_reports=user.permissions.can_view_reports(),
                can_approve_requests=user.permissions.can_approve_requests(),
                is_admin=user.permissions.is_admin(),
                is_superadmin=user.permissions.is_superadmin(),
            ),
            
            # Documents
            documents=self._convert_documents_to_dto(user.documents),
            
            # Leave Balance
            leave_balance=user.leave_balance,
            
            # System Fields
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
            created_by=user.created_by,
            updated_by=user.updated_by,
            last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
            
            # Computed fields
            is_active=user.is_active(),
            is_locked=user.is_locked(),
            can_login=user.can_login(),
            profile_completion_percentage=user.get_profile_completion_percentage(),
            display_name=user.get_display_name(),
            role_display=user.get_role_display(),
            status_display=user.get_status_display(),
        )
    
    def _convert_documents_to_dto(self, documents: UserDocuments) -> UserDocumentsResponseDTO:
        """Convert user documents to DTO format"""
        return UserDocumentsResponseDTO(
            photo_path=documents.photo_path,
            pan_document_path=documents.pan_document_path,
            aadhar_document_path=documents.aadhar_document_path,
            completion_percentage=documents.get_document_completion_percentage(),
            missing_documents=documents.get_missing_documents()
        )


class MonthlyLeaveAllocationUseCase:
    """
    Use case for adding monthly leave allocation to users.
    
    This use case should be called by a scheduled job (e.g., monthly cron job)
    to add the computed_monthly_allocation to each user's leave balance.
    
    Follows SOLID principles:
    - SRP: Only handles monthly leave allocation logic
    - OCP: Can be extended with new allocation rules
    - LSP: Can be substituted with enhanced versions
    - ISP: Depends on focused interfaces
    - DIP: Depends on abstractions (repositories)
    """
    
    def __init__(
        self,
        user_command_repository: UserCommandRepository,
        user_query_repository: UserQueryRepository,
        company_leave_query_repository: CompanyLeaveQueryRepository
    ):
        self.user_command_repository = user_command_repository
        self.user_query_repository = user_query_repository
        self.company_leave_query_repository = company_leave_query_repository
    
    async def execute_for_organisation(self, current_user: CurrentUser) -> Dict[str, int]:
        """
        Execute monthly leave allocation for all active users in an organisation.
        
        Args:
            current_user: Current authenticated user with organisation context
            
        Returns:
            Dictionary with statistics about the allocation process
        """
        logger.info(f"Starting monthly leave allocation for organisation: {current_user.hostname}")
        
        stats = {
            "users_processed": 0,
            "users_updated": 0,
            "users_failed": 0,
            "leave_types_processed": 0
        }
        
        try:
            # Fetch active company leave policies for the organisation
            company_leaves = await self.company_leave_query_repository.get_all_active(current_user.hostname)
            
            if not company_leaves:
                logger.warning(f"No company leave policies found for organisation {current_user.hostname}")
                return stats
            
            stats["leave_types_processed"] = len(company_leaves)
            
            # Fetch all active users in the organisation
            active_users = await self.user_query_repository.get_active_users(current_user.hostname)
            
            for user in active_users:
                stats["users_processed"] += 1
                
                try:
                    # Add monthly allocation for each leave type
                    user_updated = False
                    
                    for company_leave in company_leaves:
                        leave_name = company_leave.leave_name
                        monthly_allocation = float(company_leave.computed_monthly_allocation)
                        
                        # Get current balance for this leave type
                        current_balance = user.leave_balance.get(leave_name, 0)
                        
                        # Add monthly allocation
                        new_balance = current_balance + monthly_allocation
                        
                        # Update user's leave balance
                        user.update_leave_balance(leave_name, int(new_balance))
                        user_updated = True
                        
                        logger.debug(f"Added monthly allocation for user {user.employee_id}, {leave_name}: "
                                   f"{monthly_allocation} days. Previous: {current_balance}, New: {new_balance}")
                    
                    # Save the updated user
                    if user_updated:
                        await self.user_command_repository.save(user, current_user.hostname)
                        stats["users_updated"] += 1
                        logger.info(f"Successfully updated monthly leave allocation for user {user.employee_id}")
                
                except Exception as e:
                    stats["users_failed"] += 1
                    logger.error(f"Failed to update monthly leave allocation for user {user.employee_id}: {e}")
                    continue
            
            logger.info(f"Monthly leave allocation completed for organisation {current_user.hostname}. Stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error during monthly leave allocation for organisation {current_user.hostname}: {e}")
            raise
    
    async def execute_for_user(self, user_id: str, current_user: CurrentUser) -> bool:
        """
        Execute monthly leave allocation for a specific user.
        
        Args:
            user_id: Employee ID of the user
            current_user: Current authenticated user with organisation context
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Adding monthly leave allocation for user {user_id} in organisation {current_user.hostname}")
            
            # Fetch the user
            user = await self.user_query_repository.get_by_employee_id(user_id, current_user.hostname)
            if not user:
                logger.error(f"User {user_id} not found in organisation {current_user.hostname}")
                return False
            
            # Fetch active company leave policies for the organisation
            company_leaves = await self.company_leave_query_repository.get_all_active(current_user.hostname)
            
            if not company_leaves:
                logger.warning(f"No company leave policies found for organisation {current_user.hostname}")
                return False
            
            # Add monthly allocation for each leave type
            user_updated = False
            
            for company_leave in company_leaves:
                leave_name = company_leave.leave_name
                monthly_allocation = float(company_leave.computed_monthly_allocation)
                
                # Get current balance for this leave type
                current_balance = user.leave_balance.get(leave_name, 0)
                
                # Add monthly allocation
                new_balance = current_balance + monthly_allocation
                
                # Update user's leave balance
                user.update_leave_balance(leave_name, int(new_balance))
                user_updated = True
                
                logger.info(f"Added monthly allocation for user {user_id}, {leave_name}: "
                           f"{monthly_allocation} days. Previous: {current_balance}, New: {new_balance}")
            
            # Save the updated user
            if user_updated:
                await self.user_command_repository.save(user, current_user.hostname)
                logger.info(f"Successfully updated monthly leave allocation for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding monthly leave allocation for user {user_id}: {e}")
            return False


# Example usage for scheduled jobs:
"""
# Monthly Leave Allocation Scheduled Job Example

from app.application.use_cases.user.create_user_use_case import MonthlyLeaveAllocationUseCase
from app.config.dependency_container import get_dependency_container

async def monthly_leave_allocation_job():
    '''
    Scheduled job to run monthly leave allocation for all organisations.
    This should be called by a cron job or task scheduler.
    '''
    container = get_dependency_container()
    
    # Get repositories
    user_command_repo = container.get_user_command_repository()
    user_query_repo = container.get_user_query_repository()
    company_leave_query_repo = container.get_company_leave_query_repository()
    
    # Create use case
    monthly_allocation_use_case = MonthlyLeaveAllocationUseCase(
        user_command_repository=user_command_repo,
        user_query_repository=user_query_repo,
        company_leave_query_repository=company_leave_query_repo
    )
    
    # Example: Process for a specific organisation
    # You would need to iterate through all organisations in your system
    from app.auth.auth_dependencies import CurrentUser
    
    # Mock current user for organisation context
    current_user = CurrentUser(
        employee_id="SYSTEM",
        hostname="example-org.com",  # Replace with actual organisation hostname
        role="superadmin"
    )
    
    try:
        stats = await monthly_allocation_use_case.execute_for_organisation(current_user)
        print(f"Monthly allocation completed for {current_user.hostname}: {stats}")
    except Exception as e:
        print(f"Error in monthly allocation for {current_user.hostname}: {e}")

# For individual user allocation:
async def add_monthly_allocation_for_user(user_id: str, organisation_hostname: str):
    '''
    Add monthly allocation for a specific user.
    Useful for new joiners or manual adjustments.
    '''
    container = get_dependency_container()
    
    user_command_repo = container.get_user_command_repository()
    user_query_repo = container.get_user_query_repository()
    company_leave_query_repo = container.get_company_leave_query_repository()
    
    monthly_allocation_use_case = MonthlyLeaveAllocationUseCase(
        user_command_repository=user_command_repo,
        user_query_repository=user_query_repo,
        company_leave_query_repository=company_leave_query_repo
    )
    
    current_user = CurrentUser(
        employee_id="SYSTEM",
        hostname=organisation_hostname,
        role="superadmin"
    )
    
    success = await monthly_allocation_use_case.execute_for_user(user_id, current_user)
    return success
""" 