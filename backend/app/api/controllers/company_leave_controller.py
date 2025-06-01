"""
Company Leave API Controller
FastAPI controller for company leave management endpoints
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from fastapi.responses import JSONResponse

from app.application.use_cases.company_leave.create_company_leave_use_case import (
    CreateCompanyLeaveUseCase,
    CreateCompanyLeaveUseCaseError,
    CompanyLeaveAlreadyExistsError
)
from app.application.use_cases.company_leave.get_company_leaves_use_case import (
    GetCompanyLeavesUseCase,
    GetCompanyLeavesUseCaseError,
    CompanyLeaveNotFoundError
)
from app.application.dto.company_leave_dto import (
    CompanyLeaveCreateRequestDTO,
    CompanyLeaveUpdateRequestDTO,
    CompanyLeaveDTOValidationError
)
from app.infrastructure.repositories.mongodb_company_leave_repository import (
    MongoDBCompanyLeaveCommandRepository,
    MongoDBCompanyLeaveQueryRepository,
    MongoDBCompanyLeaveAnalyticsRepository
)
from app.infrastructure.services.mongodb_event_publisher import MongoDBEventPublisher
from app.auth.auth import extract_hostname, role_checker


class CompanyLeaveController:
    """
    Company Leave API Controller following clean architecture principles.
    
    Follows SOLID principles:
    - SRP: Only handles HTTP request/response for company leaves
    - OCP: Can be extended with new endpoints
    - LSP: Can be substituted with other controllers
    - ISP: Provides focused company leave operations
    - DIP: Depends on use case abstractions
    """
    
    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/company-leaves", tags=["Company Leaves"])
        self._logger = logging.getLogger(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all routes for company leave management"""
        
        @self.router.post(
            "/",
            status_code=status.HTTP_201_CREATED,
            response_model=Dict[str, Any],
            summary="Create Company Leave",
            description="Create a new company leave policy"
        )
        async def create_company_leave(
            request_data: Dict[str, Any] = Body(...),
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["superadmin", "admin"]))
        ):
            """Create a new company leave policy"""
            try:
                # Create DTO from request
                create_request = CompanyLeaveCreateRequestDTO.from_dict(request_data)
                
                # Initialize dependencies
                command_repo = MongoDBCompanyLeaveCommandRepository(hostname)
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                event_publisher = MongoDBEventPublisher(hostname)
                
                # Execute use case
                use_case = CreateCompanyLeaveUseCase(
                    command_repository=command_repo,
                    query_repository=query_repo,
                    event_publisher=event_publisher
                )
                
                response = use_case.execute(create_request)
                
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "success": True,
                        "message": "Company leave created successfully",
                        "data": response.to_dict()
                    }
                )
                
            except CompanyLeaveDTOValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Validation failed",
                        "errors": e.errors
                    }
                )
            except CompanyLeaveAlreadyExistsError as e:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Company leave already exists",
                        "message": str(e)
                    }
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Invalid data",
                        "message": str(e)
                    }
                )
            except Exception as e:
                self._logger.error(f"Error creating company leave: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to create company leave"
                    }
                )
        
        @self.router.get(
            "/",
            response_model=Dict[str, Any],
            summary="Get Company Leaves",
            description="Retrieve all company leave policies"
        )
        async def get_company_leaves(
            include_inactive: bool = Query(False, description="Include inactive leaves"),
            summary_only: bool = Query(False, description="Return summary data only"),
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))
        ):
            """Get all company leave policies"""
            try:
                # Initialize dependencies
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                
                # Execute use case
                use_case = GetCompanyLeavesUseCase(query_repository=query_repo)
                leaves = use_case.get_all_company_leaves(
                    include_inactive=include_inactive,
                    summary_only=summary_only
                )
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "data": leaves,
                        "count": len(leaves)
                    }
                )
                
            except Exception as e:
                self._logger.error(f"Error retrieving company leaves: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to retrieve company leaves"
                    }
                )
        
        @self.router.get(
            "/active",
            response_model=Dict[str, Any],
            summary="Get Active Company Leaves",
            description="Retrieve all active company leave policies"
        )
        async def get_active_company_leaves(
            summary_only: bool = Query(False, description="Return summary data only"),
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))
        ):
            """Get all active company leave policies"""
            try:
                # Initialize dependencies
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                
                # Execute use case
                use_case = GetCompanyLeavesUseCase(query_repository=query_repo)
                leaves = use_case.get_active_company_leaves(summary_only=summary_only)
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "data": leaves,
                        "count": len(leaves)
                    }
                )
                
            except Exception as e:
                self._logger.error(f"Error retrieving active company leaves: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to retrieve active company leaves"
                    }
                )
        
        @self.router.get(
            "/{company_leave_id}",
            response_model=Dict[str, Any],
            summary="Get Company Leave by ID",
            description="Retrieve a specific company leave policy by ID"
        )
        async def get_company_leave_by_id(
            company_leave_id: str,
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))
        ):
            """Get company leave policy by ID"""
            try:
                # Initialize dependencies
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                
                # Execute use case
                use_case = GetCompanyLeavesUseCase(query_repository=query_repo)
                leave = use_case.get_company_leave_by_id(company_leave_id)
                
                if not leave:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "error": "Not found",
                            "message": f"Company leave with ID {company_leave_id} not found"
                        }
                    )
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "data": leave
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self._logger.error(f"Error retrieving company leave by ID: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to retrieve company leave"
                    }
                )
        
        @self.router.get(
            "/type/{leave_type_code}",
            response_model=Dict[str, Any],
            summary="Get Company Leave by Type Code",
            description="Retrieve a company leave policy by leave type code"
        )
        async def get_company_leave_by_type_code(
            leave_type_code: str,
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))
        ):
            """Get company leave policy by type code"""
            try:
                # Initialize dependencies
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                
                # Execute use case
                use_case = GetCompanyLeavesUseCase(query_repository=query_repo)
                leave = use_case.get_company_leave_by_type_code(leave_type_code)
                
                if not leave:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail={
                            "error": "Not found",
                            "message": f"Company leave with type code {leave_type_code} not found"
                        }
                    )
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "data": leave
                    }
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self._logger.error(f"Error retrieving company leave by type code: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to retrieve company leave"
                    }
                )
        
        @self.router.get(
            "/applicable/employee",
            response_model=Dict[str, Any],
            summary="Get Applicable Leaves for Employee",
            description="Retrieve company leaves applicable for a specific employee"
        )
        async def get_applicable_leaves_for_employee(
            employee_gender: Optional[str] = Query(None, description="Employee gender"),
            employee_category: Optional[str] = Query(None, description="Employee category"),
            is_on_probation: bool = Query(False, description="Is employee on probation"),
            summary_only: bool = Query(False, description="Return summary data only"),
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))
        ):
            """Get company leaves applicable for employee"""
            try:
                # Initialize dependencies
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                
                # Execute use case
                use_case = GetCompanyLeavesUseCase(query_repository=query_repo)
                leaves = use_case.get_applicable_leaves_for_employee(
                    employee_gender=employee_gender,
                    employee_category=employee_category,
                    is_on_probation=is_on_probation,
                    summary_only=summary_only
                )
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "data": leaves,
                        "count": len(leaves)
                    }
                )
                
            except Exception as e:
                self._logger.error(f"Error retrieving applicable leaves: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to retrieve applicable leaves"
                    }
                )
        
        @self.router.get(
            "/options/leave-types",
            response_model=Dict[str, Any],
            summary="Get Leave Type Options",
            description="Get leave type options for dropdowns/selection"
        )
        async def get_leave_type_options(
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))
        ):
            """Get leave type options"""
            try:
                # Initialize dependencies
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                
                # Execute use case
                use_case = GetCompanyLeavesUseCase(query_repository=query_repo)
                options = use_case.get_leave_type_options()
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "data": options,
                        "count": len(options)
                    }
                )
                
            except Exception as e:
                self._logger.error(f"Error retrieving leave type options: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to retrieve leave type options"
                    }
                )
        
        @self.router.get(
            "/statistics/overview",
            response_model=Dict[str, Any],
            summary="Get Company Leave Statistics",
            description="Get comprehensive statistics about company leave policies"
        )
        async def get_company_leave_statistics(
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["manager", "admin", "superadmin"]))
        ):
            """Get company leave statistics"""
            try:
                # Initialize dependencies
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                
                # Execute use case
                use_case = GetCompanyLeavesUseCase(query_repository=query_repo)
                statistics = use_case.get_company_leave_statistics()
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "data": statistics
                    }
                )
                
            except Exception as e:
                self._logger.error(f"Error retrieving company leave statistics: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to retrieve statistics"
                    }
                )
        
        @self.router.get(
            "/search",
            response_model=Dict[str, Any],
            summary="Search Company Leaves",
            description="Search company leaves with various filters"
        )
        async def search_company_leaves(
            search_term: Optional[str] = Query(None, description="Search term for name/code"),
            category: Optional[str] = Query(None, description="Leave category filter"),
            is_active: Optional[bool] = Query(None, description="Active status filter"),
            is_encashable: Optional[bool] = Query(None, description="Encashable filter"),
            requires_approval: Optional[bool] = Query(None, description="Approval requirement filter"),
            hostname: str = Depends(extract_hostname),
            role: str = Depends(role_checker(["user", "manager", "admin", "superadmin"]))
        ):
            """Search company leaves with filters"""
            try:
                # Initialize dependencies
                query_repo = MongoDBCompanyLeaveQueryRepository(hostname)
                
                # Execute use case
                use_case = GetCompanyLeavesUseCase(query_repository=query_repo)
                leaves = use_case.search_company_leaves(
                    search_term=search_term,
                    category=category,
                    is_active=is_active,
                    is_encashable=is_encashable,
                    requires_approval=requires_approval
                )
                
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "data": leaves,
                        "count": len(leaves)
                    }
                )
                
            except Exception as e:
                self._logger.error(f"Error searching company leaves: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "Internal server error",
                        "message": "Failed to search company leaves"
                    }
                )


# Create controller instance
company_leave_controller = CompanyLeaveController()

# Export router for inclusion in main app
router = company_leave_controller.router 