"""
Employee Taxation Routes V2
API routes for employee self-declaration and tax management (segregated)
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, Query

from app.api.controllers.taxation.employee_taxation_controller import (
    EmployeeTaxationController, DeclareInvestmentsRequest, UpdateInvestmentRequest
)
from app.config.dependency_container import get_employee_taxation_controller


# Create router for employee taxation endpoints
employee_taxation_router = APIRouter(
    prefix="/api/v2/taxation/employee",
    tags=["Employee Taxation Self-Declaration"],
    dependencies=[]
)


@employee_taxation_router.post("/investments/declare")
async def declare_personal_investments(
    request: DeclareInvestmentsRequest,
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Declare personal investments and deductions.
    
    **Employee Access**
    
    Allows employees to declare:
    - Section 80C investments (LIC, PPF, ELSS, etc.)
    - Health insurance premiums (80D)
    - NPS contributions (80CCD)
    - Education loan interest (80E)
    - Charitable donations (80G)
    - Other deductions
    
    Uses existing TaxDeductions computation logic without changes.
    """
    return await controller.declare_personal_investments(request)


@employee_taxation_router.put("/investments/update")
async def update_specific_investment(
    request: UpdateInvestmentRequest,
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Update specific investment amount.
    
    **Employee Access**
    
    Allows updating individual investment amounts within sections.
    """
    return await controller.update_specific_investment(request)


@employee_taxation_router.post("/investments/submit")
async def submit_investment_declaration(
    tax_year: str = Query(..., description="Tax year (e.g., 2023-24)"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Submit investment declaration for approval.
    
    **Employee Access**
    
    Submit completed declaration to admin for approval.
    """
    return await controller.submit_investment_declaration(tax_year)


@employee_taxation_router.get("/investments/declaration")
async def get_personal_investment_declaration(
    tax_year: str = Query(..., description="Tax year (e.g., 2023-24)"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Get personal investment declaration.
    
    **Employee Access**
    
    Retrieve current investment declaration for the tax year.
    """
    return await controller.get_personal_investment_declaration(tax_year)


@employee_taxation_router.get("/investments/options")
async def get_investment_options(
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Get available investment options.
    
    **Employee Access**
    
    Returns comprehensive list of investment options with limits and descriptions.
    """
    return await controller.get_investment_options()


@employee_taxation_router.post("/tax/calculate")
async def calculate_comprehensive_tax(
    tax_year: str = Query(..., description="Tax year (e.g., 2023-24)"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Calculate comprehensive tax.
    
    **Employee Access**
    
    Combines company salary data with employee declarations to calculate tax.
    Uses existing comprehensive tax calculation logic without changes.
    """
    return await controller.calculate_comprehensive_tax(tax_year)


@employee_taxation_router.get("/tax/recommendations")
async def get_tax_saving_recommendations(
    tax_year: str = Query(..., description="Tax year"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Get tax saving recommendations.
    
    **Employee Access**
    
    Provides personalized recommendations for tax savings based on current declarations.
    """
    return await controller.get_tax_saving_recommendations(tax_year)


@employee_taxation_router.get("/declaration/export")
async def export_tax_declaration(
    tax_year: str = Query(..., description="Tax year"),
    format: str = Query("pdf", description="Export format: pdf, xlsx"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Export tax declaration.
    
    **Employee Access**
    
    Export personal tax declaration in specified format.
    """
    return await controller.export_tax_declaration(tax_year, format)


@employee_taxation_router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Delete uploaded document.
    
    **Employee Access**
    
    Delete a previously uploaded proof document.
    """
    return await controller.delete_document(document_id)


@employee_taxation_router.get("/documents/{document_id}/download")
async def download_document(
    document_id: str,
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Download uploaded document.
    
    **Employee Access**
    
    Download a previously uploaded proof document.
    """
    return await controller.download_document(document_id)


# Additional employee endpoints for income declaration, document upload, etc.
@employee_taxation_router.post("/income/declare")
async def declare_personal_income(
    # Will be implemented in next iteration using PersonalIncomeDeclaration
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Declare personal income from other sources.
    
    **Employee Access**
    
    Declare income from:
    - House property
    - Capital gains
    - Interest income
    - Dividend income
    - Business/professional income
    - Other sources
    """
    return {"message": "Personal income declaration - Coming in next iteration"}


@employee_taxation_router.get("/income/declaration")
async def get_personal_income_declaration(
    tax_year: str = Query(..., description="Tax year"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Get personal income declaration.
    
    **Employee Access**
    
    Retrieve declared income from other sources.
    """
    return {"message": "Get income declaration - Coming in next iteration"}


@employee_taxation_router.post("/documents/upload")
async def upload_proof_documents(
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Upload proof documents.
    
    **Employee Access**
    
    Upload supporting documents for investments and income declarations.
    """
    return {"message": "Document upload - Coming in next iteration"}


@employee_taxation_router.get("/documents/list")
async def get_uploaded_documents(
    tax_year: str = Query(..., description="Tax year"),
    section: str = Query(None, description="Specific section (80c, 80d, etc.)"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Get uploaded documents.
    
    **Employee Access**
    
    List all uploaded proof documents.
    """
    return {"message": "Document listing - Coming in next iteration"}


@employee_taxation_router.get("/tax/projections")
async def get_tax_projections(
    tax_year: str = Query(..., description="Tax year"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Get monthly tax projections.
    
    **Employee Access**
    
    Get monthly TDS and tax liability projections for remaining months.
    """
    return {"message": "Tax projections - Coming in next iteration"}


@employee_taxation_router.get("/tax/regime-comparison")
async def compare_tax_regimes(
    tax_year: str = Query(..., description="Tax year"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Compare old vs new tax regimes.
    
    **Employee Access**
    
    Detailed comparison of tax liability under old and new regimes.
    """
    return {"message": "Tax regime comparison - Coming in next iteration"}


@employee_taxation_router.get("/dashboard/summary")
async def get_tax_dashboard_summary(
    tax_year: str = Query(..., description="Tax year"),
    controller: EmployeeTaxationController = Depends(get_employee_taxation_controller)
) -> Dict[str, Any]:
    """
    Get tax dashboard summary.
    
    **Employee Access**
    
    Get summary of tax declarations, calculations, and status.
    """
    return {"message": "Tax dashboard summary - Coming in next iteration"} 