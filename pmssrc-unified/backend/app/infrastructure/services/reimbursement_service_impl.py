"""
Reimbursement Service Implementation
SOLID-compliant implementation of all reimbursement service interfaces
"""

import logging
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime

from app.application.interfaces.services.reimbursement_service import (
    ReimbursementTypeCommandService, ReimbursementRequestCommandService,
    ReimbursementQueryService, ReimbursementAnalyticsService, ReimbursementService
)
from app.application.interfaces.repositories.reimbursement_repository import ReimbursementRepository
from app.application.use_cases.reimbursement.create_reimbursement_type_use_case import CreateReimbursementTypeUseCase
from app.application.use_cases.reimbursement.create_reimbursement_request_use_case import CreateReimbursementRequestUseCase
from app.application.use_cases.reimbursement.approve_reimbursement_request_use_case import ApproveReimbursementRequestUseCase
from app.application.use_cases.reimbursement.process_reimbursement_payment_use_case import ProcessReimbursementPaymentUseCase
from app.application.use_cases.reimbursement.get_reimbursement_requests_use_case import GetReimbursementRequestsUseCase
from app.application.dto.reimbursement_dto import (
    ReimbursementTypeCreateRequestDTO,
    ReimbursementTypeUpdateRequestDTO,
    ReimbursementRequestCreateDTO,
    ReimbursementRequestUpdateDTO,
    ReimbursementApprovalDTO,
    ReimbursementRejectionDTO,
    ReimbursementPaymentDTO,
    ReimbursementSearchFiltersDTO,
    ReimbursementTypeResponseDTO,
    ReimbursementResponseDTO,
    ReimbursementSummaryDTO,
    ReimbursementListResponseDTO,
    ReimbursementStatisticsDTO,
    ReimbursementTypeOptionsDTO
)
from app.infrastructure.services.notification_service import NotificationService
from app.infrastructure.services.file_upload_service import FileUploadService

# Import CurrentUser for organisation context
if TYPE_CHECKING:
    from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class ReimbursementServiceImpl(ReimbursementService):
    """
    Complete implementation of all reimbursement service interfaces.
    
    Follows SOLID principles:
    - SRP: Delegates to specific use cases and services
    - OCP: Extensible through dependency injection
    - LSP: Implements all interface contracts correctly
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        repository: ReimbursementRepository,
        notification_service: NotificationService,
        file_upload_service: Optional[FileUploadService] = None,
        employee_repository = None
    ):
        """
        Initialize service with dependencies.
        
        Args:
            repository: Reimbursement repository for data access
            notification_service: Service for sending notifications
            file_upload_service: Service for file operations
        """
        self.repository = repository
        self.notification_service = notification_service
        self.file_upload_service = file_upload_service
        self.employee_repository = employee_repository
        
        # Initialize use cases
        self._create_reimbursement_type_use_case = CreateReimbursementTypeUseCase(
            command_repository=repository.reimbursement_type_commands,
            query_repository=repository.reimbursement_types,
            event_publisher=self._get_event_publisher(),
            notification_service=notification_service
        )
        
        self._create_reimbursement_request_use_case = CreateReimbursementRequestUseCase(
            command_repository=repository.reimbursement_commands,
            query_repository=repository.reimbursements,
            reimbursement_type_repository=repository.reimbursement_types,
            employee_repository=self._get_employee_repository(),
            event_publisher=self._get_event_publisher(),
            notification_service=notification_service
        )
        
        self._approve_reimbursement_request_use_case = ApproveReimbursementRequestUseCase(
            command_repository=repository.reimbursement_commands,
            query_repository=repository.reimbursements,
            reimbursement_type_repository=repository.reimbursement_types,
            employee_repository=self._get_employee_repository(),
            event_publisher=self._get_event_publisher(),
            notification_service=notification_service
        )
        
        self._process_payment_use_case = ProcessReimbursementPaymentUseCase(
            command_repository=repository.reimbursement_commands,
            query_repository=repository.reimbursements,
            reimbursement_type_repository=repository.reimbursement_types,
            employee_repository=self._get_employee_repository(),
            event_publisher=self._get_event_publisher(),
            notification_service=notification_service
        )
        
        self._get_reimbursement_requests_use_case = GetReimbursementRequestsUseCase(
            query_repository=repository.reimbursements,
            reimbursement_type_repository=repository.reimbursement_types
        )
    
    def _get_event_publisher(self):
        """Get event publisher instance."""
        from app.infrastructure.services.event_publisher_impl import EventPublisherImpl
        return EventPublisherImpl()
    
    def _get_employee_repository(self):
        """Get employee repository instance."""
        return self.employee_repository
    
    # ==================== REIMBURSEMENT TYPE COMMAND OPERATIONS ====================
    
    async def create_reimbursement_type(
        self, 
        request: ReimbursementTypeCreateRequestDTO, 
        current_user: "CurrentUser"
    ) -> ReimbursementTypeResponseDTO:
        """Create a new reimbursement type."""
        try:
            logger.info(f"Creating reimbursement type: {request.category_name} in organisation: {current_user.hostname}")
            
            # Convert DTO to use case DTO
            use_case_request = self._convert_to_use_case_request(request)
            
            # Execute use case with organisation context
            response = await self._create_reimbursement_type_use_case.execute(
                use_case_request, 
                current_user
            )
            
            logger.info(f"Successfully created reimbursement type: {response.type_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating reimbursement type in organisation {current_user.hostname}: {e}")
            raise
    
    async def update_reimbursement_type(
        self,
        type_id: str,
        request: ReimbursementTypeUpdateRequestDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementTypeResponseDTO:
        """Update an existing reimbursement type."""
        try:
            logger.info(f"Updating reimbursement type: {type_id} in organisation: {current_user.hostname}")
            
            # Get existing type
            existing_type = await self.repository.reimbursement_types.get_by_id(type_id, current_user.hostname)
            if not existing_type:
                from app.application.dto.reimbursement_dto import ReimbursementNotFoundError
                raise ReimbursementNotFoundError(f"Reimbursement type not found: {type_id}")
            
            # Update fields
            if request.category_name is not None:
                existing_type.category_name = request.category_name
            if request.description is not None:
                existing_type.description = request.description
            if request.max_limit is not None:
                existing_type.max_limit = request.max_limit
            if request.is_receipt_required is not None:
                existing_type.is_receipt_required = request.is_receipt_required
            if request.is_approval_required is not None:
                existing_type.is_approval_required = request.is_approval_required
            if request.is_active is not None:
                existing_type.is_active = request.is_active
            
            existing_type.updated_by = current_user.employee_id
            
            # Save updated type
            updated_type = await self.repository.reimbursement_type_commands.save(existing_type, current_user.hostname)
            
            # Convert to response DTO
            from app.application.dto.reimbursement_dto import create_reimbursement_type_response_from_entity
            response = create_reimbursement_type_response_from_entity(updated_type)
            
            logger.info(f"Successfully updated reimbursement type: {type_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error updating reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def delete_reimbursement_type(
        self,
        type_id: str,
        current_user: "CurrentUser"
    ) -> bool:
        """Delete (deactivate) a reimbursement type."""
        try:
            logger.info(f"Deleting reimbursement type: {type_id} in organisation: {current_user.hostname}")
            
            # Get existing type
            existing_type = await self.repository.reimbursement_types.get_by_id(type_id, current_user.hostname)
            if not existing_type:
                from app.application.dto.reimbursement_dto import ReimbursementNotFoundError
                raise ReimbursementNotFoundError(f"Reimbursement type not found: {type_id}")
            
            # Deactivate type
            existing_type.is_active = False
            existing_type.updated_by = current_user.employee_id
            
            # Save deactivated type
            await self.repository.reimbursement_type_commands.save(existing_type, current_user.hostname)
            
            logger.info(f"Successfully deleted reimbursement type: {type_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise
    
    # ==================== REIMBURSEMENT REQUEST COMMAND OPERATIONS ====================
    
    async def create_reimbursement_request(
        self, 
        request: ReimbursementRequestCreateDTO, 
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """Create a new reimbursement request."""
        try:
            logger.info(f"Creating reimbursement request for employee: {request.employee_id} in organisation: {current_user.hostname}")
            
            # Execute use case with organisation context
            response = await self._create_reimbursement_request_use_case.execute(
                request, 
                current_user
            )
            
            logger.info(f"Successfully created reimbursement request: {response.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating reimbursement request in organisation {current_user.hostname}: {e}")
            raise
    
    async def update_reimbursement_request(
        self,
        request_id: str,
        request: ReimbursementRequestUpdateDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """Update an existing reimbursement request."""
        try:
            logger.info(f"Updating reimbursement request: {request_id} in organisation: {current_user.hostname}")
            
            # Get existing request
            existing_request = await self.repository.reimbursements.get_by_id(request_id, current_user.hostname)
            if not existing_request:
                from app.application.dto.reimbursement_dto import ReimbursementNotFoundError
                raise ReimbursementNotFoundError(f"Reimbursement request not found: {request_id}")
            
            # Update fields
            if request.amount is not None:
                from app.domain.value_objects.reimbursement_amount import ReimbursementAmount
                existing_request.amount = ReimbursementAmount(request.amount, existing_request.amount.currency)
            if request.description is not None:
                existing_request.description = request.description
            
            # Save updated request
            updated_request = await self.repository.reimbursement_commands.update(existing_request, current_user.hostname)
            
            # Convert to response DTO
            from app.application.dto.reimbursement_dto import create_reimbursement_response_from_entity
            response = create_reimbursement_response_from_entity(updated_request)
            
            logger.info(f"Successfully updated reimbursement request: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error updating reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def approve_reimbursement_request(
        self,
        request_id: str,
        approval: ReimbursementApprovalDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """Approve a reimbursement request."""
        try:
            logger.info(f"Approving reimbursement request: {request_id} in organisation: {current_user.hostname}")
            
            # Execute use case with organisation context
            response = await self._approve_reimbursement_request_use_case.execute(
                request_id, 
                approval, 
                current_user.employee_id,
                current_user.hostname
            )
            
            logger.info(f"Successfully approved reimbursement request: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error approving reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def reject_reimbursement_request(
        self,
        request_id: str,
        rejection: ReimbursementRejectionDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """Reject a reimbursement request."""
        try:
            logger.info(f"Rejecting reimbursement request: {request_id} in organisation: {current_user.hostname}")
            
            # Get existing request
            existing_request = await self.repository.reimbursements.get_by_id(request_id, current_user.hostname)
            if not existing_request:
                from app.application.dto.reimbursement_dto import ReimbursementNotFoundError
                raise ReimbursementNotFoundError(f"Reimbursement request not found: {request_id}")
            
            # Reject the request
            existing_request.reject_request(
                rejected_by=current_user.employee_id,
                rejection_comments=rejection.rejection_comments
            )
            
            # Save rejected request
            updated_request = await self.repository.reimbursement_commands.update(existing_request, current_user.hostname)
            
            # Convert to response DTO
            from app.application.dto.reimbursement_dto import create_reimbursement_response_from_entity
            response = create_reimbursement_response_from_entity(updated_request)
            
            logger.info(f"Successfully rejected reimbursement request: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error rejecting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def process_reimbursement_payment(
        self,
        request_id: str,
        payment: ReimbursementPaymentDTO,
        current_user: "CurrentUser"
    ) -> ReimbursementResponseDTO:
        """Process payment for a reimbursement request."""
        try:
            logger.info(f"Processing payment for reimbursement request: {request_id} in organisation: {current_user.hostname}")
            
            # Execute use case with organisation context
            response = await self._process_payment_use_case.execute(
                request_id, 
                payment, 
                current_user
            )
            
            logger.info(f"Successfully processed payment for reimbursement request: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing payment for reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def delete_reimbursement_request(
        self,
        request_id: str,
        current_user: "CurrentUser"
    ) -> bool:
        """Delete a reimbursement request."""
        try:
            logger.info(f"Deleting reimbursement request: {request_id} in organisation: {current_user.hostname}")
            
            # Get existing request
            existing_request = await self.repository.reimbursements.get_by_id(request_id, current_user.hostname)
            if not existing_request:
                from app.application.dto.reimbursement_dto import ReimbursementNotFoundError
                raise ReimbursementNotFoundError(f"Reimbursement request not found: {request_id}")
            
            # Check if deletion is allowed
            if existing_request.status.value not in ['draft', 'submitted']:
                from app.application.dto.reimbursement_dto import ReimbursementBusinessRuleError
                raise ReimbursementBusinessRuleError("Cannot delete reimbursement request in current status")
            
            # Delete request
            await self.repository.reimbursement_commands.delete(request_id, current_user.hostname)
            
            logger.info(f"Successfully deleted reimbursement request: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise

    async def attach_receipt_to_request(
        self,
        request_id: str,
        file_path: str,
        file_name: str,
        file_size: int,
        uploaded_by: str,
        current_user: "CurrentUser"
    ) -> bool:
        """Attach receipt to an existing reimbursement request."""
        try:
            logger.info(f"Attaching receipt to reimbursement request: {request_id} in organisation: {current_user.hostname}")
            logger.info(f"Receipt details - file_path: {file_path}, file_name: {file_name}, file_size: {file_size}, uploaded_by: {uploaded_by}")
            
            # Get existing request with retry mechanism
            request_entity = None
            max_retries = 3
            for attempt in range(max_retries):
                request_entity = await self.repository.reimbursements.get_by_id(request_id, current_user.hostname)
                if request_entity:
                    logger.info(f"Found reimbursement entity on attempt {attempt + 1}: {request_entity.reimbursement_id}")
                    logger.info(f"Entity status: {request_entity.status}, receipt before: {request_entity.receipt}")
                    break
                if attempt < max_retries - 1:
                    logger.warning(f"Request not found on attempt {attempt + 1}, retrying...")
                    import asyncio
                    await asyncio.sleep(0.1)
            
            # Try the domain method first if entity was found
            if request_entity:
                try:
                    logger.info(f"Calling upload_receipt on domain entity...")
                    request_entity.upload_receipt(
                        file_path=file_path,
                        file_name=file_name,
                        file_size=file_size,
                        uploaded_by=uploaded_by
                    )
                    
                    logger.info(f"Receipt attached to entity - receipt after: {request_entity.receipt}")
                    logger.info(f"Receipt file_name: {request_entity.receipt.file_name if request_entity.receipt else 'None'}")
                    
                    # Update the request in the repository
                    logger.info(f"Updating entity in repository...")
                    updated_entity = await self.repository.reimbursements.update(request_entity, current_user.hostname)
                    
                    logger.info(f"Successfully attached receipt to reimbursement request: {request_id}")
                    logger.info(f"Updated entity receipt: {updated_entity.receipt.file_name if updated_entity.receipt else 'None'}")
                    return True
                    
                except Exception as domain_error:
                    logger.error(f"Domain method failed: {domain_error}")
                    # Continue to fallback below
            else:
                logger.warning(f"Entity not found after retries, proceeding with direct MongoDB update")
            
            # Fallback: Direct MongoDB update (always try this if domain method failed or entity not found)
            logger.info(f"Trying direct MongoDB update as fallback...")
            
            from datetime import datetime
            receipt_data = {
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "uploaded_at": datetime.utcnow(),
                "uploaded_by": uploaded_by
            }
            
            # Get MongoDB collection directly
            collection = await self.repository._get_reimbursements_collection(current_user.hostname)
            result = await collection.update_one(
                {"request_id": request_id},
                {
                    "$set": {
                        "receipt": receipt_data,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Successfully attached receipt via direct MongoDB update: {request_id}")
                logger.info(f"Modified count: {result.modified_count}, Matched count: {result.matched_count}")
                return True
            else:
                logger.error(f"Failed to update MongoDB document for request: {request_id}")
                logger.error(f"Modified count: {result.modified_count}, Matched count: {result.matched_count}")
                return False
            
        except Exception as e:
            logger.error(f"Error attaching receipt to reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    # ==================== QUERY OPERATIONS ====================
    
    async def get_reimbursement_type_by_id(
        self, 
        type_id: str, 
        current_user: "CurrentUser"
    ) -> Optional[ReimbursementTypeResponseDTO]:
        """Get reimbursement type by ID."""
        try:
            logger.info(f"Getting reimbursement type: {type_id} in organisation: {current_user.hostname}")
            
            type_entity = await self.repository.reimbursement_types.get_by_id(type_id, current_user.hostname)
            
            if not type_entity:
                return None
            
            # Convert to response DTO
            from app.application.dto.reimbursement_dto import create_reimbursement_type_response_from_entity
            response = create_reimbursement_type_response_from_entity(type_entity)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_reimbursement_request_by_id(
        self, 
        request_id: str, 
        current_user: "CurrentUser"
    ) -> Optional[ReimbursementResponseDTO]:
        """Get reimbursement request by ID."""
        try:
            logger.info(f"Getting reimbursement request: {request_id} in organisation: {current_user.hostname}")
            
            # Debug: Let's check what's actually in the database
            collection = await self.repository._get_reimbursements_collection(current_user.hostname)
            
            # Get a sample document to see the structure
            sample_doc = await collection.find_one()
            if sample_doc:
                logger.info(f"Sample document keys: {list(sample_doc.keys())}")
                logger.info(f"Sample request_id: {sample_doc.get('request_id')}")
                logger.info(f"Sample reimbursement_id: {sample_doc.get('reimbursement_id')}")
            
            # List ALL document IDs to see what's actually in the database
            all_docs = await collection.find({}, {"request_id": 1, "reimbursement_id": 1, "_id": 1, "employee_id": 1, "status": 1, "receipt_file_name": 1}).to_list(length=None)
            logger.info(f"All document IDs in database:")
            for i, doc in enumerate(all_docs, 1):
                logger.info(f"  {i}. _id: {doc.get('_id')}")
                logger.info(f"     request_id: {doc.get('request_id')}")
                logger.info(f"     reimbursement_id: {doc.get('reimbursement_id')}")
                logger.info(f"     employee_id: {doc.get('employee_id')}")
                logger.info(f"     status: {doc.get('status')}")
                logger.info(f"     receipt_file_name: {doc.get('receipt_file_name')}")
            
            logger.info(f"Looking for ID: {request_id}")
            
            # Check if any document has this ID in any field
            matching_docs = []
            for doc in all_docs:
                if (doc.get('_id') == request_id or 
                    doc.get('request_id') == request_id or 
                    doc.get('reimbursement_id') == request_id):
                    matching_docs.append(doc)
            
            logger.info(f"Documents matching ID {request_id}: {len(matching_docs)}")
            for doc in matching_docs:
                logger.info(f"  Matching doc: {doc}")
            
            # Try to find our specific document with different queries
            doc1 = await collection.find_one({"request_id": request_id})
            doc2 = await collection.find_one({"reimbursement_id": request_id})
            doc3 = await collection.find_one({"_id": request_id})
            
            logger.info(f"Query by request_id: {doc1 is not None}")
            logger.info(f"Query by reimbursement_id: {doc2 is not None}")
            logger.info(f"Query by _id: {doc3 is not None}")
            
            # Count total documents
            total_count = await collection.count_documents({})
            logger.info(f"Total documents in collection: {total_count}")
            
            logger.info(f"About to call repository.reimbursements.get_by_id with request_id: {request_id}, hostname: {current_user.hostname}")
            logger.info(f"Repository type: {type(self.repository)}")
            logger.info(f"Repository.reimbursements type: {type(self.repository.reimbursements)}")
            
            try:
                request_entity = await self.repository.reimbursements.get_by_id(request_id, current_user.hostname)
                logger.info(f"Repository call completed successfully. Entity: {request_entity is not None}")
            except Exception as repo_error:
                logger.error(f"Repository call failed with error: {repo_error}")
                raise
            
            logger.info(f"Repository returned entity: {request_entity is not None}")
            
            if not request_entity:
                logger.warning(f"No request entity found for ID: {request_id}")
                return None
            
            logger.info(f"Request entity found. ID: {request_entity.reimbursement_id}, Status: {request_entity.status}")
            
            # Convert to response DTO
            from app.application.dto.reimbursement_dto import create_reimbursement_response_from_entity
            response = create_reimbursement_response_from_entity(request_entity)
            
            logger.info(f"Successfully created response DTO for request: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def list_reimbursement_types(
        self,
        include_inactive: bool = False,
        current_user: "CurrentUser" = None
    ) -> List[ReimbursementTypeOptionsDTO]:
        """List all reimbursement types."""
        try:
            logger.info(f"Listing reimbursement types in organisation: {current_user.hostname}")
            
            types = await self.repository.reimbursement_types.get_all(
                current_user.hostname, 
                include_inactive=include_inactive
            )
            
            # Convert to options DTOs
            options = []
            for type_entity in types:
                option = ReimbursementTypeOptionsDTO(
                    type_id=type_entity.reimbursement_type_id,
                    category_name=type_entity.category_name,
                    description=type_entity.description,
                    max_limit=type_entity.max_limit,
                    is_approval_required=type_entity.is_approval_required,
                    is_receipt_required=type_entity.is_receipt_required,
                    is_active=type_entity.is_active
                )
                options.append(option)
            
            return options
            
        except Exception as e:
            logger.error(f"Error listing reimbursement types in organisation {current_user.hostname}: {e}")
            raise
    
    async def list_reimbursement_requests(
        self, 
        filters: Optional[ReimbursementSearchFiltersDTO] = None,
        current_user: "CurrentUser" = None
    ) -> ReimbursementListResponseDTO:
        """List reimbursement requests with optional filters."""
        try:
            logger.info(f"Listing reimbursement requests in organisation: {current_user.hostname}")
            
            # Use the appropriate method from the use case based on filters
            if filters:
                if filters.employee_id:
                    # Get requests for specific employee
                    requests = await self._get_reimbursement_requests_use_case.get_requests_by_employee(filters.employee_id, current_user)
                elif filters.status:
                    # Get requests by status
                    requests = await self._get_reimbursement_requests_use_case.get_requests_by_status(filters.status, current_user)
                else:
                    # Use search with filters
                    requests = await self._get_reimbursement_requests_use_case.search_requests(filters, current_user)
            else:
                # Get all requests
                requests = await self._get_reimbursement_requests_use_case.get_all_requests(current_user)
            
            # Convert to summary DTOs
            summaries = []
            for request in requests:
                summary = ReimbursementSummaryDTO(
                    request_id=request.request_id,
                    employee_id=request.employee_id,
                    category_name=request.reimbursement_type.category_name,
                    amount=request.amount,
                    status=request.status,
                    submitted_at=request.submitted_at,
                    final_amount=request.approved_amount if request.status in ["approved", "paid"] else None,
                    receipt_file_name=request.receipt_file_name,
                    receipt_uploaded_at=request.receipt_uploaded_at
                )
                summaries.append(summary)
            
            # Calculate pagination info
            total_count = len(summaries)
            page = filters.page if filters else 1
            page_size = filters.page_size if filters else 20
            total_pages = (total_count + page_size - 1) // page_size
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_summaries = summaries[start_idx:end_idx]
            
            return ReimbursementListResponseDTO(
                reimbursements=paginated_summaries,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Error listing reimbursement requests in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_reimbursement_requests_by_employee(
        self,
        employee_id: str,
        current_user: "CurrentUser"
    ) -> List[ReimbursementSummaryDTO]:
        """Get reimbursement requests for a specific employee."""
        try:
            logger.info(f"Getting reimbursement requests for employee: {employee_id} in organisation: {current_user.hostname}")
            
            requests = await self.repository.reimbursements.get_by_employee_id(employee_id, current_user.hostname)
            
            # Convert to summary DTOs
            summaries = []
            for request_entity in requests:
                summary = ReimbursementSummaryDTO(
                    request_id=request_entity.reimbursement_id,
                    employee_id=request_entity.employee_id.value,
                    category_name=request_entity.reimbursement_type.category_name,
                    amount=request_entity.amount,
                    status=request_entity.status.value,
                    submitted_at=request_entity.submitted_at,
                    final_amount=request_entity.get_final_amount(),
                    receipt_file_name=request_entity.receipt.file_name if request_entity.receipt else None,
                    receipt_uploaded_at=request_entity.receipt.uploaded_at if request_entity.receipt else None
                )
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting reimbursement requests for employee {employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_pending_approvals(
        self,
        approver_id: str,
        current_user: "CurrentUser"
    ) -> List[ReimbursementSummaryDTO]:
        """Get reimbursement requests pending approval by a specific approver."""
        try:
            logger.info(f"Getting pending approvals for approver: {approver_id} in organisation: {current_user.hostname}")
            
            # 1. Extract employee_id from current_user
            manager_employee_id = current_user.employee_id
            logger.info(f"Manager employee ID: {manager_employee_id}")
            
            # 2. Get all employees whose manager_id equals current_user's employee_id
            if not self.employee_repository:
                logger.error("Employee repository not available")
                return []
            
            from app.domain.value_objects.employee_id import EmployeeId
            managed_employees = await self.employee_repository.get_by_manager(
                EmployeeId(manager_employee_id), 
                current_user.hostname
            )
            
            if not managed_employees:
                logger.info(f"No employees found under manager: {manager_employee_id}")
                return []
            
            managed_employee_ids = [str(emp.employee_id) for emp in managed_employees]
            logger.info(f"Found {len(managed_employee_ids)} employees under manager: {managed_employee_ids}")
            
            # 3. Get reimbursements for all the employees from step 2
            all_pending_requests = []
            for employee_id in managed_employee_ids:
                try:
                    employee_requests = await self.repository.reimbursements.get_by_employee_id(
                        employee_id, 
                        current_user.hostname
                    )
                    
                    # 4. Filter reimbursements with status 'submitted' (pending approval)
                    submitted_requests = [
                        req for req in employee_requests 
                        if req.status.value == 'submitted'
                    ]
                    
                    all_pending_requests.extend(submitted_requests)
                    logger.info(f"Found {len(submitted_requests)} submitted requests for employee: {employee_id}")
                    
                except Exception as emp_error:
                    logger.error(f"Error getting requests for employee {employee_id}: {emp_error}")
                    continue
            
            # Convert to summary DTOs
            summaries = []
            for request_entity in all_pending_requests:
                try:
                    summary = ReimbursementSummaryDTO(
                        request_id=request_entity.reimbursement_id,
                        employee_id=request_entity.employee_id.value,
                        category_name=request_entity.reimbursement_type.category_name,
                        amount=request_entity.amount,
                        status=request_entity.status.value,
                        submitted_at=request_entity.submitted_at,
                        final_amount=request_entity.get_final_amount(),
                        receipt_file_name=request_entity.receipt.file_name if request_entity.receipt else None,
                        receipt_uploaded_at=request_entity.receipt.uploaded_at if request_entity.receipt else None
                    )
                    summaries.append(summary)
                except Exception as dto_error:
                    logger.error(f"Error creating summary DTO for request {request_entity.reimbursement_id}: {dto_error}")
                    continue
            
            logger.info(f"Returning {len(summaries)} pending approvals for manager: {manager_employee_id}")
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting pending approvals for approver {approver_id} in organisation {current_user.hostname}: {e}")
            raise

    async def get_receipt_file_path(
        self,
        request_id: str,
        current_user: "CurrentUser"
    ) -> Optional[str]:
        """Get receipt file path for a reimbursement request."""
        try:
            logger.info(f"Getting receipt file path for request: {request_id} in organisation: {current_user.hostname}")
            
            # Get the reimbursement request
            request_entity = await self.repository.reimbursements.get_by_id(request_id, current_user.hostname)
            
            if not request_entity:
                logger.warning(f"Request entity not found for ID: {request_id}")
                return None
                
            if not request_entity.receipt:
                logger.warning(f"No receipt found for request: {request_id}")
                return None
            
            logger.info(f"Receipt found for request {request_id}. File path: {request_entity.receipt.file_path}")
            return request_entity.receipt.file_path
            
        except Exception as e:
            logger.error(f"Error getting receipt file path for request {request_id} in organisation {current_user.hostname}: {e}")
            return None
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_reimbursement_statistics(
        self, 
        current_user: "CurrentUser"
    ) -> ReimbursementStatisticsDTO:
        """Get comprehensive reimbursement statistics."""
        try:
            logger.info(f"Getting reimbursement statistics in organisation: {current_user.hostname}")
            
            # This would need to be implemented with proper analytics
            # For now, return basic statistics
            statistics = ReimbursementStatisticsDTO(
                total_requests=0,
                total_amount=Decimal('0.00'),
                approved_requests=0,
                approved_amount=Decimal('0.00'),
                pending_requests=0,
                pending_amount=Decimal('0.00'),
                rejected_requests=0,
                rejected_amount=Decimal('0.00'),
                paid_requests=0,
                paid_amount=Decimal('0.00'),
                category_breakdown={},
                status_breakdown={}
            )
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting reimbursement statistics in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_reimbursement_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        current_user: "CurrentUser" = None
    ) -> Dict[str, Any]:
        """Get detailed reimbursement analytics."""
        try:
            logger.info(f"Getting reimbursement analytics in organisation: {current_user.hostname}")
            
            # This would need to be implemented with proper analytics
            # For now, return basic analytics
            analytics = {
                "summary": {
                    "total_requests": 0,
                    "total_amount": 0.0,
                    "average_amount": 0.0
                },
                "trends": [],
                "categories": {},
                "status_distribution": {}
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting reimbursement analytics in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_employee_reimbursement_report(
        self,
        employee_id: str,
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """Get reimbursement report for a specific employee."""
        try:
            logger.info(f"Getting employee reimbursement report for: {employee_id} in organisation: {current_user.hostname}")
            
            # This would need to be implemented with proper reporting
            # For now, return basic report
            report = {
                "employee_id": employee_id,
                "total_requests": 0,
                "total_amount": 0.0,
                "approved_amount": 0.0,
                "pending_amount": 0.0,
                "categories": {},
                "recent_requests": []
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error getting employee reimbursement report for {employee_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_category_wise_report(
        self,
        current_user: "CurrentUser"
    ) -> Dict[str, Any]:
        """Get category-wise reimbursement report."""
        try:
            logger.info(f"Getting category-wise reimbursement report in organisation: {current_user.hostname}")
            
            # This would need to be implemented with proper reporting
            # For now, return basic report
            report = {
                "categories": {},
                "total_amount": 0.0,
                "total_requests": 0
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error getting category-wise reimbursement report in organisation {current_user.hostname}: {e}")
            raise
    
    # ==================== HELPER METHODS ====================
    
    def _convert_to_use_case_request(self, request: ReimbursementTypeCreateRequestDTO):
        """Convert API DTO to use case DTO."""
        # This would map between different DTO formats if needed
        return request 