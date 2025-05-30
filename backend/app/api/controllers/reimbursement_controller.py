"""
SOLID-Compliant Reimbursement Controller
Handles reimbursement-related HTTP operations with proper dependency injection
"""

import logging
from typing import List, Optional
from datetime import datetime

from app.application.dto.reimbursement_dto import (
    ReimbursementRequestCreateDTO,
    ReimbursementTypeCreateRequestDTO,
    ReimbursementApprovalDTO,
    ReimbursementPaymentDTO,
    ReimbursementSearchFiltersDTO,
    ReimbursementResponseDTO,
    ReimbursementTypeResponseDTO,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError
)

logger = logging.getLogger(__name__)


class ReimbursementController:
    """
    Controller for reimbursement operations following SOLID principles.
    
    This controller acts as a facade between the HTTP layer and business logic,
    delegating operations to appropriate use cases.
    """
    
    def __init__(
        self,
        create_type_use_case=None,
        create_request_use_case=None,
        approve_request_use_case=None,
        get_requests_use_case=None,
        process_payment_use_case=None
    ):
        """
        Initialize the controller with use cases.
        
        Args:
            create_type_use_case: Use case for creating reimbursement types
            create_request_use_case: Use case for creating reimbursement requests
            approve_request_use_case: Use case for approving requests
            get_requests_use_case: Use case for querying requests
            process_payment_use_case: Use case for processing payments
        """
        self.create_type_use_case = create_type_use_case
        self.create_request_use_case = create_request_use_case
        self.approve_request_use_case = approve_request_use_case
        self.get_requests_use_case = get_requests_use_case
        self.process_payment_use_case = process_payment_use_case
        
        # If use cases are not provided, we'll handle gracefully
        self._initialized = all([
            create_type_use_case is not None,
            create_request_use_case is not None,
            approve_request_use_case is not None,
            get_requests_use_case is not None,
            process_payment_use_case is not None
        ])
        
        if not self._initialized:
            logger.warning("ReimbursementController initialized without all required use cases")
    
    async def create_reimbursement_type(self, request: ReimbursementTypeCreateRequestDTO, hostname: str) -> ReimbursementTypeResponseDTO:
        """Create a new reimbursement type"""
        try:
            logger.info(f"Creating reimbursement type: {request.name}")
            
            if self.create_type_use_case:
                return await self.create_type_use_case.execute(request, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_type_response(request)
                
        except Exception as e:
            logger.error(f"Error creating reimbursement type: {e}")
            raise ReimbursementBusinessRuleError(f"Type creation failed: {str(e)}")
    
    async def get_reimbursement_types(self, filters, hostname: str) -> List[ReimbursementTypeResponseDTO]:
        """Get reimbursement types"""
        try:
            logger.info("Getting reimbursement types")
            
            if self.get_requests_use_case:
                return await self.get_requests_use_case.get_types(filters, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_type_list()
                
        except Exception as e:
            logger.error(f"Error getting reimbursement types: {e}")
            raise ReimbursementBusinessRuleError(f"Failed to get types: {str(e)}")
    
    async def create_reimbursement_request(self, request: ReimbursementRequestCreateDTO, hostname: str) -> ReimbursementResponseDTO:
        """Create a new reimbursement request"""
        try:
            logger.info(f"Creating reimbursement request for employee: {request.employee_id}")
            
            if self.create_request_use_case:
                return await self.create_request_use_case.execute(request, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_request_response(request)
                
        except Exception as e:
            logger.error(f"Error creating reimbursement request: {e}")
            raise ReimbursementBusinessRuleError(f"Request creation failed: {str(e)}")
    
    async def create_reimbursement_request_with_file(self, request: ReimbursementRequestCreateDTO, file, hostname: str) -> ReimbursementResponseDTO:
        """Create a new reimbursement request with file upload"""
        try:
            logger.info(f"Creating reimbursement request with file for employee: {request.employee_id}")
            
            # Handle file upload logic here
            # For now, just create a request without the file
            return await self.create_reimbursement_request(request, hostname)
                
        except Exception as e:
            logger.error(f"Error creating reimbursement request with file: {e}")
            raise ReimbursementBusinessRuleError(f"Request creation with file failed: {str(e)}")
    
    async def get_reimbursement_requests(self, filters: ReimbursementSearchFiltersDTO, hostname: str) -> List[ReimbursementResponseDTO]:
        """Get reimbursement requests with filters"""
        try:
            logger.info(f"Getting reimbursement requests with filters")
            
            if self.get_requests_use_case:
                return await self.get_requests_use_case.execute(filters, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_request_list(filters)
                
        except Exception as e:
            logger.error(f"Error getting reimbursement requests: {e}")
            raise ReimbursementBusinessRuleError(f"Failed to get requests: {str(e)}")
    
    async def approve_reimbursement_request(self, request_id: str, approval: ReimbursementApprovalDTO, hostname: str) -> ReimbursementResponseDTO:
        """Approve a reimbursement request"""
        try:
            logger.info(f"Approving reimbursement request: {request_id}")
            
            if self.approve_request_use_case:
                return await self.approve_request_use_case.execute(request_id, approval, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_approved_response(request_id)
                
        except Exception as e:
            logger.error(f"Error approving reimbursement request: {e}")
            raise ReimbursementBusinessRuleError(f"Approval failed: {str(e)}")

    async def reject_reimbursement_request(self, request_id: str, reason: str, hostname: str) -> ReimbursementResponseDTO:
        """Reject a reimbursement request"""
        try:
            logger.info(f"Rejecting reimbursement request: {request_id}")
            
            if self.approve_request_use_case:
                return await self.approve_request_use_case.reject(request_id, reason, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_rejected_response(request_id, reason)
                
        except Exception as e:
            logger.error(f"Error rejecting reimbursement request: {e}")
            raise ReimbursementBusinessRuleError(f"Rejection failed: {str(e)}")
    
    # Private helper methods for fallback implementations
    
    def _create_mock_type_response(self, request: ReimbursementTypeCreateRequestDTO) -> ReimbursementTypeResponseDTO:
        """Create a mock reimbursement type response for development/testing"""
        current_time = datetime.now()
        
        return ReimbursementTypeResponseDTO(
            id=f"type_{request.name.lower().replace(' ', '_')}_{current_time.strftime('%Y%m%d')}",
            name=request.name,
            description=request.description or "",
            category=request.category or "general",
            max_amount=request.max_amount or 0.0,
            is_active=True,
            requires_receipt=request.requires_receipt or False,
            created_at=current_time,
            updated_at=current_time
        )
    
    def _create_mock_type_list(self) -> List[ReimbursementTypeResponseDTO]:
        """Create mock reimbursement type list for development/testing"""
        logger.info("Returning empty reimbursement type list")
        return []
    
    def _create_mock_request_response(self, request: ReimbursementRequestCreateDTO) -> ReimbursementResponseDTO:
        """Create a mock reimbursement request response for development/testing"""
        current_time = datetime.now()
        
        return ReimbursementResponseDTO(
            id=f"req_{request.employee_id}_{current_time.strftime('%Y%m%d%H%M%S')}",
            employee_id=request.employee_id,
            reimbursement_type_id=request.reimbursement_type_id,
            amount=request.amount,
            description=request.description or "",
            status="pending",
            submitted_date=current_time,
            receipt_url=None,
            approval_date=None,
            approved_by=None,
            payment_date=None,
            created_at=current_time,
            updated_at=current_time
        )
    
    def _create_mock_request_list(self, filters: ReimbursementSearchFiltersDTO) -> List[ReimbursementResponseDTO]:
        """Create mock reimbursement request list for development/testing"""
        # Return empty list for now - can be enhanced later
        logger.info(f"Returning empty reimbursement request list for filters: {filters}")
        return []
    
    def _create_mock_approved_response(self, request_id: str) -> ReimbursementResponseDTO:
        """Create mock approved reimbursement response for development/testing"""
        current_time = datetime.now()
        
        return ReimbursementResponseDTO(
            id=request_id,
            employee_id="EMP001",
            reimbursement_type_id="TYPE001",
            amount=1000.0,
            description="Mock approved reimbursement",
            status="approved",
            submitted_date=current_time,
            receipt_url=None,
            approval_date=current_time,
            approved_by="ADMIN001",
            payment_date=None,
            created_at=current_time,
            updated_at=current_time
        )
    
    def _create_mock_rejected_response(self, request_id: str, reason: str) -> ReimbursementResponseDTO:
        """Create mock rejected reimbursement response for development/testing"""
        current_time = datetime.now()
        
        return ReimbursementResponseDTO(
            id=request_id,
            employee_id="EMP001",
            reimbursement_type_id="TYPE001",
            amount=1000.0,
            description="Mock rejected reimbursement",
            status="rejected",
            submitted_date=current_time,
            receipt_url=None,
            approval_date=current_time,
            approved_by="ADMIN001",
            payment_date=None,
            created_at=current_time,
            updated_at=current_time
        ) 