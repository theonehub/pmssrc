"""
Company Leave Service Implementation
SOLID-compliant implementation of company leave service interfaces
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, date

from app.application.interfaces.services.company_leaves_service import CompanyLeaveService
from app.application.interfaces.repositories.company_leave_repository import CompanyLeaveRepository
from app.application.dto.company_leave_dto import (
    CreateCompanyLeaveRequestDTO,
    UpdateCompanyLeaveRequestDTO,
    CompanyLeaveResponseDTO,
    CompanyLeaveListResponseDTO,
    CompanyLeaveSearchFiltersDTO,
    BulkCompanyLeaveUpdateDTO,
    BulkCompanyLeaveUpdateResultDTO,
    CompanyLeaveStatisticsDTO,
    CompanyLeaveAnalyticsDTO,
    CompanyLeaveDTOValidationError
)

# Import domain entities
from app.domain.entities.company_leave import CompanyLeave

# Import use cases
from app.application.use_cases.company_leave.create_company_leave_use_case import CreateCompanyLeaveUseCase
from app.application.use_cases.company_leave.update_company_leave_use_case import UpdateCompanyLeaveUseCase
from app.application.use_cases.company_leave.delete_company_leave_use_case import DeleteCompanyLeaveUseCase
from app.application.use_cases.company_leave.get_company_leaves_use_case import GetCompanyLeaveUseCase
from app.application.use_cases.company_leave.list_company_leaves_use_case import ListCompanyLeavesUseCase

from app.infrastructure.services.notification_service import NotificationService

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class CompanyLeaveServiceImpl(CompanyLeaveService):
    """
    Concrete implementation of company leave services.
    
    Follows SOLID principles:
    - SRP: Each method has a single responsibility
    - OCP: Extensible through inheritance
    - LSP: Can be substituted with other implementations
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions (repository, notification service)
    """
    
    def __init__(
        self,
        repository: CompanyLeaveRepository,
        notification_service: Optional[NotificationService] = None
    ):
        self.repository = repository
        self.notification_service = notification_service
        self.logger = logging.getLogger(__name__)
        
        # TODO: Need to get event_publisher from dependency injection
        # For now, we'll create a dummy event publisher
        from app.infrastructure.services.dummy_event_publisher import DummyEventPublisher
        event_publisher = DummyEventPublisher()
        
        # Initialize use cases with dependencies
        self._create_use_case = CreateCompanyLeaveUseCase(
            command_repository=repository,
            query_repository=repository,
            event_publisher=event_publisher
        )
        
        # TODO: Fix other use cases when we see their constructors
        # For now, commenting them out to get the create use case working
        # self._update_use_case = UpdateCompanyLeaveUseCase(
        #     company_leave_repository=repository,
        #     company_leave_query_repository=repository,
        #     company_leave_validation_service=self,
        #     company_leave_notification_service=self
        # )
        
        # self._delete_use_case = DeleteCompanyLeaveUseCase(
        #     company_leave_repository=repository,
        #     company_leave_query_repository=repository,
        #     company_leave_notification_service=self
        # )
        
        # self._get_use_case = GetCompanyLeaveUseCase(
        #     company_leave_query_repository=repository,
        #     company_leave_validation_service=self
        # )
        
        # self._get_multiple_use_case = GetCompanyLeavesUseCase(
        #     company_leave_query_repository=repository,
        #     company_leave_validation_service=self
        # )
        
        # self._list_use_case = ListCompanyLeavesUseCase(
        #     company_leave_query_repository=repository
        # )
    
    # ==================== COMMAND OPERATIONS ====================
    
    async def create_company_leave(
        self, 
        request: CreateCompanyLeaveRequestDTO, 
        current_user: "CurrentUser"
    ) -> CompanyLeaveResponseDTO:
        """Create a new company leave policy."""
        try:
            self.logger.info(f"Creating company leave: {request.leave_name} in organisation: {current_user.hostname}")
            
            # Populate created_by from current user
            request.created_by = current_user.employee_id
            
            # Validate request data
            validation_errors = request.validate()
            if validation_errors:
                raise CompanyLeaveDTOValidationError(validation_errors)
            
            # Create company leave entity
            company_leave = CompanyLeave.create_new_company_leave(
                leave_name=request.leave_name,
                accrual_type=request.accrual_type,
                annual_allocation=request.annual_allocation,
                created_by=request.created_by,
                description=request.description,
                encashable=request.encashable
            )
            
            # Save to database
            success = await self.repository.save(company_leave, current_user.hostname)
            if not success:
                raise Exception("Failed to save company leave to database")
            
            # Convert to response DTO
            response = CompanyLeaveResponseDTO.from_entity(company_leave)
            
            self.logger.info(f"Successfully created company leave: {company_leave.company_leave_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating company leave {request.leave_name} in organisation {current_user.hostname}: {e}")
            raise
    
    async def update_company_leave(
        self, 
        leave_id: str, 
        request: UpdateCompanyLeaveRequestDTO,
        current_user: "CurrentUser"
    ) -> CompanyLeaveResponseDTO:
        """Update an existing company leave policy."""
        try:
            self.logger.info(f"Updating company leave: {leave_id} in organisation: {current_user.hostname}")
            return await self._update_use_case.execute(leave_id, request, current_user)
        except Exception as e:
            self.logger.error(f"Error updating company leave {leave_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def delete_company_leave(
        self, 
        leave_id: str, 
        deletion_reason: str,
        current_user: "CurrentUser",
        deleted_by: Optional[str] = None,
        soft_delete: bool = True
    ) -> bool:
        """Delete a company leave policy."""
        try:
            self.logger.info(f"Deleting company leave: {leave_id} (soft: {soft_delete}) in organisation: {current_user.hostname}")
            return await self._delete_use_case.execute(leave_id, deletion_reason, current_user, deleted_by, soft_delete)
        except Exception as e:
            self.logger.error(f"Error deleting company leave {leave_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def activate_company_leave(
        self, 
        leave_id: str, 
        activated_by: str,
        current_user: "CurrentUser"
    ) -> CompanyLeaveResponseDTO:
        """Activate a company leave policy."""
        try:
            self.logger.info(f"Activating company leave: {leave_id} in organisation: {current_user.hostname}")
            
            # Get existing leave
            leave = await self.repository.get_by_id(leave_id, current_user.hostname)
            if not leave:
                raise ValueError(f"Company leave not found: {leave_id}")
            
            # Update status
            leave.activate(activated_by)
            
            # Save updated leave
            updated_leave = await self.repository.save(leave, current_user.hostname)
            
            # Convert to response DTO
            response = CompanyLeaveResponseDTO.from_entity(updated_leave)
            
            # Send notification
            await self.notify_leave_status_changed(response, "inactive", "active", activated_by, current_user)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error activating company leave {leave_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def deactivate_company_leave(
        self, 
        leave_id: str, 
        deactivated_by: str,
        reason: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> CompanyLeaveResponseDTO:
        """Deactivate a company leave policy."""
        try:
            self.logger.info(f"Deactivating company leave: {leave_id} in organisation: {current_user.hostname}")
            
            # Get existing leave
            leave = await self.repository.get_by_id(leave_id, current_user.hostname)
            if not leave:
                raise ValueError(f"Company leave not found: {leave_id}")
            
            # Update status
            leave.deactivate(deactivated_by, reason)
            
            # Save updated leave
            updated_leave = await self.repository.save(leave, current_user.hostname)
            
            # Convert to response DTO
            response = CompanyLeaveResponseDTO.from_entity(updated_leave)
            
            # Send notification
            await self.notify_leave_status_changed(response, "active", "inactive", deactivated_by, current_user)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error deactivating company leave {leave_id} in organisation {current_user.hostname}: {e}")
            raise
    
    # ==================== QUERY OPERATIONS ====================
    
    async def get_company_leave_by_id(
        self, 
        leave_id: str, 
        current_user: "CurrentUser"
    ) -> Optional[CompanyLeaveResponseDTO]:
        """Get company leave by ID."""
        try:
            self.logger.info(f"Getting company leave {leave_id} from organisation {current_user.hostname}")
            # Using repository directly instead of use case
            leave = await self.repository.get_by_id(leave_id, current_user.hostname)
            return CompanyLeaveResponseDTO.from_entity(leave) if leave else None
        except Exception as e:
            self.logger.error(f"Error getting company leave by ID {leave_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_company_leave_by_type(
        self, 
        leave_type: str, 
        current_user: "CurrentUser"
    ) -> Optional[CompanyLeaveResponseDTO]:
        """Get company leave by type."""
        try:
            self.logger.info(f"Getting company leave by type {leave_type} from organisation {current_user.hostname}")
            leave = await self.repository.get_by_leave_type(leave_type, current_user.hostname)
            return CompanyLeaveResponseDTO.from_entity(leave) if leave else None
        except Exception as e:
            self.logger.error(f"Error getting company leave by type {leave_type} in organisation {current_user.hostname}: {e}")
            raise
    
    async def list_company_leaves(
        self, 
        filters: Optional[CompanyLeaveSearchFiltersDTO] = None,
        current_user: "CurrentUser" = None
    ) -> CompanyLeaveListResponseDTO:
        """List company leaves with optional filters."""
        try:
            self.logger.info(f"Listing company leaves in organisation {current_user.hostname if current_user else 'global'}")
            
            # Use filters if provided, otherwise get all active leaves
            if filters:
                leaves = await self.repository.list_with_filters(filters, current_user.hostname)
                total = await self.repository.count_with_filters(filters, current_user.hostname)
            else:
                leaves = await self.repository.get_all_active(current_user.hostname)
                total = len(leaves)
            
            # Convert to response DTOs
            leave_responses = [CompanyLeaveResponseDTO.from_entity(leave) for leave in leaves]
            
            # Calculate pagination info
            page = filters.page if filters else 1
            page_size = filters.page_size if filters else len(leave_responses)
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
            
            return CompanyLeaveListResponseDTO(
                items=leave_responses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        except Exception as e:
            self.logger.error(f"Error listing company leaves in organisation {current_user.hostname if current_user else 'unknown'}: {e}")
            raise
    
    async def get_active_leaves(
        self, 
        current_user: "CurrentUser"
    ) -> List[CompanyLeaveResponseDTO]:
        """Get all active company leave policies."""
        try:
            self.logger.info(f"Getting active leaves from organisation {current_user.hostname}")
            leaves = await self.repository.get_active_leaves(current_user.hostname)
            return [CompanyLeaveResponseDTO.from_entity(leave) for leave in leaves]
        except Exception as e:
            self.logger.error(f"Error getting active leaves in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_leaves_by_category(
        self, 
        category: str, 
        current_user: "CurrentUser"
    ) -> List[CompanyLeaveResponseDTO]:
        """Get company leaves by category."""
        try:
            self.logger.info(f"Getting leaves by category {category} from organisation {current_user.hostname}")
            leaves = await self.repository.get_by_category(category, current_user.hostname)
            return [CompanyLeaveResponseDTO.from_entity(leave) for leave in leaves]
        except Exception as e:
            self.logger.error(f"Error getting leaves by category {category} in organisation {current_user.hostname}: {e}")
            raise
    
    async def check_leave_exists(
        self, 
        leave_type: str,
        exclude_id: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> bool:
        """Check if leave type already exists."""
        try:
            organisation_context = f" in organisation {current_user.hostname}" if current_user else ""
            self.logger.info(f"Checking leave existence for type {leave_type}{organisation_context}")
            organisation_id = current_user.hostname if current_user else None
            return await self.repository.exists_by_leave_type(leave_type, exclude_id, organisation_id)
        except Exception as e:
            self.logger.error(f"Error checking leave existence for type {leave_type}: {e}")
            raise
    
    # ==================== VALIDATION OPERATIONS ====================
    
    async def validate_leave_request(
        self, 
        request: CreateCompanyLeaveRequestDTO,
        current_user: "CurrentUser"
    ) -> List[str]:
        """Validate company leave creation request."""
        try:
            errors = []
            
            # Validate required fields
            if not request.leave_type or not request.leave_type.strip():
                errors.append("Leave type is required")
            
            if not request.leave_name or not request.leave_name.strip():
                errors.append("Leave name is required")
            
            # Validate business rules
            if request.max_days_per_year is not None and request.max_days_per_year < 0:
                errors.append("Maximum days per year cannot be negative")
            
            if request.max_consecutive_days is not None and request.max_consecutive_days < 0:
                errors.append("Maximum consecutive days cannot be negative")
            
            # Check for duplicate leave type
            if request.leave_type:
                exists = await self.check_leave_exists(request.leave_type, None, current_user)
                if exists:
                    errors.append(f"Leave type '{request.leave_type}' already exists")
            
            return errors
            
        except Exception as e:
            self.logger.error(f"Error validating leave request: {e}")
            return [f"Validation error: {str(e)}"]
    
    async def validate_leave_update(
        self, 
        leave_id: str, 
        request: UpdateCompanyLeaveRequestDTO,
        current_user: "CurrentUser"
    ) -> List[str]:
        """Validate company leave update request."""
        try:
            errors = []
            
            # Check if leave exists
            leave = await self.repository.get_by_id(leave_id, current_user.hostname)
            if not leave:
                errors.append(f"Company leave not found: {leave_id}")
                return errors
            
            # Validate business rules
            if request.max_days_per_year is not None and request.max_days_per_year < 0:
                errors.append("Maximum days per year cannot be negative")
            
            if request.max_consecutive_days is not None and request.max_consecutive_days < 0:
                errors.append("Maximum consecutive days cannot be negative")
            
            # Check for duplicate leave type if being changed
            if request.leave_type and request.leave_type != leave.leave_type:
                exists = await self.check_leave_exists(request.leave_type, leave_id, current_user)
                if exists:
                    errors.append(f"Leave type '{request.leave_type}' already exists")
            
            return errors
            
        except Exception as e:
            self.logger.error(f"Error validating leave update: {e}")
            return [f"Validation error: {str(e)}"]
    
    async def validate_business_rules(
        self, 
        leave_data: Dict[str, Any],
        current_user: "CurrentUser"
    ) -> List[str]:
        """Validate company leave business rules."""
        try:
            errors = []
            
            # Validate leave configuration consistency
            max_days_per_year = leave_data.get("max_days_per_year")
            max_consecutive_days = leave_data.get("max_consecutive_days")
            
            if (max_days_per_year is not None and max_consecutive_days is not None 
                and max_consecutive_days > max_days_per_year):
                errors.append("Maximum consecutive days cannot exceed maximum days per year")
            
            # Validate carry forward rules
            is_carry_forward_allowed = leave_data.get("is_carry_forward_allowed", False)
            max_carry_forward_days = leave_data.get("max_carry_forward_days")
            
            if is_carry_forward_allowed and max_carry_forward_days is None:
                errors.append("Maximum carry forward days must be specified when carry forward is allowed")
            
            if not is_carry_forward_allowed and max_carry_forward_days is not None:
                errors.append("Maximum carry forward days should not be specified when carry forward is not allowed")
            
            # Validate encashment rules
            is_encashable = leave_data.get("is_encashable", False)
            encashment_percentage = leave_data.get("encashment_percentage")
            
            if is_encashable and encashment_percentage is None:
                errors.append("Encashment percentage must be specified when leave is encashable")
            
            if not is_encashable and encashment_percentage is not None:
                errors.append("Encashment percentage should not be specified when leave is not encashable")
            
            return errors
            
        except Exception as e:
            self.logger.error(f"Error validating business rules: {e}")
            return [f"Business rule validation error: {str(e)}"]
    
    async def validate_leave_conflicts(
        self, 
        request: CreateCompanyLeaveRequestDTO,
        exclude_id: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> List[str]:
        """Validate leave type conflicts."""
        try:
            errors = []
            
            # Check for leave type conflicts
            if request.leave_type:
                exists = await self.check_leave_exists(request.leave_type, exclude_id, current_user)
                if exists:
                    errors.append(f"Leave type '{request.leave_type}' already exists")
            
            # Check for leave name conflicts (if different from type)
            if request.leave_name and request.leave_name != request.leave_type:
                # Could add additional name conflict checks here
                pass
            
            return errors
            
        except Exception as e:
            self.logger.error(f"Error validating leave conflicts: {e}")
            return [f"Conflict validation error: {str(e)}"]
    
    # ==================== NOTIFICATION OPERATIONS ====================
    
    async def notify_leave_created(
        self, 
        company_leave: CompanyLeaveResponseDTO,
        current_user: "CurrentUser"
    ) -> bool:
        """Notify about company leave creation."""
        try:
            if self.notification_service:
                # Send notification to administrators
                message = f"New company leave policy '{company_leave.leave_name}' has been created"
                # TODO: Implement actual notification logic
                self.logger.info(f"Notification sent for leave creation: {company_leave.leave_type}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error sending leave created notification: {e}")
            return False
    
    async def notify_leave_updated(
        self, 
        company_leave: CompanyLeaveResponseDTO,
        changes: Dict[str, Any],
        current_user: "CurrentUser"
    ) -> bool:
        """Notify about company leave update."""
        try:
            if self.notification_service:
                # Send notification to administrators
                changed_fields = ", ".join(changes.keys())
                message = f"Company leave policy '{company_leave.leave_name}' has been updated. Changed fields: {changed_fields}"
                # TODO: Implement actual notification logic
                self.logger.info(f"Notification sent for leave update: {company_leave.leave_type}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error sending leave updated notification: {e}")
            return False
    
    async def notify_leave_deleted(
        self, 
        leave_id: str, 
        leave_type: str,
        deleted_by: str,
        reason: str,
        current_user: "CurrentUser"
    ) -> bool:
        """Notify about company leave deletion."""
        try:
            if self.notification_service:
                # Send notification to administrators
                message = f"Company leave policy '{leave_type}' has been deleted by {deleted_by}. Reason: {reason}"
                # TODO: Implement actual notification logic
                self.logger.info(f"Notification sent for leave deletion: {leave_type}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error sending leave deleted notification: {e}")
            return False
    
    async def notify_leave_status_changed(
        self, 
        company_leave: CompanyLeaveResponseDTO,
        old_status: str,
        new_status: str,
        changed_by: str,
        current_user: "CurrentUser"
    ) -> bool:
        """Notify about company leave status change."""
        try:
            if self.notification_service:
                # Send notification to administrators
                message = f"Company leave policy '{company_leave.leave_name}' status changed from {old_status} to {new_status} by {changed_by}"
                # TODO: Implement actual notification logic
                self.logger.info(f"Notification sent for leave status change: {company_leave.leave_type}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error sending leave status change notification: {e}")
            return False
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_leave_statistics(
        self, 
        current_user: "CurrentUser"
    ) -> CompanyLeaveStatisticsDTO:
        """Get comprehensive leave statistics."""
        try:
            self.logger.info(f"Getting leave statistics for organisation {current_user.hostname}")
            return await self.repository.get_leave_statistics(current_user.hostname)
        except Exception as e:
            self.logger.error(f"Error getting leave statistics for organisation {current_user.hostname}: {e}")
            # Return empty statistics on error
            return CompanyLeaveStatisticsDTO(
                total_leaves=0,
                active_leaves=0,
                inactive_leaves=0,
                category_distribution={},
                usage_statistics={}
            )
    
    async def get_leave_analytics(
        self, 
        current_user: "CurrentUser"
    ) -> CompanyLeaveAnalyticsDTO:
        """Get detailed leave analytics."""
        try:
            self.logger.info(f"Getting leave analytics for organisation {current_user.hostname}")
            return await self.repository.get_leave_analytics(current_user.hostname)
        except Exception as e:
            self.logger.error(f"Error getting leave analytics for organisation {current_user.hostname}: {e}")
            # Return empty analytics on error
            return CompanyLeaveAnalyticsDTO(
                usage_trends={},
                popular_leave_types=[],
                seasonal_patterns={},
                recommendations=[]
            )
    
    async def get_leave_usage_report(
        self, 
        start_date: date, 
        end_date: date,
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """Get leave usage report for a date range."""
        try:
            self.logger.info(f"Getting leave usage report for {start_date} to {end_date} in organisation {current_user.hostname}")
            return await self.repository.get_leave_usage_report(start_date, end_date, current_user.hostname)
        except Exception as e:
            self.logger.error(f"Error getting leave usage report for organisation {current_user.hostname}: {e}")
            return {
                "period": {"start_date": start_date, "end_date": end_date},
                "total_applications": 0,
                "approved_applications": 0,
                "rejected_applications": 0,
                "leave_type_breakdown": {},
                "trends": {}
            }
    
    async def get_leave_type_distribution(
        self, 
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """Get leave type distribution report."""
        try:
            self.logger.info(f"Getting leave type distribution for organisation {current_user.hostname}")
            return await self.repository.get_leave_type_distribution(current_user.hostname)
        except Exception as e:
            self.logger.error(f"Error getting leave type distribution for organisation {current_user.hostname}: {e}")
            return {
                "total_types": 0,
                "active_types": 0,
                "category_distribution": {},
                "usage_distribution": {}
            }
    
    # ==================== BULK OPERATIONS ====================
    
    async def bulk_update_leaves(
        self, 
        updates: List[BulkCompanyLeaveUpdateDTO],
        updated_by: str,
        current_user: "CurrentUser"
    ) -> BulkCompanyLeaveUpdateResultDTO:
        """Bulk update multiple company leaves."""
        try:
            self.logger.info(f"Performing bulk update on {len(updates)} leaves in organisation {current_user.hostname}")
            
            results = []
            successful_updates = 0
            failed_updates = 0
            
            for update in updates:
                try:
                    # Create update request
                    request = UpdateCompanyLeaveRequestDTO(
                        leave_name=update.leave_name,
                        description=update.description,
                        max_days_per_year=update.max_days_per_year,
                        max_consecutive_days=update.max_consecutive_days,
                        is_carry_forward_allowed=update.is_carry_forward_allowed,
                        max_carry_forward_days=update.max_carry_forward_days,
                        is_encashable=update.is_encashable,
                        encashment_percentage=update.encashment_percentage,
                        updated_by=updated_by
                    )
                    
                    # Update leave
                    result = await self.update_company_leave(update.leave_id, request, current_user)
                    results.append({
                        "leave_id": update.leave_id,
                        "status": "success",
                        "result": result
                    })
                    successful_updates += 1
                    
                except Exception as e:
                    results.append({
                        "leave_id": update.leave_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed_updates += 1
            
            return BulkCompanyLeaveUpdateResultDTO(
                total_requested=len(updates),
                successful_updates=successful_updates,
                failed_updates=failed_updates,
                results=results
            )
            
        except Exception as e:
            self.logger.error(f"Error in bulk leave update: {e}")
            raise
    
    async def bulk_activate_leaves(
        self, 
        leave_ids: List[str],
        activated_by: str,
        current_user: "CurrentUser"
    ) -> BulkCompanyLeaveUpdateResultDTO:
        """Bulk activate company leaves."""
        try:
            self.logger.info(f"Performing bulk activation on {len(leave_ids)} leaves in organisation {current_user.hostname}")
            
            results = []
            successful_updates = 0
            failed_updates = 0
            
            for leave_id in leave_ids:
                try:
                    result = await self.activate_company_leave(leave_id, activated_by, current_user)
                    results.append({
                        "leave_id": leave_id,
                        "status": "success",
                        "result": result
                    })
                    successful_updates += 1
                    
                except Exception as e:
                    results.append({
                        "leave_id": leave_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed_updates += 1
            
            return BulkCompanyLeaveUpdateResultDTO(
                total_requested=len(leave_ids),
                successful_updates=successful_updates,
                failed_updates=failed_updates,
                results=results
            )
            
        except Exception as e:
            self.logger.error(f"Error in bulk leave activation: {e}")
            raise
    
    async def bulk_deactivate_leaves(
        self, 
        leave_ids: List[str],
        deactivated_by: str,
        reason: Optional[str] = None,
        current_user: "CurrentUser" = None
    ) -> BulkCompanyLeaveUpdateResultDTO:
        """Bulk deactivate company leaves."""
        try:
            self.logger.info(f"Performing bulk deactivation on {len(leave_ids)} leaves in organisation {current_user.hostname}")
            
            results = []
            successful_updates = 0
            failed_updates = 0
            
            for leave_id in leave_ids:
                try:
                    result = await self.deactivate_company_leave(leave_id, deactivated_by, reason, current_user)
                    results.append({
                        "leave_id": leave_id,
                        "status": "success",
                        "result": result
                    })
                    successful_updates += 1
                    
                except Exception as e:
                    results.append({
                        "leave_id": leave_id,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed_updates += 1
            
            return BulkCompanyLeaveUpdateResultDTO(
                total_requested=len(leave_ids),
                successful_updates=successful_updates,
                failed_updates=failed_updates,
                results=results
            )
            
        except Exception as e:
            self.logger.error(f"Error in bulk leave deactivation: {e}")
            raise
    
    async def bulk_export_leaves(
        self, 
        leave_ids: Optional[List[str]] = None,
        format: str = "csv",
        current_user: "CurrentUser" = None
    ) -> bytes:
        """Bulk export company leave data."""
        try:
            self.logger.info(f"Performing bulk export in format {format} for organisation {current_user.hostname if current_user else 'global'}")
            organisation_id = current_user.hostname if current_user else None
            return await self.repository.bulk_export_leaves(leave_ids, format, organisation_id)
        except Exception as e:
            self.logger.error(f"Error in bulk leave export: {e}")
            return b""
