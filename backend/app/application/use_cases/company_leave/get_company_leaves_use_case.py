"""
Get Company Leaves Use Case
Business workflow for retrieving company leave policies
"""

import logging
from typing import List, Optional, Dict, Any

from app.application.dto.company_leave_dto import (
    CompanyLeaveResponseDTO,
    CompanyLeaveSummaryDTO,
    LeaveTypeOptionsDTO
)
from app.application.interfaces.repositories.company_leave_repository import (
    CompanyLeaveQueryRepository,
    CompanyLeaveAnalyticsRepository
)
from app.domain.entities.company_leave import CompanyLeave


class GetCompanyLeavesUseCase:
    """
    Use case for retrieving company leave policies.
    
    Follows SOLID principles:
    - SRP: Only handles company leave retrieval operations
    - OCP: Can be extended with new filtering options
    - LSP: Can be substituted with other query use cases
    - ISP: Depends only on required query interfaces
    - DIP: Depends on abstractions, not concrete implementations
    """
    
    def __init__(
        self,
        query_repository: CompanyLeaveQueryRepository,
        analytics_repository: Optional[CompanyLeaveAnalyticsRepository] = None
    ):
        self._query_repository = query_repository
        self._analytics_repository = analytics_repository
        self._logger = logging.getLogger(__name__)
    
    def get_all_company_leaves(
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
            
            company_leaves = self._query_repository.get_all(include_inactive=include_inactive)
            
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
    
    def get_active_company_leaves(self, summary_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all active company leaves.
        
        Args:
            summary_only: Whether to return summary data only
            
        Returns:
            List of active company leave data
        """
        
        try:
            self._logger.info("Retrieving active company leaves")
            
            company_leaves = self._query_repository.get_all_active()
            
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
    
    def get_company_leave_by_id(self, company_leave_id: str) -> Optional[Dict[str, Any]]:
        """
        Get company leave by ID.
        
        Args:
            company_leave_id: Company leave identifier
            
        Returns:
            Company leave data if found, None otherwise
        """
        
        try:
            self._logger.info(f"Retrieving company leave by ID: {company_leave_id}")
            
            company_leave = self._query_repository.get_by_id(company_leave_id)
            
            if company_leave:
                return CompanyLeaveResponseDTO.from_entity(company_leave).to_dict()
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve company leave {company_leave_id}: {str(e)}")
            raise Exception(f"Failed to retrieve company leave: {str(e)}")
    
    def get_company_leave_by_type_code(self, leave_type_code: str) -> Optional[Dict[str, Any]]:
        """
        Get company leave by leave type code.
        
        Args:
            leave_type_code: Leave type code (e.g., "CL", "SL")
            
        Returns:
            Company leave data if found, None otherwise
        """
        
        try:
            self._logger.info(f"Retrieving company leave by type code: {leave_type_code}")
            
            company_leave = self._query_repository.get_by_leave_type_code(leave_type_code)
            
            if company_leave:
                return CompanyLeaveResponseDTO.from_entity(company_leave).to_dict()
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve company leave for type {leave_type_code}: {str(e)}")
            raise Exception(f"Failed to retrieve company leave: {str(e)}")
    
    def get_applicable_leaves_for_employee(
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
            
            company_leaves = self._query_repository.get_applicable_for_employee(
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
    
    def get_leave_type_options(self) -> List[Dict[str, Any]]:
        """
        Get leave type options for dropdowns/selection.
        
        Returns:
            List of leave type options
        """
        
        try:
            self._logger.info("Retrieving leave type options")
            
            company_leaves = self._query_repository.get_all_active()
            
            options = []
            for leave in company_leaves:
                option = LeaveTypeOptionsDTO(
                    code=leave.leave_type.code,
                    name=leave.leave_type.name,
                    category=leave.leave_type.category.value,
                    description=leave.leave_type.description
                )
                options.append(option.to_dict())
            
            return options
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve leave type options: {str(e)}")
            raise Exception(f"Failed to retrieve leave type options: {str(e)}")
    
    def get_company_leave_statistics(self) -> Dict[str, Any]:
        """
        Get company leave statistics.
        
        Returns:
            Dictionary containing leave statistics
        """
        
        try:
            self._logger.info("Retrieving company leave statistics")
            
            # Basic statistics
            total_leaves = len(self._query_repository.get_all(include_inactive=True))
            active_leaves = self._query_repository.count_active()
            inactive_leaves = total_leaves - active_leaves
            
            # Category breakdown
            all_leaves = self._query_repository.get_all_active()
            category_breakdown = {}
            total_allocation = 0
            
            for leave in all_leaves:
                category = leave.leave_type.category.value
                if category not in category_breakdown:
                    category_breakdown[category] = {
                        'count': 0,
                        'total_allocation': 0,
                        'leave_types': []
                    }
                
                category_breakdown[category]['count'] += 1
                category_breakdown[category]['total_allocation'] += leave.policy.annual_allocation
                category_breakdown[category]['leave_types'].append({
                    'code': leave.leave_type.code,
                    'name': leave.leave_type.name,
                    'allocation': leave.policy.annual_allocation
                })
                
                total_allocation += leave.policy.annual_allocation
            
            statistics = {
                'summary': {
                    'total_leave_types': total_leaves,
                    'active_leave_types': active_leaves,
                    'inactive_leave_types': inactive_leaves,
                    'total_annual_allocation': total_allocation
                },
                'category_breakdown': category_breakdown,
                'policy_features': {
                    'encashable_leaves': len([l for l in all_leaves if l.policy.is_encashable]),
                    'auto_approval_leaves': len([l for l in all_leaves if l.policy.auto_approve_threshold]),
                    'medical_cert_required': len([l for l in all_leaves if l.policy.requires_medical_certificate]),
                    'probation_restricted': len([l for l in all_leaves if not l.policy.available_during_probation])
                }
            }
            
            return statistics
            
        except Exception as e:
            self._logger.error(f"Failed to retrieve company leave statistics: {str(e)}")
            raise Exception(f"Failed to retrieve company leave statistics: {str(e)}")
    
    def search_company_leaves(
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
            search_term: Search term for name/code
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
                company_leaves = self._query_repository.get_all(include_inactive=True)
            elif is_active:
                company_leaves = self._query_repository.get_all_active()
            else:
                all_leaves = self._query_repository.get_all(include_inactive=True)
                company_leaves = [leave for leave in all_leaves if not leave.is_active]
            
            # Apply filters
            filtered_leaves = []
            
            for leave in company_leaves:
                # Search term filter
                if search_term:
                    search_lower = search_term.lower()
                    if not (search_lower in leave.leave_type.name.lower() or 
                           search_lower in leave.leave_type.code.lower()):
                        continue
                
                # Category filter
                if category and leave.leave_type.category.value != category.lower():
                    continue
                
                # Encashable filter
                if is_encashable is not None and leave.policy.is_encashable != is_encashable:
                    continue
                
                # Approval requirement filter
                if requires_approval is not None and leave.policy.requires_approval != requires_approval:
                    continue
                
                filtered_leaves.append(leave)
            
            return [
                CompanyLeaveResponseDTO.from_entity(leave).to_dict()
                for leave in filtered_leaves
            ]
            
        except Exception as e:
            self._logger.error(f"Failed to search company leaves: {str(e)}")
            raise Exception(f"Failed to search company leaves: {str(e)}")


class GetCompanyLeavesUseCaseError(Exception):
    """Base exception for get company leaves use case"""
    pass


class CompanyLeaveNotFoundError(GetCompanyLeavesUseCaseError):
    """Exception raised when company leave is not found"""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        super().__init__(f"Company leave not found with {identifier_type}: {identifier}")


class InvalidSearchCriteriaError(GetCompanyLeavesUseCaseError):
    """Exception raised when search criteria is invalid"""
    
    def __init__(self, criteria: str, reason: str):
        self.criteria = criteria
        self.reason = reason
        super().__init__(f"Invalid search criteria '{criteria}': {reason}") 