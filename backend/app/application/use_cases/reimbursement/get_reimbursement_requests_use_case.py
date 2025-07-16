"""
Get Reimbursement Requests Use Case
Business logic for retrieving reimbursement requests
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.application.dto.reimbursement_dto import (
    ReimbursementResponseDTO,
    ReimbursementSummaryDTO,
    ReimbursementStatisticsDTO,
    ReimbursementSearchFiltersDTO,
    create_reimbursement_response_from_entity
)
from app.application.interfaces.repositories.reimbursement_repository import (
    ReimbursementQueryRepository,
    ReimbursementTypeQueryRepository,
    ReimbursementAnalyticsRepository
)
from app.domain.entities.reimbursement import Reimbursement
from app.auth.auth_dependencies import CurrentUser


logger = logging.getLogger(__name__)


class GetReimbursementRequestsUseCaseError(Exception):
    """Exception raised for get reimbursement requests use case errors"""
    pass


class GetReimbursementRequestsUseCase:
    """
    Use case for retrieving reimbursement requests.
    
    Follows SOLID principles:
    - SRP: Only handles reimbursement request retrieval
    - OCP: Extensible through composition
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for retrieval operations
    - DIP: Depends on abstractions (repositories)
    """
    
    def __init__(
        self,
        query_repository: ReimbursementQueryRepository,
        reimbursement_type_repository: ReimbursementTypeQueryRepository,
        analytics_repository: Optional[ReimbursementAnalyticsRepository] = None
    ):
        self.query_repository = query_repository
        self.reimbursement_type_repository = reimbursement_type_repository
        self.analytics_repository = analytics_repository
    
    async def get_all_requests(self, current_user: CurrentUser = None, include_drafts: bool = False) -> List[ReimbursementResponseDTO]:
        """Get all reimbursement requests"""
        
        logger.info(f"Retrieving all reimbursement requests (include_drafts: {include_drafts})")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            requests = await self.query_repository.get_all(current_user)
            
            # Filter out drafts if not requested
            if not include_drafts:
                requests = [req for req in requests if req.status.value != "draft"]
            
            response_dtos = []
            for request in requests:
                reimbursement_type = await self._get_reimbursement_type_by_code(request.reimbursement_type.reimbursement_type_id, current_user)
                if reimbursement_type:
                    response_dto = create_reimbursement_response_from_entity(request, reimbursement_type)
                    response_dtos.append(response_dto)
            
            logger.info(f"Retrieved {len(response_dtos)} reimbursement requests")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving all reimbursement requests: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve requests: {str(e)}")
    
    async def get_request_by_id(self, request_id: str, current_user: CurrentUser = None) -> Optional[ReimbursementResponseDTO]:
        """Get reimbursement request by ID"""
        
        logger.info(f"Retrieving reimbursement request: {request_id}")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            request = await self.query_repository.get_by_id(request_id, current_user)
            if not request:
                logger.warning(f"Reimbursement request not found: {request_id}")
                return None
            
            reimbursement_type = await self._get_reimbursement_type_by_code(request.reimbursement_type.reimbursement_type_id, current_user)
            if not reimbursement_type:
                logger.error(f"Reimbursement type not found: {request.reimbursement_type.reimbursement_type_id}")
                raise GetReimbursementRequestsUseCaseError(f"Reimbursement type not found: {request.reimbursement_type.reimbursement_type_id}")
            
            response_dto = create_reimbursement_response_from_entity(request, reimbursement_type)
            
            logger.info(f"Retrieved reimbursement request: {request_id}")
            return response_dto
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursement request {request_id}: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve request: {str(e)}")
    
    async def get_requests_by_employee(self, employee_id: str, current_user: CurrentUser = None) -> List[ReimbursementResponseDTO]:
        """Get reimbursement requests by employee ID"""
        
        logger.info(f"Retrieving reimbursement requests for employee: {employee_id}")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            requests = await self.query_repository.get_by_employee_id(employee_id, current_user)
            
            response_dtos = []
            for request in requests:
                reimbursement_type = await self._get_reimbursement_type_by_code(request.reimbursement_type.reimbursement_type_id, current_user)
                if reimbursement_type:
                    response_dto = create_reimbursement_response_from_entity(request, reimbursement_type)
                    response_dtos.append(response_dto)
            
            logger.info(f"Retrieved {len(response_dtos)} reimbursement requests for employee: {employee_id}")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving requests for employee {employee_id}: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve employee requests: {str(e)}")
    
    async def get_requests_by_status(self, status: str, current_user: CurrentUser = None) -> List[ReimbursementResponseDTO]:
        """Get reimbursement requests by status"""
        
        logger.info(f"Retrieving reimbursement requests with status: {status}")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            requests = await self.query_repository.get_by_status(status, current_user)
            
            response_dtos = []
            for request in requests:
                reimbursement_type = await self._get_reimbursement_type_by_code(request.reimbursement_type.reimbursement_type_id, current_user)
                if reimbursement_type:
                    response_dto = create_reimbursement_response_from_entity(request, reimbursement_type)
                    response_dtos.append(response_dto)
            
            logger.info(f"Retrieved {len(response_dtos)} reimbursement requests with status: {status}")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving requests by status {status}: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve requests by status: {str(e)}")
    
    async def get_pending_approval_requests(self, current_user: CurrentUser = None) -> List[ReimbursementResponseDTO]:
        """Get reimbursement requests pending approval"""
        
        logger.info("Retrieving reimbursement requests pending approval")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            requests = await self.query_repository.get_pending_approval(current_user)
            
            response_dtos = []
            for request in requests:
                reimbursement_type = await self._get_reimbursement_type_by_code(request.reimbursement_type.reimbursement_type_id, current_user)
                if reimbursement_type:
                    response_dto = create_reimbursement_response_from_entity(request, reimbursement_type)
                    response_dtos.append(response_dto)
            
            logger.info(f"Retrieved {len(response_dtos)} reimbursement requests pending approval")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving pending approval requests: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve pending requests: {str(e)}")
    
    async def search_requests(self, filters: ReimbursementSearchFiltersDTO, current_user: CurrentUser = None) -> List[ReimbursementResponseDTO]:
        """Search reimbursement requests with filters"""
        
        logger.info(f"Searching reimbursement requests with filters")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            requests = await self.query_repository.search(filters, current_user)
            
            response_dtos = []
            for request in requests:
                reimbursement_type = await self._get_reimbursement_type_by_code(request.reimbursement_type.reimbursement_type_id, current_user)
                if reimbursement_type:
                    response_dto = create_reimbursement_response_from_entity(request, reimbursement_type)
                    response_dtos.append(response_dto)
            
            logger.info(f"Found {len(response_dtos)} reimbursement requests matching filters")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error searching reimbursement requests: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to search requests: {str(e)}")
    
    async def get_requests_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        current_user: CurrentUser = None
    ) -> List[ReimbursementResponseDTO]:
        """Get reimbursement requests within date range"""
        
        logger.info(f"Retrieving reimbursement requests from {start_date} to {end_date}")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            requests = await self.query_repository.get_by_date_range(start_date, end_date, current_user)
            
            response_dtos = []
            for request in requests:
                reimbursement_type = await self._get_reimbursement_type_by_code(request.reimbursement_type.reimbursement_type_id, current_user)
                if reimbursement_type:
                    response_dto = create_reimbursement_response_from_entity(request, reimbursement_type)
                    response_dtos.append(response_dto)
            
            logger.info(f"Retrieved {len(response_dtos)} reimbursement requests in date range")
            return response_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving requests by date range: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve requests by date range: {str(e)}")
    
    async def get_employee_requests_summary(self, employee_id: str, current_user: CurrentUser = None) -> List[ReimbursementSummaryDTO]:
        """Get summary of employee's reimbursement requests"""
        
        logger.info(f"Retrieving reimbursement summary for employee: {employee_id}")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            requests = await self.query_repository.get_by_employee_id(employee_id, current_user)
            
            summary_dtos = []
            for request in requests:
                summary_dto = ReimbursementSummaryDTO(
                    request_id=request.reimbursement_id,
                    employee_id=request.employee_id.value,
                    category_name=request.reimbursement_type.category_name,
                    amount=request.amount,
                    status=request.status.value,
                    submitted_at=request.submitted_at,
                    final_amount=request.get_final_amount() if request.is_approved() or request.is_paid() else None
                )
                summary_dtos.append(summary_dto)
            
            logger.info(f"Retrieved summary for {len(summary_dtos)} reimbursement requests")
            return summary_dtos
            
        except Exception as e:
            logger.error(f"Error retrieving employee summary for {employee_id}: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve employee summary: {str(e)}")
    
    async def get_reimbursement_statistics(
        self,
        current_user: CurrentUser = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ReimbursementStatisticsDTO:
        """Get reimbursement statistics"""
        
        if not self.analytics_repository:
            raise GetReimbursementRequestsUseCaseError("Analytics repository not available")
        
        logger.info("Retrieving reimbursement statistics")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            statistics = await self.analytics_repository.get_statistics(current_user, start_date, end_date)
            
            logger.info("Retrieved reimbursement statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error retrieving reimbursement statistics: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve statistics: {str(e)}")
    
    async def get_employee_statistics(
        self,
        employee_id: str,
        current_user: CurrentUser = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get statistics for specific employee"""
        
        if not self.analytics_repository:
            raise GetReimbursementRequestsUseCaseError("Analytics repository not available")
        
        logger.info(f"Retrieving statistics for employee: {employee_id}")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            statistics = await self.analytics_repository.get_employee_statistics(
                employee_id, current_user, start_date, end_date
            )
            
            logger.info(f"Retrieved statistics for employee: {employee_id}")
            return statistics
            
        except Exception as e:
            logger.error(f"Error retrieving employee statistics for {employee_id}: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve employee statistics: {str(e)}")
    
    async def get_category_wise_spending(
        self,
        current_user: CurrentUser = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Get spending breakdown by category"""
        
        if not self.analytics_repository:
            raise GetReimbursementRequestsUseCaseError("Analytics repository not available")
        
        logger.info("Retrieving category-wise spending breakdown")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            spending = await self.analytics_repository.get_category_wise_spending(current_user, start_date, end_date)
            
            # Convert Decimal to float for JSON serialization
            spending_dict = {category: float(amount) for category, amount in spending.items()}
            
            logger.info("Retrieved category-wise spending breakdown")
            return spending_dict
            
        except Exception as e:
            logger.error(f"Error retrieving category-wise spending: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve category spending: {str(e)}")
    
    async def get_monthly_trends(self, current_user: CurrentUser = None, months: int = 12) -> Dict[str, Dict[str, Any]]:
        """Get monthly spending trends"""
        
        if not self.analytics_repository:
            raise GetReimbursementRequestsUseCaseError("Analytics repository not available")
        
        logger.info(f"Retrieving monthly trends for {months} months")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            trends = await self.analytics_repository.get_monthly_trends(current_user, months)
            
            logger.info(f"Retrieved monthly trends for {months} months")
            return trends
            
        except Exception as e:
            logger.error(f"Error retrieving monthly trends: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve monthly trends: {str(e)}")
    
    async def get_top_spenders(
        self,
        current_user: CurrentUser = None,
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top spending employees"""
        
        if not self.analytics_repository:
            raise GetReimbursementRequestsUseCaseError("Analytics repository not available")
        
        logger.info(f"Retrieving top {limit} spenders")
        
        try:
            # organisation_id = current_user.hostname if current_user else None
            spenders = await self.analytics_repository.get_top_spenders(current_user, limit, start_date, end_date)
            
            logger.info(f"Retrieved top {len(spenders)} spenders")
            return spenders
            
        except Exception as e:
            logger.error(f"Error retrieving top spenders: {e}")
            raise GetReimbursementRequestsUseCaseError(f"Failed to retrieve top spenders: {str(e)}")
    
    async def _get_reimbursement_type_by_code(self, code: str, current_user: CurrentUser = None):
        """Helper method to get reimbursement type by code"""
        try:
            return await self.reimbursement_type_repository.get_by_code(code, current_user)
        except Exception as e:
            logger.error(f"Error retrieving reimbursement type by code {code}: {e}")
            return None 