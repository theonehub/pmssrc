"""
Admin Taxation Routes V2
API routes for admin/superadmin taxation management (segregated)
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, Query

from app.api.controllers.taxation.admin_taxation_controller import (
    AdminTaxationController, ConfigureSalaryStructureRequest, UpdateAllowanceRequest
)
from app.config.dependency_container import get_admin_taxation_controller


# Create router for admin taxation endpoints
admin_taxation_router = APIRouter(
    prefix="/api/v2/taxation/admin",
    tags=["Admin Taxation Management"],
    dependencies=[]
)


@admin_taxation_router.post("/salary-structure/configure")
async def configure_company_salary_structure(
    request: ConfigureSalaryStructureRequest,
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Configure company salary structure and policies.
    
    **Admin/Superadmin Only**
    
    This endpoint allows admins to configure:
    - Default salary components
    - HRA policies
    - Company allowance policies (40+ allowances)
    - Perquisites enablement
    
    Uses existing salary computation logic without changes.
    """
    return await controller.configure_company_salary_structure(request)


@admin_taxation_router.put("/salary-structure/allowance")
async def update_allowance_policy(
    request: UpdateAllowanceRequest,
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Update specific allowance policy.
    
    **Admin/Superadmin Only**
    
    Allows updating individual allowance amounts in company policy.
    """
    return await controller.update_allowance_policy(request)


@admin_taxation_router.get("/salary-structure/list")
async def get_company_salary_structures(
    include_inactive: bool = Query(False, description="Include inactive structures"),
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Get company salary structures.
    
    **Admin/Superadmin Only**
    
    Returns list of configured salary structures for the organization.
    """
    return await controller.get_company_salary_structures(include_inactive)


@admin_taxation_router.get("/allowances/available")
async def get_available_allowances(
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Get available allowances for configuration.
    
    **Admin/Superadmin Only**
    
    Returns comprehensive list of 40+ allowances that can be configured,
    including exemption rules and limits.
    """
    return await controller.get_available_allowances()


@admin_taxation_router.get("/salary-structure/{structure_id}")
async def get_salary_structure_details(
    structure_id: str,
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Get detailed salary structure information.
    
    **Admin/Superadmin Only**
    
    Returns complete details of a specific salary structure.
    """
    return await controller.get_salary_structure_details(structure_id)


@admin_taxation_router.delete("/salary-structure/{structure_id}")
async def delete_salary_structure(
    structure_id: str,
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Delete salary structure.
    
    **Admin/Superadmin Only**
    
    Permanently delete a salary structure (soft delete recommended).
    """
    return await controller.delete_salary_structure(structure_id)


@admin_taxation_router.patch("/salary-structure/{structure_id}/status")
async def toggle_salary_structure_status(
    structure_id: str,
    is_active: bool = Query(..., description="Set structure active/inactive"),
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Toggle salary structure status.
    
    **Admin/Superadmin Only**
    
    Activate or deactivate a salary structure.
    """
    return await controller.toggle_salary_structure_status(structure_id, is_active)


@admin_taxation_router.get("/salary-structure/export")
async def export_salary_structures(
    format: str = Query("xlsx", description="Export format: csv, xlsx"),
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Export salary structures.
    
    **Admin/Superadmin Only**
    
    Export all salary structures in specified format.
    """
    return await controller.export_salary_structures(format)


@admin_taxation_router.get("/dashboard/stats")
async def get_dashboard_stats(
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Get admin dashboard statistics.
    
    **Admin/Superadmin Only**
    
    Returns key metrics for admin dashboard.
    """
    return await controller.get_dashboard_stats()


# Additional admin endpoints for perquisites, employee management, etc.
@admin_taxation_router.post("/perquisites-policy/configure")
async def configure_perquisites_policy(
    # Will be implemented in next iteration
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Configure company perquisites policy.
    
    **Admin/Superadmin Only**
    
    Configure perquisites policies for:
    - Accommodation
    - Car
    - Medical reimbursement
    - LTA
    - And other perquisites
    """
    return {"message": "Perquisites policy configuration - Coming in next iteration"}


@admin_taxation_router.get("/employees/tax-overview")
async def get_employees_tax_overview(
    tax_year: str = Query(..., description="Tax year (e.g., 2023-24)"),
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Get tax overview for all employees.
    
    **Admin/Superadmin Only**
    
    Provides summary of employee tax declarations and calculations.
    """
    return {"message": "Employee tax overview - Coming in next iteration"}


@admin_taxation_router.post("/employees/{employee_id}/approve-declaration")
async def approve_employee_declaration(
    employee_id: str,
    tax_year: str = Query(..., description="Tax year"),
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Approve employee tax declaration.
    
    **Admin/Superadmin Only**
    
    Approve employee's investment and income declarations.
    """
    return {"message": "Declaration approval - Coming in next iteration"}


@admin_taxation_router.post("/bulk-employee-setup")
async def bulk_employee_setup(
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Bulk employee salary structure assignment.
    
    **Admin/Superadmin Only**
    
    Assign salary structures to multiple employees at once.
    """
    return {"message": "Bulk employee setup - Coming in next iteration"}


@admin_taxation_router.get("/reports/tax-summary")
async def generate_tax_summary_report(
    tax_year: str = Query(..., description="Tax year"),
    format: str = Query("json", description="Report format: json, csv, xlsx"),
    controller: AdminTaxationController = Depends(get_admin_taxation_controller)
) -> Dict[str, Any]:
    """
    Generate tax summary report.
    
    **Admin/Superadmin Only**
    
    Generate comprehensive tax reports for the organization.
    """
    return {"message": "Tax summary reports - Coming in next iteration"} 