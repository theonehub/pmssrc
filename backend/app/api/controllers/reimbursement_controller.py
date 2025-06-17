"""
Reimbursement Controller Implementation
SOLID-compliant controller for reimbursement HTTP operations with organisation segregation
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, UploadFile

from app.application.interfaces.services.reimbursement_service import ReimbursementService
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
    ReimbursementTypeOptionsDTO,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError,
    ReimbursementNotFoundError
)
from app.infrastructure.services.file_upload_service import FileUploadService, DocumentType
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class ReimbursementController:
    """
    Reimbursement controller following SOLID principles with organisation segregation.
    
    - SRP: Only handles HTTP request/response concerns
    - OCP: Can be extended with new endpoints
    - LSP: Can be substituted with other controllers
    - ISP: Focused interface for reimbursement HTTP operations
    - DIP: Depends on abstractions (ReimbursementService, FileUploadService)
    """
    
    def __init__(
        self,
        reimbursement_service: ReimbursementService,
        file_upload_service: FileUploadService
    ):
        """
        Initialize controller with dependencies.
        
        Args:
            reimbursement_service: Reimbursement service for business operations
            file_upload_service: Service for file operations
        """
        self.reimbursement_service = reimbursement_service
        self.file_upload_service = file_upload_service
        self._initialized = True
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for reimbursement controller."""
        return {
            "service": "reimbursement_controller",
            "status": "healthy", 
            "controller": "ReimbursementController",
            "initialized": self._initialized,
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-organisation-segregated"
        }
    
    # ==================== REIMBURSEMENT TYPE OPERATIONS ====================
    
    async def create_reimbursement_type(
        self, 
        request: ReimbursementTypeCreateRequestDTO,
        current_user: CurrentUser
    ) -> ReimbursementTypeResponseDTO:
        """Create a new reimbursement type with organisation context."""
        try:
            logger.info(f"Creating reimbursement type: {request.category_name} in organisation: {current_user.hostname}")
            return await self.reimbursement_service.create_reimbursement_type(request, current_user)
        except ReimbursementValidationError as e:
            logger.error(f"Validation error creating reimbursement type {request.category_name} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error creating reimbursement type {request.category_name} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating reimbursement type {request.category_name} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_reimbursement_type(
        self, 
        type_id: str,
        current_user: CurrentUser
    ) -> ReimbursementTypeResponseDTO:
        """Get reimbursement type by ID with organisation context."""
        try:
            reimbursement_type = await self.reimbursement_service.get_reimbursement_type_by_id(type_id, current_user)
            if not reimbursement_type:
                raise HTTPException(status_code=404, detail="Reimbursement type not found")
            return reimbursement_type
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def list_reimbursement_types(
        self,
        include_inactive: bool = False,
        current_user: CurrentUser = None
    ) -> List[ReimbursementTypeOptionsDTO]:
        """Get all reimbursement types with organisation context."""
        try:
            return await self.reimbursement_service.list_reimbursement_types(
                include_inactive=include_inactive,
                current_user=current_user
            )
        except Exception as e:
            logger.error(f"Error getting reimbursement types in organisation {current_user.hostname if current_user else 'unknown'}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def update_reimbursement_type(
        self, 
        type_id: str,
        request: ReimbursementTypeUpdateRequestDTO,
        current_user: CurrentUser
    ) -> ReimbursementTypeResponseDTO:
        """Update reimbursement type with organisation context."""
        try:
            return await self.reimbursement_service.update_reimbursement_type(type_id, request, current_user)
        except ReimbursementNotFoundError as e:
            logger.error(f"Reimbursement type not found {type_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ReimbursementValidationError as e:
            logger.error(f"Validation error updating reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error updating reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def delete_reimbursement_type(
        self, 
        type_id: str,
        current_user: CurrentUser
    ) -> Dict[str, str]:
        """Delete (deactivate) reimbursement type with organisation context."""
        try:
            success = await self.reimbursement_service.delete_reimbursement_type(type_id, current_user)
            if success:
                return {"message": "Reimbursement type deleted successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to delete reimbursement type")
        except ReimbursementNotFoundError as e:
            logger.error(f"Reimbursement type not found {type_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error deleting reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error deleting reimbursement type {type_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    # ==================== REIMBURSEMENT REQUEST OPERATIONS ====================
    
    async def create_reimbursement_request(
        self, 
        request: ReimbursementRequestCreateDTO,
        current_user: CurrentUser
    ) -> ReimbursementResponseDTO:
        """Create a new reimbursement request with organisation context."""
        try:
            logger.info(f"Creating reimbursement request for employee: {request.employee_id} in organisation: {current_user.hostname}")
            return await self.reimbursement_service.create_reimbursement_request(request, current_user)
        except ReimbursementValidationError as e:
            logger.error(f"Validation error creating reimbursement request for employee {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error creating reimbursement request for employee {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating reimbursement request for employee {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def create_reimbursement_request_with_file(
        self,
        request: ReimbursementRequestCreateDTO,
        receipt_file: UploadFile,
        current_user: CurrentUser
    ) -> ReimbursementResponseDTO:
        """Create reimbursement request with file upload and organisation context."""
        try:
            logger.info(f"Creating reimbursement request with file for employee: {request.employee_id} in organisation: {current_user.hostname}")
            
            # First create the reimbursement request
            reimbursement_response = await self.reimbursement_service.create_reimbursement_request(request, current_user)
            
            # Handle file upload with organisation-specific path
            receipt_path = await self.file_upload_service.upload_document(
                receipt_file, DocumentType.RECEIPT, current_user.hostname
            )
            
            # Add a small delay to ensure the document is available in the database
            import asyncio
            await asyncio.sleep(0.1)
            
            # Now attach the receipt to the created reimbursement with retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    success = await self.reimbursement_service.attach_receipt_to_request(
                        reimbursement_response.request_id,
                        receipt_path,
                        receipt_file.filename or "receipt",
                        receipt_file.size or 0,
                        current_user.employee_id,
                        current_user
                    )
                    
                    if success:
                        break
                    else:
                        logger.warning(f"Failed to attach receipt on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(0.2)  # Wait before retry
                        
                except Exception as e:
                    logger.warning(f"Error attaching receipt on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.2)  # Wait before retry
                    else:
                        # If all retries failed, log the error but don't fail the entire request
                        logger.error(f"Failed to attach receipt after {max_retries} attempts: {e}")
                        # Return the reimbursement without receipt attachment
                        return reimbursement_response
            
            # Return the updated reimbursement with receipt information
            updated_response = await self.reimbursement_service.get_reimbursement_request_by_id(
                reimbursement_response.request_id, current_user
            )
            
            return updated_response or reimbursement_response
            
        except ReimbursementValidationError as e:
            logger.error(f"Validation error creating reimbursement request with file for employee {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error creating reimbursement request with file for employee {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating reimbursement request with file for employee {request.employee_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_reimbursement_request(
        self, 
        request_id: str,
        current_user: CurrentUser
    ) -> ReimbursementResponseDTO:
        """Get reimbursement request by ID with organisation context."""
        try:
            reimbursement_request = await self.reimbursement_service.get_reimbursement_request_by_id(request_id, current_user)
            if not reimbursement_request:
                raise HTTPException(status_code=404, detail="Reimbursement request not found")
            return reimbursement_request
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_receipt_file_path(
        self,
        request_id: str,
        current_user: CurrentUser
    ) -> Optional[str]:
        """Get receipt file path for a reimbursement request."""
        try:
            return await self.reimbursement_service.get_receipt_file_path(request_id, current_user)
        except Exception as e:
            logger.error(f"Error getting receipt file path for request {request_id} in organisation {current_user.hostname}: {e}")
            return None
    
    async def list_reimbursement_requests(
        self,
        filters: Optional[ReimbursementSearchFiltersDTO] = None,
        current_user: CurrentUser = None
    ) -> ReimbursementListResponseDTO:
        """Get reimbursement requests with filters and organisation context."""
        try:
            return await self.reimbursement_service.list_reimbursement_requests(filters, current_user)
        except Exception as e:
            logger.error(f"Error listing reimbursement requests in organisation {current_user.hostname if current_user else 'unknown'}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def update_reimbursement_request(
        self,
        request_id: str,
        request: ReimbursementRequestUpdateDTO,
        current_user: CurrentUser
    ) -> ReimbursementResponseDTO:
        """Update reimbursement request with organisation context."""
        try:
            return await self.reimbursement_service.update_reimbursement_request(request_id, request, current_user)
        except ReimbursementNotFoundError as e:
            logger.error(f"Reimbursement request not found {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ReimbursementValidationError as e:
            logger.error(f"Validation error updating reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error updating reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def approve_reimbursement_request(
        self, 
        request_id: str,
        approval: ReimbursementApprovalDTO,
        current_user: CurrentUser
    ) -> ReimbursementResponseDTO:
        """Approve reimbursement request with organisation context."""
        try:
            logger.info(f"Approving reimbursement request: {request_id} in organisation: {current_user.hostname}")
            return await self.reimbursement_service.approve_reimbursement_request(request_id, approval, current_user)
        except ReimbursementNotFoundError as e:
            logger.error(f"Reimbursement request not found {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ReimbursementValidationError as e:
            logger.error(f"Validation error approving reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error approving reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error approving reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def reject_reimbursement_request(
        self, 
        request_id: str,
        rejection: ReimbursementRejectionDTO,
        current_user: CurrentUser
    ) -> ReimbursementResponseDTO:
        """Reject reimbursement request with organisation context."""
        try:
            logger.info(f"Rejecting reimbursement request: {request_id} in organisation: {current_user.hostname}")
            return await self.reimbursement_service.reject_reimbursement_request(request_id, rejection, current_user)
        except ReimbursementNotFoundError as e:
            logger.error(f"Reimbursement request not found {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ReimbursementValidationError as e:
            logger.error(f"Validation error rejecting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error rejecting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error rejecting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def process_reimbursement_payment(
        self,
        request_id: str,
        payment: ReimbursementPaymentDTO,
        current_user: CurrentUser
    ) -> ReimbursementResponseDTO:
        """Process payment for reimbursement request with organisation context."""
        try:
            logger.info(f"Processing payment for reimbursement request: {request_id} in organisation: {current_user.hostname}")
            return await self.reimbursement_service.process_reimbursement_payment(request_id, payment, current_user)
        except ReimbursementNotFoundError as e:
            logger.error(f"Reimbursement request not found {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ReimbursementValidationError as e:
            logger.error(f"Validation error processing payment for reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error processing payment for reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error processing payment for reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def delete_reimbursement_request(
        self, 
        request_id: str,
        current_user: CurrentUser
    ) -> Dict[str, str]:
        """Delete reimbursement request with organisation context."""
        try:
            success = await self.reimbursement_service.delete_reimbursement_request(request_id, current_user)
            if success:
                return {"message": "Reimbursement request deleted successfully"}
            else:
                raise HTTPException(status_code=500, detail="Failed to delete reimbursement request")
        except ReimbursementNotFoundError as e:
            logger.error(f"Reimbursement request not found {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ReimbursementBusinessRuleError as e:
            logger.error(f"Business rule error deleting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Error deleting reimbursement request {request_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    # ==================== EMPLOYEE-SPECIFIC OPERATIONS ====================
    
    async def get_my_reimbursement_requests(
        self,
        current_user: CurrentUser
    ) -> List[ReimbursementSummaryDTO]:
        """Get reimbursement requests for current user with organisation context."""
        try:
            return await self.reimbursement_service.get_reimbursement_requests_by_employee(
                current_user.employee_id, current_user
            )
        except Exception as e:
            logger.error(f"Error getting reimbursement requests for user {current_user.employee_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_pending_approvals(
        self,
        current_user: CurrentUser
    ) -> List[ReimbursementSummaryDTO]:
        """Get pending approvals for current user with organisation context."""
        try:
            return await self.reimbursement_service.get_pending_approvals(
                current_user.employee_id, current_user
            )
        except Exception as e:
            logger.error(f"Error getting pending approvals for user {current_user.employee_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    async def get_reimbursement_statistics(
        self, 
        current_user: CurrentUser
    ) -> ReimbursementStatisticsDTO:
        """Get reimbursement statistics with organisation context."""
        try:
            return await self.reimbursement_service.get_reimbursement_statistics(current_user)
        except Exception as e:
            logger.error(f"Error getting reimbursement statistics in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
 
    # ==================== LEGACY COMPATIBILITY METHODS ====================
    # These are for backward compatibility and should be deprecated
    
    async def create_reimbursement(
        self, 
        request: ReimbursementRequestCreateDTO,
        employee_id: str,
        current_user: CurrentUser
    ) -> ReimbursementResponseDTO:
        """Legacy method: Create reimbursement (alias for create_reimbursement_request)."""
        request.employee_id = employee_id
        return await self.create_reimbursement_request(request, current_user)
    
    async def get_reimbursement_types(
        self,
        filters: Optional[Dict[str, Any]] = None,
        current_user: CurrentUser = None
    ) -> List[ReimbursementTypeOptionsDTO]:
        """Legacy method: Get reimbursement types."""
        include_inactive = filters.get('include_inactive', False) if filters else False
        return await self.list_reimbursement_types(include_inactive, current_user)
    
    async def get_reimbursement_requests(
        self, 
        filters: ReimbursementSearchFiltersDTO,
        current_user: CurrentUser
    ) -> ReimbursementListResponseDTO:
        """Legacy method: Get reimbursement requests."""
        return await self.list_reimbursement_requests(filters, current_user)
    
    