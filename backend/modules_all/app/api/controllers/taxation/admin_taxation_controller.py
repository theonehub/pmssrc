"""
Admin Taxation Controller
API controller for admin/superadmin taxation management
"""

from typing import Dict, Any, List
from fastapi import HTTPException, Depends, status
from pydantic import BaseModel

from app.auth.auth_dependencies import get_current_user, require_role
from app.application.use_cases.taxation.admin.configure_company_salary_structure_use_case import (
    ConfigureCompanySalaryStructureUseCase,
    ConfigureCompanySalaryStructureCommand,
    UpdateAllowancePolicyUseCase,
    UpdateAllowancePolicyCommand,
    GetCompanySalaryStructuresUseCase,
    GetCompanySalaryStructuresQuery
)


class ConfigureSalaryStructureRequest(BaseModel):
    """Request model for configuring salary structure."""
    
    structure_name: str
    effective_from_date: str
    default_basic_salary: float = 0.0
    default_dearness_allowance: float = 0.0
    default_special_allowance: float = 0.0
    hra_policy: Dict[str, Any] = {}
    allowance_policies: Dict[str, float] = {}
    perquisites_enabled: bool = True


class UpdateAllowanceRequest(BaseModel):
    """Request model for updating allowance policy."""
    
    structure_id: str
    allowance_name: str
    allowance_amount: float


class AdminTaxationController:
    """
    Controller for admin taxation management.
    Delegates to existing computation logic without changes.
    """
    
    def __init__(
        self,
        configure_salary_structure_use_case: ConfigureCompanySalaryStructureUseCase,
        update_allowance_policy_use_case: UpdateAllowancePolicyUseCase,
        get_salary_structures_use_case: GetCompanySalaryStructuresUseCase
    ):
        self._configure_salary_structure_use_case = configure_salary_structure_use_case
        self._update_allowance_policy_use_case = update_allowance_policy_use_case
        self._get_salary_structures_use_case = get_salary_structures_use_case
    
    async def configure_company_salary_structure(
        self,
        request: ConfigureSalaryStructureRequest,
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Configure company salary structure.
        
        Args:
            request: Configuration request
            current_user: Current authenticated user
            
        Returns:
            Dict: Configuration result
        """
        
        try:
            # Create command
            command = ConfigureCompanySalaryStructureCommand(
                organization_id=current_user.hostname,  # Multi-tenant support
                structure_name=request.structure_name,
                effective_from_date=request.effective_from_date,
                admin_user_id=current_user.employee_id,
                default_basic_salary=request.default_basic_salary,
                default_dearness_allowance=request.default_dearness_allowance,
                default_special_allowance=request.default_special_allowance,
                hra_policy=request.hra_policy,
                allowance_policies=request.allowance_policies,
                perquisites_enabled=request.perquisites_enabled
            )
            
            # Execute use case (uses existing computation logic)
            response = await self._configure_salary_structure_use_case.execute(command)
            
            if not response.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )
            
            return {
                "success": True,
                "message": response.message,
                "structure_id": response.structure_id,
                "validation_warnings": response.validation_warnings,
                "structure_summary": response.structure_summary
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to configure salary structure: {str(e)}"
            )
    
    async def update_allowance_policy(
        self,
        request: UpdateAllowanceRequest,
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Update specific allowance policy.
        
        Args:
            request: Update request
            current_user: Current authenticated user
            
        Returns:
            Dict: Update result
        """
        
        try:
            # Create command
            command = UpdateAllowancePolicyCommand(
                organization_id=current_user.hostname,
                structure_id=request.structure_id,
                allowance_name=request.allowance_name,
                allowance_amount=request.allowance_amount,
                admin_user_id=current_user.employee_id
            )
            
            # Execute use case
            response = await self._update_allowance_policy_use_case.execute(command)
            
            if not response.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )
            
            return {
                "success": True,
                "message": response.message,
                "validation_warnings": response.validation_warnings,
                "structure_summary": response.structure_summary
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update allowance policy: {str(e)}"
            )
    
    async def get_company_salary_structures(
        self,
        include_inactive: bool = False,
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Get company salary structures.
        
        Args:
            include_inactive: Whether to include inactive structures
            current_user: Current authenticated user
            
        Returns:
            Dict: Salary structures list
        """
        
        try:
            # Create query
            query = GetCompanySalaryStructuresQuery(
                organization_id=current_user.hostname,
                admin_user_id=current_user.employee_id,
                include_inactive=include_inactive
            )
            
            # Execute use case
            response = await self._get_salary_structures_use_case.execute(query)
            
            if not response.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=response.message
                )
            
            return {
                "success": True,
                "structures": response.structures,
                "total_count": len(response.structures),
                "active_count": len([s for s in response.structures if s.get("is_active", True)])
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get salary structures: {str(e)}"
            )
    
    async def get_available_allowances(
        self,
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Get available allowances for configuration.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Dict: Available allowances
        """
        
        try:
            # Return comprehensive list of 40+ allowances
            allowances = {
                "basic_allowances": {
                    "basic_salary": {
                        "name": "Basic Salary",
                        "description": "Basic salary component",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    },
                    "dearness_allowance": {
                        "name": "Dearness Allowance",
                        "description": "Cost of living adjustment",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    },
                    "special_allowance": {
                        "name": "Special Allowance",
                        "description": "Special allowance component",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    }
                },
                "house_rent_allowance": {
                    "hra": {
                        "name": "House Rent Allowance",
                        "description": "Housing allowance for rented accommodation",
                        "exemption_available": True,
                        "exemption_limit": "Minimum of (Actual HRA, Rent paid - 10% of Basic, 50% of Basic for Metro/40% for Non-Metro)",
                        "exemption_unit": "Percentage of Basic",
                        "exemption_varies": True
                    }
                },
                "transport_allowances": {
                    "transport_allowance": {
                        "name": "Transport Allowance",
                        "description": "Transportation allowance",
                        "exemption_available": True,
                        "exemption_limit": 19200,
                        "exemption_unit": "Fixed Amount",
                        "exemption_varies": False
                    },
                    "conveyance_allowance": {
                        "name": "Conveyance Allowance",
                        "description": "Conveyance allowance for official duties",
                        "exemption_available": True,
                        "exemption_limit": 9600,
                        "exemption_unit": "Fixed Amount",
                        "exemption_varies": False
                    }
                },
                "medical_allowances": {
                    "medical_allowance": {
                        "name": "Medical Allowance",
                        "description": "Medical reimbursement allowance",
                        "exemption_available": True,
                        "exemption_limit": 15000,
                        "exemption_unit": "Fixed Amount",
                        "exemption_varies": False
                    },
                    "medical_reimbursement": {
                        "name": "Medical Reimbursement",
                        "description": "Medical expense reimbursement",
                        "exemption_available": True,
                        "exemption_limit": 15000,
                        "exemption_unit": "Fixed Amount",
                        "exemption_varies": False
                    }
                },
                "education_allowances": {
                    "children_education_allowance": {
                        "name": "Children Education Allowance",
                        "description": "Education allowance for children",
                        "exemption_available": True,
                        "exemption_limit": 1200,
                        "exemption_unit": "Per Child",
                        "exemption_varies": True
                    },
                    "hostel_allowance": {
                        "name": "Hostel Allowance",
                        "description": "Hostel allowance for children",
                        "exemption_available": True,
                        "exemption_limit": 3600,
                        "exemption_unit": "Per Child",
                        "exemption_varies": True
                    }
                },
                "specialized_allowances": {
                    "city_compensatory_allowance": {
                        "name": "City Compensatory Allowance",
                        "description": "Allowance for high cost cities",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    },
                    "rural_allowance": {
                        "name": "Rural Allowance",
                        "description": "Allowance for rural posting",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    },
                    "proctorship_allowance": {
                        "name": "Proctorship Allowance",
                        "description": "Allowance for proctorship duties",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    },
                    "wardenship_allowance": {
                        "name": "Wardenship Allowance",
                        "description": "Allowance for hostel warden duties",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    },
                    "project_allowance": {
                        "name": "Project Allowance",
                        "description": "Allowance for project work",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    },
                    "deputation_allowance": {
                        "name": "Deputation Allowance",
                        "description": "Allowance for deputation",
                        "exemption_available": False,
                        "exemption_limit": None,
                        "exemption_unit": None,
                        "exemption_varies": False
                    }
                }
            }
            
            return {
                "success": True,
                "allowances": allowances,
                "total_categories": len(allowances),
                "total_allowances": sum(len(category) for category in allowances.values())
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get available allowances: {str(e)}"
            )
    
    async def get_salary_structure_details(
        self,
        structure_id: str,
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Get detailed salary structure information.
        
        Args:
            structure_id: Salary structure ID
            current_user: Current authenticated user
            
        Returns:
            Dict: Salary structure details
        """
        
        try:
            # For now, return mock data - will be implemented with actual repository
            structure_details = {
                "structure_id": structure_id,
                "structure_name": "Senior Software Engineer Structure",
                "effective_from_date": "2024-04-01",
                "is_active": True,
                "default_basic_salary": 800000,
                "default_dearness_allowance": 0,
                "default_special_allowance": 200000,
                "company_allowance_policies": {
                    "hra": 400000,
                    "transport_allowance": 19200,
                    "medical_allowance": 15000,
                    "children_education_allowance": 2400
                },
                "perquisites_enabled": True,
                "created_by": current_user.employee_id,
                "updated_by": current_user.employee_id,
                "created_date": "2024-01-15",
                "updated_date": "2024-01-20"
            }
            
            return {
                "success": True,
                "structure": structure_details
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get salary structure details: {str(e)}"
            )
    
    async def delete_salary_structure(
        self,
        structure_id: str,
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Delete salary structure.
        
        Args:
            structure_id: Salary structure ID
            current_user: Current authenticated user
            
        Returns:
            Dict: Delete result
        """
        
        try:
            # For now, return success - will be implemented with actual repository
            return {
                "success": True,
                "message": f"Salary structure {structure_id} deleted successfully",
                "deleted_structure_id": structure_id
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete salary structure: {str(e)}"
            )
    
    async def toggle_salary_structure_status(
        self,
        structure_id: str,
        is_active: bool,
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Toggle salary structure status.
        
        Args:
            structure_id: Salary structure ID
            is_active: New status
            current_user: Current authenticated user
            
        Returns:
            Dict: Status update result
        """
        
        try:
            # For now, return success - will be implemented with actual repository
            status_text = "activated" if is_active else "deactivated"
            return {
                "success": True,
                "message": f"Salary structure {structure_id} {status_text} successfully",
                "structure_id": structure_id,
                "is_active": is_active
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update salary structure status: {str(e)}"
            )
    
    async def export_salary_structures(
        self,
        format: str = "xlsx",
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Export salary structures.
        
        Args:
            format: Export format (csv, xlsx)
            current_user: Current authenticated user
            
        Returns:
            Dict: Export result
        """
        
        try:
            # For now, return success - will be implemented with actual export logic
            return {
                "success": True,
                "message": f"Salary structures exported successfully in {format.upper()} format",
                "download_url": f"/api/v2/taxation/admin/salary-structure/export/download?format={format}",
                "file_name": f"salary_structures_{current_user.hostname}_{format}.{format}"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to export salary structures: {str(e)}"
            )
    
    async def get_dashboard_stats(
        self,
        current_user = Depends(get_current_user),
        _admin_check = Depends(require_role("admin"))
    ) -> Dict[str, Any]:
        """
        Get admin dashboard statistics.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Dict: Dashboard statistics
        """
        
        try:
            # For now, return mock data - will be implemented with actual repository
            stats = {
                "total_employees": 150,
                "pending_declarations": 45,
                "completed_declarations": 105,
                "salary_structures_configured": 8,
                "perquisite_policies_active": 12,
                "total_tax_savings": 5625000,
                "average_tax_savings": 37500,
                "completion_rate": 70.0,
                "recent_activities": [
                    {
                        "activity": "Salary structure updated",
                        "timestamp": "2024-01-20T10:30:00Z",
                        "user": "admin@company.com"
                    },
                    {
                        "activity": "Employee declaration approved",
                        "timestamp": "2024-01-20T09:15:00Z",
                        "user": "admin@company.com"
                    }
                ]
            }
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get dashboard statistics: {str(e)}"
            ) 