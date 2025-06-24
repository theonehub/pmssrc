"""
Employee Taxation Controller
API controller for employee self-declaration and tax management
"""

from typing import Dict, Any, List, Optional
from fastapi import HTTPException, Depends, status
from pydantic import BaseModel

from app.auth.auth_dependencies import get_current_user, require_role
from app.application.use_cases.taxation.employee.declare_personal_investments_use_case import (
    DeclarePersonalInvestmentsUseCase,
    DeclarePersonalInvestmentsCommand,
    UpdateSpecificInvestmentUseCase,
    UpdateInvestmentCommand,
    SubmitInvestmentDeclarationUseCase,
    SubmitDeclarationCommand,
    GetPersonalInvestmentDeclarationUseCase,
    GetInvestmentDeclarationQuery,
    GetInvestmentOptionsUseCase,
    GetInvestmentOptionsQuery
)
# Import existing comprehensive tax calculation use case (no changes)
from app.application.use_cases.taxation.get_comprehensive_taxation_record_use_case import (
    GetComprehensiveTaxationRecordUseCase
)


class DeclareInvestmentsRequest(BaseModel):
    """Request model for declaring personal investments."""
    
    tax_year: str
    section_80c_investments: Dict[str, float] = {}
    section_80d_premiums: Dict[str, float] = {}
    section_80ccd_nps: float = 0.0
    section_80e_education_loan: float = 0.0
    section_80g_donations: Dict[str, float] = {}
    section_80tta_interest: float = 0.0
    section_80ttb_interest: float = 0.0
    section_80u_disability: float = 0.0
    other_deductions: Dict[str, float] = {}


class UpdateInvestmentRequest(BaseModel):
    """Request model for updating specific investment."""
    
    tax_year: str
    section: str
    investment_name: str
    amount: float


class EmployeeTaxationController:
    """
    Controller for employee taxation self-declaration.
    Delegates to existing computation logic without changes.
    """
    
    def __init__(
        self,
        declare_investments_use_case: DeclarePersonalInvestmentsUseCase,
        update_investment_use_case: UpdateSpecificInvestmentUseCase,
        submit_declaration_use_case: SubmitInvestmentDeclarationUseCase,
        get_declaration_use_case: GetPersonalInvestmentDeclarationUseCase,
        get_investment_options_use_case: GetInvestmentOptionsUseCase,
        get_comprehensive_tax_use_case: GetComprehensiveTaxationRecordUseCase
    ):
        self._declare_investments_use_case = declare_investments_use_case
        self._update_investment_use_case = update_investment_use_case
        self._submit_declaration_use_case = submit_declaration_use_case
        self._get_declaration_use_case = get_declaration_use_case
        self._get_investment_options_use_case = get_investment_options_use_case
        self._get_comprehensive_tax_use_case = get_comprehensive_tax_use_case
    
    async def declare_personal_investments(
        self,
        request: DeclareInvestmentsRequest,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Declare personal investments and deductions.
        
        Args:
            request: Investment declaration request
            current_user: Current authenticated user
            
        Returns:
            Dict: Declaration result
        """
        
        try:
            # Create command
            command = DeclarePersonalInvestmentsCommand(
                employee_id=current_user.employee_id,
                organization_id=current_user.hostname,
                tax_year=request.tax_year,
                section_80c_investments=request.section_80c_investments,
                section_80d_premiums=request.section_80d_premiums,
                section_80ccd_nps=request.section_80ccd_nps,
                section_80e_education_loan=request.section_80e_education_loan,
                section_80g_donations=request.section_80g_donations,
                section_80tta_interest=request.section_80tta_interest,
                section_80ttb_interest=request.section_80ttb_interest,
                section_80u_disability=request.section_80u_disability,
                other_deductions=request.other_deductions
            )
            
            # Execute use case (uses existing TaxDeductions computation logic)
            response = await self._declare_investments_use_case.execute(command)
            
            if not response.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )
            
            return {
                "success": True,
                "message": response.message,
                "declaration_id": response.declaration_id,
                "total_deductions": response.total_deductions,
                "validation_warnings": response.validation_warnings,
                "tax_savings": response.tax_savings
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to declare investments: {str(e)}"
            )
    
    async def update_specific_investment(
        self,
        request: UpdateInvestmentRequest,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Update specific investment amount.
        
        Args:
            request: Update request
            current_user: Current authenticated user
            
        Returns:
            Dict: Update result
        """
        
        try:
            # Create command
            command = UpdateInvestmentCommand(
                employee_id=current_user.employee_id,
                organization_id=current_user.hostname,
                tax_year=request.tax_year,
                investment_type=request.investment_name,
                investment_section=request.section,
                amount=request.amount
            )
            
            # Execute use case
            response = await self._update_investment_use_case.execute(command)
            
            if not response.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )
            
            return {
                "success": True,
                "message": response.message,
                "updated_investment": response.updated_investment,
                "total_deductions": response.total_deductions,
                "tax_savings": response.tax_savings
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update investment: {str(e)}"
            )
    
    async def submit_investment_declaration(
        self,
        tax_year: str,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Submit investment declaration for approval.
        
        Args:
            tax_year: Tax year
            current_user: Current authenticated user
            
        Returns:
            Dict: Submission result
        """
        
        try:
            # Create command
            command = SubmitDeclarationCommand(
                employee_id=current_user.employee_id,
                organization_id=current_user.hostname,
                tax_year=tax_year
            )
            
            # Execute use case
            response = await self._submit_declaration_use_case.execute(command)
            
            if not response.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )
            
            return {
                "success": True,
                "message": response.message,
                "submission_id": response.submission_id,
                "submission_date": response.submission_date,
                "approval_status": response.approval_status
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to submit declaration: {str(e)}"
            )
    
    async def get_personal_investment_declaration(
        self,
        tax_year: str,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Get personal investment declaration.
        
        Args:
            tax_year: Tax year
            current_user: Current authenticated user
            
        Returns:
            Dict: Investment declaration
        """
        
        try:
            # Create query
            query = GetInvestmentDeclarationQuery(
                employee_id=current_user.employee_id,
                organization_id=current_user.hostname,
                tax_year=tax_year
            )
            
            # Execute use case
            response = await self._get_declaration_use_case.execute(query)
            
            if not response.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )
            
            return {
                "success": True,
                "declaration": response.declaration,
                "total_deductions": response.total_deductions,
                "tax_savings": response.tax_savings,
                "approval_status": response.approval_status
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get declaration: {str(e)}"
            )
    
    async def get_investment_options(
        self,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Get available investment options.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Dict: Investment options
        """
        
        try:
            # Create query
            query = GetInvestmentOptionsQuery(
                organization_id=current_user.hostname
            )
            
            # Execute use case
            response = await self._get_investment_options_use_case.execute(query)
            
            if not response.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )
            
            return {
                "success": True,
                "message": response.message,
                "investment_options": response.investment_summary.get("investment_options", {})
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get investment options: {str(e)}"
            )
    
    async def calculate_comprehensive_tax(
        self,
        tax_year: str,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive tax.
        
        Args:
            tax_year: Tax year
            current_user: Current authenticated user
            
        Returns:
            Dict: Tax calculation result
        """
        
        try:
            # Execute use case (uses existing comprehensive tax calculation logic)
            comprehensive_tax_dto = await self._get_comprehensive_tax_use_case.execute(
                employee_id=current_user.employee_id,
                organization_id=current_user.hostname,
                tax_year=tax_year
            )
            
            return {
                "success": True,
                "message": "Comprehensive tax calculation completed successfully",
                "tax_data": comprehensive_tax_dto.dict()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to calculate tax: {str(e)}"
            )
    
    async def get_tax_saving_recommendations(
        self,
        tax_year: str,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Get tax saving recommendations.
        
        Args:
            tax_year: Tax year
            current_user: Current authenticated user
            
        Returns:
            Dict: Tax saving recommendations
        """
        
        try:
            # For now, return mock recommendations - will be implemented with actual logic
            recommendations = {
                "current_declarations": {
                    "section_80c": 120000,
                    "section_80d": 15000,
                    "section_80ccd": 50000,
                    "total_declared": 185000
                },
                "potential_savings": {
                    "section_80c_remaining": 150000,
                    "section_80d_remaining": 15000,
                    "section_80ccd_remaining": 50000,
                    "total_potential": 215000
                },
                "recommendations": [
                    {
                        "section": "80C",
                        "investment_type": "ELSS Mutual Funds",
                        "amount": 150000,
                        "tax_saving": 45000,
                        "priority": "High",
                        "deadline": "March 31, 2024"
                    },
                    {
                        "section": "80D",
                        "investment_type": "Health Insurance Premium",
                        "amount": 15000,
                        "tax_saving": 4500,
                        "priority": "Medium",
                        "deadline": "March 31, 2024"
                    },
                    {
                        "section": "80CCD",
                        "investment_type": "NPS Contribution",
                        "amount": 50000,
                        "tax_saving": 15000,
                        "priority": "Medium",
                        "deadline": "March 31, 2024"
                    }
                ],
                "total_tax_saving": 64500
            }
            
            return {
                "success": True,
                "recommendations": recommendations
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get tax saving recommendations: {str(e)}"
            )
    
    async def export_tax_declaration(
        self,
        tax_year: str,
        format: str = "pdf",
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Export tax declaration.
        
        Args:
            tax_year: Tax year
            format: Export format (pdf, xlsx)
            current_user: Current authenticated user
            
        Returns:
            Dict: Export result
        """
        
        try:
            # For now, return success - will be implemented with actual export logic
            return {
                "success": True,
                "message": f"Tax declaration exported successfully in {format.upper()} format",
                "download_url": f"/api/v2/taxation/employee/declaration/export/download?tax_year={tax_year}&format={format}",
                "file_name": f"tax_declaration_{current_user.employee_id}_{tax_year}.{format}"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to export tax declaration: {str(e)}"
            )
    
    async def delete_document(
        self,
        document_id: str,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Delete uploaded document.
        
        Args:
            document_id: Document ID
            current_user: Current authenticated user
            
        Returns:
            Dict: Delete result
        """
        
        try:
            # For now, return success - will be implemented with actual document management
            return {
                "success": True,
                "message": f"Document {document_id} deleted successfully",
                "deleted_document_id": document_id
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete document: {str(e)}"
            )
    
    async def download_document(
        self,
        document_id: str,
        current_user = Depends(get_current_user),
        _employee_check = Depends(require_role("employee"))
    ) -> Dict[str, Any]:
        """
        Download uploaded document.
        
        Args:
            document_id: Document ID
            current_user: Current authenticated user
            
        Returns:
            Dict: Download result
        """
        
        try:
            # For now, return success - will be implemented with actual document management
            return {
                "success": True,
                "message": f"Document {document_id} download initiated",
                "download_url": f"/api/v2/taxation/employee/documents/{document_id}/file",
                "file_name": f"document_{document_id}.pdf"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download document: {str(e)}"
            ) 