"""
Company Leave Use Cases
Business workflows for retrieving company leave policies
"""

import logging
from typing import List, Optional, Dict, Any

from app.application.dto.company_leave_dto import (
    CompanyLeaveResponseDTO,
    CompanyLeaveSummaryDTO,
    CompanyLeaveNotFoundError
)
from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveQueryRepository
)
from app.domain.entities.company_leave import CompanyLeave


class GetCompanyLeaveUseCase:
    """
    Use case for retrieving company leave policies.
    
    Follows SOLID principles:
    - SRP: Only handles company leave retrieval workflow
    - OCP: Can be extended with new retrieval methods
    - LSP: Can be substituted with other use cases
    - ISP: Depends only on required interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(self, query_repository: CompanyLeaveQueryRepository):
        self._query_repository = query_repository
        self._logger = logging.getLogger(__name__)
    
    async def execute_by_id(self, company_leave_id: str) -> Optional[CompanyLeaveResponseDTO]:
        """
        Get company leave by ID.
        
        Args:
            company_leave_id: ID of company leave to retrieve
            
        Returns:
            CompanyLeaveResponseDTO if found, None otherwise
            
        Raises:
            Exception: If retrieval fails
        """
        
        try:
            self._logger.info(f"Getting company leave by ID: {company_leave_id}")
            
            company_leave = await self._query_repository.get_by_id(company_leave_id)
            
            if not company_leave:
                self._logger.warning(f"Company leave not found: {company_leave_id}")
                return None
            
            response = CompanyLeaveResponseDTO.from_entity(company_leave)
            self._logger.debug(f"Successfully retrieved company leave: {company_leave_id}")
            
            return response
            
        except Exception as e:
            self._logger.error(f"Failed to get company leave by ID {company_leave_id}: {str(e)}")
            raise Exception(f"Company leave retrieval failed: {str(e)}")
    
    async def get_all_company_leaves(
        self, 
        include_inactive: bool = False,
        summary_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all company leaves.
        
        Args:
            include_inactive: Whether to include inactive leaves
            summary_only: Whether to return summary data only
            
        Returns:
            List of company leave data
        """
        
        try:
            self._logger.info(f"Retrieving all company leaves (include_inactive={include_inactive})")
            
            company_leaves = await self._query_repository.get_all(include_inactive=include_inactive)
            
            if summary_only:
                return [
                    CompanyLeaveSummaryDTO.from_entity(leave).to_dict()
                    for leave in company_leaves
                ]
            else:
                return [
                    CompanyLeaveResponseDTO.from_entity(leave).to_dict()
                    for leave in company_leaves
                ]
                
        except Exception as e:
            self._logger.error(f"Failed to retrieve company leaves: {str(e)}")
            raise Exception(f"Failed to retrieve company leaves: {str(e)}")
    
    async def get_active_company_leaves(self, summary_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all active company leaves.
        
        Args:
            summary_only: Whether to return summary data only
            
        Returns:
            List of active company leave data
        """
        
        try:
            self._logger.info("Retrieving active company leaves")
            
            company_leaves = await self._query_repository.get_all_active()
            
            if summary_only:
                return [
                    CompanyLeaveSummaryDTO.from_entity(leave).to_dict()
                    for leave in company_leaves
                ]
            else:
                return [
                    CompanyLeaveResponseDTO.from_entity(leave).to_dict()
                    for leave in company_leaves
                ]
                
        except Exception as e:
            self._logger.error(f"Failed to retrieve active company leaves: {str(e)}")
            raise Exception(f"Failed to retrieve active company leaves: {str(e)}")
    
    async def get_company_leave_by_id(self, company_leave_id: str) -> Optional[Dict[str, Any]]:
        """
        Get company leave by ID.
        
        Args:
            company_leave_id: Company leave identifier
            
        Returns:
            Company leave data if found, None otherwise
        """
        
        try:
            self._logger.info(f"Retrieving company leave by ID: {company_leave_id}")
            
            company_leave = await self._query_repository.get_by_id(company_leave_id)
            
            if company_leave:
                return CompanyLeaveResponseDTO.from_entity(company_leave).to_dict()
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve company leave {company_leave_id}: {str(e)}")
            raise Exception(f"Failed to retrieve company leave: {str(e)}")
    
    async def get_company_leave_by_name(self, leave_name: str) -> Optional[Dict[str, Any]]:
        """
        Get company leave by leave name.
        
        Args:
            leave_name: Leave name (e.g., "Casual Leave", "Sick Leave")
            
        Returns:
            Company leave data if found, None otherwise
        """
        
        try:
            self._logger.info(f"Retrieving company leave by name: {leave_name}")
            
            company_leave = await self._query_repository.get_by_leave_name(leave_name)
            
            if company_leave:
                return CompanyLeaveResponseDTO.from_entity(company_leave).to_dict()
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve company leave for name {leave_name}: {str(e)}")
            raise Exception(f"Failed to retrieve company leave: {str(e)}")
    
    async def get_applicable_leaves_for_employee(
        self,
        employee_gender: Optional[str] = None,
        employee_category: Optional[str] = None,
        is_on_probation: bool = False,
        summary_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get company leaves applicable for employee.
        
        Args:
            employee_gender: Employee gender
            employee_category: Employee category
            is_on_probation: Whether employee is on probation
            summary_only: Whether to return summary data only
            
        Returns:
            List of applicable company leave data
        """
        
        try:
            self._logger.info(
                f"Retrieving applicable leaves for employee "
                f"(gender={employee_gender}, category={employee_category}, probation={is_on_probation})"
            )
            
            company_leaves = await self._query_repository.get_applicable_for_employee(
                employee_gender=employee_gender,
                employee_category=employee_category,
                is_on_probation=is_on_probation
            )
            
            if summary_only:
                return [
                    CompanyLeaveSummaryDTO.from_entity(leave).to_dict()
                    for leave in company_leaves
                ]
            else:
                return [
                    CompanyLeaveResponseDTO.from_entity(leave).to_dict()
                    for leave in company_leaves
                ]
                
        except Exception as e:
            self._logger.error(f"Failed to retrieve applicable leaves: {str(e)}")
            raise Exception(f"Failed to retrieve applicable leaves: {str(e)}")
    
    async def get_leave_name_options(self) -> List[Dict[str, Any]]:
        """
        Get leave name options for dropdowns/selection.
        
        Returns:
            List of leave name options
        """
        
        try:
            self._logger.info("Retrieving leave name options")
            
            company_leaves = await self._query_repository.get_all_active()
            
            options = []
            for leave in company_leaves:
                option = {
                    'name': leave.leave_name,
                    'description': leave.description,
                    'category': getattr(leave, 'category', 'general'),
                    'annual_allocation': leave.policy.annual_allocation if hasattr(leave, 'policy') else 0
                }
                options.append(option)
            
            return options
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve leave name options: {str(e)}")
            raise Exception(f"Failed to retrieve leave name options: {str(e)}")
    
    async def get_company_leave_statistics(self) -> Dict[str, Any]:
        """
        Get company leave statistics.
        
        Returns:
            Dictionary containing leave statistics
        """
        
        try:
            self._logger.info("Retrieving company leave statistics")
            
            # Basic statistics
            all_leaves_list = await self._query_repository.get_all(include_inactive=True)
            total_leaves = len(all_leaves_list)
            active_leaves = await self._query_repository.count_active()
            inactive_leaves = total_leaves - active_leaves
            
            # Category breakdown
            active_leaves_list = await self._query_repository.get_all_active()
            category_breakdown = {}
            total_allocation = 0
            
            for leave in active_leaves_list:
                category = getattr(leave, 'category', 'general')
                if category not in category_breakdown:
                    category_breakdown[category] = {
                        'count': 0,
                        'total_allocation': 0,
                        'leave_names': []
                    }
                
                category_breakdown[category]['count'] += 1
                allocation = leave.policy.annual_allocation if hasattr(leave, 'policy') else 0
                category_breakdown[category]['total_allocation'] += allocation
                category_breakdown[category]['leave_names'].append({
                    'name': leave.leave_name,
                    'allocation': allocation
                })
                
                total_allocation += allocation
            
            statistics = {
                'summary': {
                    'total_leave_types': total_leaves,
                    'active_leave_types': active_leaves,
                    'inactive_leave_types': inactive_leaves,
                    'total_annual_allocation': total_allocation
                },
                'category_breakdown': category_breakdown,
                'policy_features': {
                    'encashable_leaves': len([l for l in active_leaves_list if hasattr(l, 'policy') and l.policy.is_encashable]),
                    'auto_approval_leaves': len([l for l in active_leaves_list if hasattr(l, 'policy') and l.policy.auto_approve_threshold]),
                    'medical_cert_required': len([l for l in active_leaves_list if hasattr(l, 'policy') and l.policy.requires_medical_certificate]),
                    'probation_restricted': len([l for l in active_leaves_list if hasattr(l, 'policy') and not l.policy.available_during_probation])
                }
            }
            
            return statistics
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve company leave statistics: {str(e)}")
            raise Exception(f"Failed to retrieve company leave statistics: {str(e)}")
    
    async def search_company_leaves(
        self,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_encashable: Optional[bool] = None,
        requires_approval: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Search company leaves with filters.
        
        Args:
            search_term: Search term for name
            category: Leave category filter
            is_active: Active status filter
            is_encashable: Encashable filter
            requires_approval: Approval requirement filter
            
        Returns:
            List of filtered company leave data
        """
        
        try:
            self._logger.info(f"Searching company leaves with filters")
            
            # Get all leaves (including inactive if not specifically filtered)
            if is_active is None:
                company_leaves = await self._query_repository.get_all(include_inactive=True)
            elif is_active:
                company_leaves = await self._query_repository.get_all_active()
            else:
                all_leaves = await self._query_repository.get_all(include_inactive=True)
                company_leaves = [leave for leave in all_leaves if not leave.is_active]
            
            # Apply filters
            filtered_leaves = []
            
            for leave in company_leaves:
                # Search term filter
                if search_term:
                    search_lower = search_term.lower()
                    if not (search_lower in leave.leave_name.lower()):
                        continue
                
                # Category filter
                if category and getattr(leave, 'category', 'general') != category.lower():
                    continue
                
                # Encashable filter
                if is_encashable is not None and hasattr(leave, 'policy') and leave.policy.is_encashable != is_encashable:
                    continue
                
                # Approval requirement filter
                if requires_approval is not None and hasattr(leave, 'policy') and leave.policy.requires_approval != requires_approval:
                    continue
                
                filtered_leaves.append(leave)
            
            return [
                CompanyLeaveResponseDTO.from_entity(leave).to_dict()
                for leave in filtered_leaves
            ]
            
        except Exception as e:
            self._logger.error(f"Failed to search company leaves: {str(e)}")
            raise Exception(f"Failed to search company leaves: {str(e)}")


class GetCompanyLeaveUseCaseError(Exception):
    """Base exception for get company leave use case"""
    pass


class CompanyLeaveNotFoundError(GetCompanyLeaveUseCaseError):
    """Exception raised when company leave is not found"""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        super().__init__(f"Company leave not found with {identifier_type}: {identifier}")


class InvalidSearchCriteriaError(GetCompanyLeaveUseCaseError):
    """Exception raised when search criteria is invalid"""
    
    def __init__(self, criteria: str, reason: str):
        self.criteria = criteria
        self.reason = reason
        super().__init__(f"Invalid search criteria '{criteria}': {reason}") 