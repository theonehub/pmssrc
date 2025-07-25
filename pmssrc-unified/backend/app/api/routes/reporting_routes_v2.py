"""
Reporting Routes V2
FastAPI routes for reporting operations following SOLID principles
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, status
from fastapi.responses import JSONResponse

from app.api.controllers.reporting_controller import ReportingController
from app.application.dto.reporting_dto import (
    CreateReportRequestDTO, UpdateReportRequestDTO, ReportSearchFiltersDTO,
    ReportResponseDTO, ReportListResponseDTO, DashboardAnalyticsDTO,
    UserAnalyticsDTO, AttendanceAnalyticsDTO, LeaveAnalyticsDTO,
    PayrollAnalyticsDTO, ReimbursementAnalyticsDTO, ConsolidatedAnalyticsDTO,
    ExportRequestDTO, ExportResponseDTO
)
from app.auth.auth_dependencies import get_current_user, CurrentUser
from app.config.dependency_container import get_reporting_controller

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v2/reporting", tags=["📊 Reporting V2 (SOLID)"])


# Analytics Endpoints (Main Dashboard Endpoint)
@router.get(
    "/dashboard/analytics/statistics",
    response_model=DashboardAnalyticsDTO,
    summary="Get Dashboard Analytics",
    description="Get consolidated dashboard analytics data from all modules",
    responses={
        200: {"description": "Dashboard analytics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_dashboard_analytics(
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> DashboardAnalyticsDTO:
    """
    Get consolidated dashboard analytics.
    
    This endpoint provides the main dashboard data that aggregates information
    from all modules including users, attendance, leaves, reimbursements, etc.
    """
    return await controller.get_dashboard_analytics(current_user)


@router.get(
    "/analytics/consolidated",
    response_model=ConsolidatedAnalyticsDTO,
    summary="Get Consolidated Analytics",
    description="Get comprehensive analytics from all modules",
    responses={
        200: {"description": "Consolidated analytics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_consolidated_analytics(
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> ConsolidatedAnalyticsDTO:
    """
    Get consolidated analytics from all modules.
    
    Provides detailed analytics data from all system modules with optional date filtering.
    """
    return await controller.get_consolidated_analytics(current_user, start_date, end_date)


@router.get(
    "/analytics/users",
    response_model=UserAnalyticsDTO,
    summary="Get User Analytics",
    description="Get user-related analytics data",
    responses={
        200: {"description": "User analytics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_user_analytics(
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> UserAnalyticsDTO:
    """Get user analytics data including distributions and trends."""
    return await controller.get_user_analytics(current_user)


@router.get(
    "/analytics/attendance",
    response_model=AttendanceAnalyticsDTO,
    summary="Get Attendance Analytics",
    description="Get attendance-related analytics data",
    responses={
        200: {"description": "Attendance analytics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_attendance_analytics(
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> AttendanceAnalyticsDTO:
    """Get attendance analytics data with optional date filtering."""
    return await controller.get_attendance_analytics(current_user, start_date, end_date)


@router.get(
    "/analytics/leaves",
    response_model=LeaveAnalyticsDTO,
    summary="Get Leave Analytics",
    description="Get leave-related analytics data",
    responses={
        200: {"description": "Leave analytics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_leave_analytics(
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> LeaveAnalyticsDTO:
    """Get leave analytics data with optional date filtering."""
    return await controller.get_leave_analytics(current_user, start_date, end_date)


@router.get(
    "/analytics/payroll",
    response_model=PayrollAnalyticsDTO,
    summary="Get Payroll Analytics",
    description="Get payroll-related analytics data",
    responses={
        200: {"description": "Payroll analytics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_payroll_analytics(
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> PayrollAnalyticsDTO:
    """Get payroll analytics data with optional date filtering."""
    return await controller.get_payroll_analytics(current_user, start_date, end_date)


@router.get(
    "/analytics/reimbursements",
    response_model=ReimbursementAnalyticsDTO,
    summary="Get Reimbursement Analytics",
    description="Get reimbursement-related analytics data",
    responses={
        200: {"description": "Reimbursement analytics retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_reimbursement_analytics(
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date filter (ISO format)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> ReimbursementAnalyticsDTO:
    """Get reimbursement analytics data with optional date filtering."""
    return await controller.get_reimbursement_analytics(current_user, start_date, end_date)


# Report Management Endpoints
@router.post(
    "/reports",
    response_model=ReportResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Report",
    description="Create a new report",
    responses={
        201: {"description": "Report created successfully"},
        400: {"description": "Validation error"},
        422: {"description": "Business rule error"},
        500: {"description": "Internal server error"}
    }
)
async def create_report(
    request: CreateReportRequestDTO = Body(..., description="Report creation data"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> ReportResponseDTO:
    """Create a new report with specified parameters."""
    return await controller.create_report(request, current_user)


@router.get(
    "/reports/{report_id}",
    response_model=ReportResponseDTO,
    summary="Get Report by ID",
    description="Get a specific report by its ID",
    responses={
        200: {"description": "Report retrieved successfully"},
        404: {"description": "Report not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_report_by_id(
    report_id: str = Path(..., description="Report ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> ReportResponseDTO:
    """Get a specific report by its ID."""
    return await controller.get_report_by_id(report_id, current_user)


@router.get(
    "/reports",
    response_model=ReportListResponseDTO,
    summary="List Reports",
    description="List reports with filtering and pagination",
    responses={
        200: {"description": "Reports listed successfully"},
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=1000, description="Page size"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    start_date: Optional[str] = Query(None, description="Filter by start date"),
    end_date: Optional[str] = Query(None, description="Filter by end date"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> ReportListResponseDTO:
    """List reports with filtering and pagination."""
    filters = ReportSearchFiltersDTO(
        page=page,
        page_size=page_size,
        report_type=report_type,
        status=status,
        created_by=created_by,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return await controller.list_reports(filters, current_user)


@router.put(
    "/reports/{report_id}",
    response_model=ReportResponseDTO,
    summary="Update Report",
    description="Update an existing report",
    responses={
        200: {"description": "Report updated successfully"},
        400: {"description": "Validation error"},
        404: {"description": "Report not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_report(
    report_id: str = Path(..., description="Report ID"),
    request: UpdateReportRequestDTO = Body(..., description="Report update data"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> ReportResponseDTO:
    """Update an existing report."""
    return await controller.update_report(report_id, request, current_user)


@router.delete(
    "/reports/{report_id}",
    summary="Delete Report",
    description="Delete a report",
    responses={
        200: {"description": "Report deleted successfully"},
        404: {"description": "Report not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_report(
    report_id: str = Path(..., description="Report ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> Dict[str, Any]:
    """Delete a report."""
    return await controller.delete_report(report_id, current_user)


# Export Endpoints
@router.post(
    "/export",
    response_model=ExportResponseDTO,
    summary="Export Report",
    description="Export report data to file",
    responses={
        200: {"description": "Report exported successfully"},
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def export_report(
    request: ExportRequestDTO = Body(..., description="Export request data"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> ExportResponseDTO:
    """Export report data to file (PDF, Excel, CSV)."""
    return await controller.export_report(request, current_user)


# Utility Endpoints
@router.post(
    "/cleanup",
    summary="Cleanup Old Reports",
    description="Clean up old completed reports",
    responses={
        200: {"description": "Cleanup completed successfully"},
        500: {"description": "Internal server error"}
    }
)
async def cleanup_old_reports(
    days_old: int = Query(30, ge=1, description="Number of days old"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReportingController = Depends(get_reporting_controller)
) -> Dict[str, Any]:
    """Clean up old completed reports."""
    return await controller.cleanup_old_reports(current_user, days_old)


# Health Check Endpoint
@router.get(
    "/health",
    summary="Reporting Health Check",
    description="Check reporting module health",
    responses={
        200: {"description": "Reporting module is healthy"},
        500: {"description": "Reporting module is unhealthy"}
    }
)
async def health_check() -> Dict[str, Any]:
    """Check reporting module health."""
    return {
        "status": "healthy",
        "module": "reporting",
        "version": "2.0.0",
        "features": [
            "Dashboard Analytics",
            "Consolidated Analytics", 
            "User Analytics",
            "Attendance Analytics",
            "Leave Analytics",
            "Payroll Analytics",
            "Reimbursement Analytics",
            "Report Management",
            "Export Functionality",
            "Cleanup Utilities"
        ]
    } 