"""
Reimbursement Service Interface
Following Interface Segregation Principle for reimbursement business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from app.application.dto.reimbursement_dto import (
    CreateReimbursementTypeRequestDTO,
    CreateReimbursementRequestDTO,
    ApproveReimbursementRequestDTO,
    ReimbursementResponseDTO,
    ReimbursementListResponseDTO,
    ReimbursementSearchFiltersDTO
)


class ReimbursementCommandService(ABC):
    """Service interface for reimbursement command operations."""
    
    @abstractmethod
    async def create_reimbursement_type(self, request: CreateReimbursementTypeRequestDTO) -> ReimbursementResponseDTO:
        """Create a new reimbursement type."""
        pass
    
    @abstractmethod
    async def create_reimbursement_request(self, request: CreateReimbursementRequestDTO) -> ReimbursementResponseDTO:
        """Create a new reimbursement request."""
        pass
    
    @abstractmethod
    async def approve_reimbursement(self, request: ApproveReimbursementRequestDTO) -> ReimbursementResponseDTO:
        """Approve a reimbursement request."""
        pass


class ReimbursementQueryService(ABC):
    """Service interface for reimbursement query operations."""
    
    @abstractmethod
    async def get_reimbursement_by_id(self, reimbursement_id: str) -> Optional[ReimbursementResponseDTO]:
        """Get reimbursement by ID."""
        pass
    
    @abstractmethod
    async def list_reimbursements(self, filters: Optional[ReimbursementSearchFiltersDTO] = None) -> ReimbursementListResponseDTO:
        """List reimbursements with optional filters."""
        pass


class ReimbursementService(
    ReimbursementCommandService,
    ReimbursementQueryService
):
    """Combined reimbursement service interface."""
    pass 