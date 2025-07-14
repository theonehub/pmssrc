"""
Export Controller Implementation
Handles file export operations and coordinates between services
"""

import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from app.application.interfaces.services.file_generation_service import FileGenerationService
from app.api.controllers.taxation_controller import UnifiedTaxationController
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class ExportController:
    """
    Controller for file export operations.
    
    Coordinates between file generation service and data repositories
    to generate various export formats.
    """
    
    def __init__(
        self,
        file_generation_service: FileGenerationService,
        taxation_controller: UnifiedTaxationController
    ):
        self.file_generation_service = file_generation_service
        self.taxation_controller = taxation_controller

    async def export_processed_salaries(
        self,
        format_type: str,
        filters: Dict[str, Any],
        current_user: CurrentUser
    ) -> Tuple[bytes, str, str]:
        """Export processed salaries in specified format"""
        try:
            logger.info(f"Exporting processed salaries in {format_type} format for organisation {current_user.hostname}")
            
            # Use taxation controller to get salary data with proper DTOs
            if self.taxation_controller:
                response = await self.taxation_controller.get_monthly_salaries_for_period(
                    month=filters.get('month'),
                    year=filters.get('year'),
                    current_user=current_user,  # You may need to ensure current_user is available in this context
                    salary_status=filters.get('status'),
                    department=filters.get('department'),
                    skip=0,
                    limit=1000  # Get all records for export
                )
                salary_data = response.get('items', [])
            
            # Convert to list of dictionaries for file generation
            salary_list = []
            for salary in salary_data:
                if isinstance(salary, dict):
                    # Already a dictionary (from DTO)
                    salary_list.append(salary)
                elif hasattr(salary, 'basic_salary'):
                    # MonthlySalaryResponseDTO object - has flat fields
                    salary_dict = {
                        'employee_id': salary.employee_id,
                        'employee_name': salary.employee_name,
                        'department': salary.department,
                        'designation': salary.designation,
                        'month': salary.month,
                        'year': salary.year,
                        'basic_salary': salary.basic_salary,
                        'hra': salary.hra,
                        'da': salary.da,
                        'other_allowances': salary.other_allowances,
                        'gross_salary': salary.gross_salary,
                        'pf': salary.epf_employee,
                        'pt': salary.professional_tax,
                        'tds': salary.tds,
                        'net_salary': salary.net_salary,
                        'status': salary.status
                    }
                    salary_list.append(salary_dict)
                else:
                    # Entity object (fallback)
                    salary_dict = {
                        'employee_id': str(salary.employee_id),
                        'employee_name': None,
                        'department': None,
                        'designation': None,
                        'month': salary.month,
                        'year': salary.year,
                        'basic_salary': salary.salary.basic_salary.to_float(),
                        'hra': salary.salary.hra_provided.to_float(),
                        'da': salary.salary.dearness_allowance.to_float(),
                        'other_allowances': 0.0,
                        'gross_salary': salary.salary.calculate_gross_salary().to_float(),
                        'pf': 0.0,
                        'pt': 0.0,
                        'tds': salary.tax_amount.to_float(),
                        'net_salary': salary.net_salary.to_float(),
                        'status': 'computed'
                    }
                    salary_list.append(salary_dict)
            
            # Generate file
            file_data = await self.file_generation_service.generate_processed_salaries_export(
                salary_data=salary_list,
                current_user=current_user,
                format_type=format_type,
                filters=filters
            )
            
            # Determine filename and content type
            filename, content_type = self._get_filename_and_content_type(
                format_type, 'processed_salaries', filters.get('month'), filters.get('year')
            )
            
            return file_data, filename, content_type
            
        except Exception as e:
            logger.error(f"Error exporting processed salaries: {e}")
            raise

    async def export_tds_report(
        self,
        format_type: str,
        filters: Dict[str, Any],
        quarter: Optional[int],
        tax_year: int,
        current_user: CurrentUser
    ) -> Tuple[bytes, str, str]:
        """Export TDS report in specified format"""
        try:
            logger.info(f"Exporting TDS report in {format_type} format for organisation {current_user.hostname}")
            
            # Use taxation controller to get salary data with proper DTOs
            if self.taxation_controller:
                response = await self.taxation_controller.get_monthly_salaries_for_period(
                    month=filters.get('month'),
                    year=filters.get('year'),
                    current_user=current_user,  # You may need to ensure current_user is available in this context
                    salary_status=filters.get('status'),
                    department=filters.get('department'),
                    skip=0,
                    limit=1000  # Get all records for export
                )
                salary_data = response.get('items', [])
            
            
            # Filter for TDS data and convert to list of dictionaries
            tds_list = []
            for salary in salary_data:
                if isinstance(salary, dict):
                    # DTO object
                    if salary.get('tds', 0) > 0:
                        tds_list.append(salary)
                elif hasattr(salary, 'basic_salary'):
                    # MonthlySalaryResponseDTO object - has flat fields
                    if salary.tds > 0:
                        tds_dict = {
                            'employee_id': salary.employee_id,
                            'employee_name': salary.employee_name,
                            'department': salary.department,
                            'designation': salary.designation,
                            'month': salary.month,
                            'year': salary.year,
                            'gross_salary': salary.gross_salary,
                            'tds': salary.tds,
                            'tax_regime': salary.tax_regime,
                            'status': salary.status
                        }
                        tds_list.append(tds_dict)
                else:
                    # Entity object (fallback)
                    if salary.tax_amount.to_float() > 0:
                        tds_dict = {
                            'employee_id': str(salary.employee_id),
                            'employee_name': None,
                            'department': None,
                            'designation': None,
                            'month': salary.month,
                            'year': salary.year,
                            'gross_salary': salary.salary.calculate_gross_salary().to_float(),
                            'tds': salary.tax_amount.to_float(),
                            'tax_regime': str(salary.tax_regime),
                            'status': 'computed'
                        }
                        tds_list.append(tds_dict)
            
            # Generate file
            file_data = await self.file_generation_service.generate_tds_report_export(
                tds_data=tds_list,
                current_user=current_user,
                format_type=format_type,
                quarter=quarter,
                tax_year=tax_year,
                filters=filters
            )
            
            # Determine filename and content type
            filename, content_type = self._get_filename_and_content_type(
                format_type, 'tds_report', filters.get('month'), filters.get('year'), quarter
            )
            
            return file_data, filename, content_type
            
        except Exception as e:
            logger.error(f"Error exporting TDS report: {e}")
            raise

    async def export_form_16(
        self,
        employee_id: str,
        tax_year: Optional[str],
        current_user: CurrentUser
    ) -> Tuple[bytes, str, str]:
        """Export Form 16 for specific employee"""
        try:
            logger.info(f"Exporting Form 16 for employee {employee_id} in organisation {current_user.hostname}")
            
            # Fetch TDS data for the employee for the entire tax year
            if not tax_year:
                # Default to current tax year
                current_year = datetime.now().year
                tax_year = f"{current_year}-{current_year + 1}"
            
            # Parse tax year
            start_year = int(tax_year.split('-')[0])
            
            # Fetch salary data for the entire tax year
            tds_list = []
            for month in range(1, 13):
                if self.taxation_controller:
                    response = await self.taxation_controller.get_monthly_salaries_for_period(
                        month=month,
                        year=start_year,
                        current_user=current_user,  # You may need to ensure current_user is available in this context
                        salary_status=None,
                        department=None,
                        skip=0,
                        limit=1000
                    )
                    salary_data = response.get('items', [])
                    # Filter for specific employee
                    salary_data = [s for s in salary_data if s.get('employee_id') == employee_id]
                
                for salary in salary_data:
                    if isinstance(salary, dict):
                        # DTO object
                        if salary.get('tds', 0) > 0:
                            tds_list.append(salary)
                    elif hasattr(salary, 'basic_salary'):
                        # MonthlySalaryResponseDTO object - has flat fields
                        if salary.tds > 0:
                            tds_dict = {
                                'employee_id': salary.employee_id,
                                'employee_name': salary.employee_name,
                                'pan_number': None,  # Would need to fetch from user data
                                'month': salary.month,
                                'year': salary.year,
                                'gross_salary': salary.gross_salary,
                                'tds': salary.tds
                            }
                            tds_list.append(tds_dict)
                    else:
                        # Entity object (fallback)
                        if salary.tax_amount.to_float() > 0:
                            tds_dict = {
                                'employee_id': str(salary.employee_id),
                                'employee_name': None,
                                'pan_number': None,
                                'month': salary.month,
                                'year': salary.year,
                                'gross_salary': salary.salary.calculate_gross_salary().to_float(),
                                'tds': salary.tax_amount.to_float()
                            }
                            tds_list.append(tds_dict)
            
            # Generate file
            file_data = await self.file_generation_service.generate_form_16(
                tds_data=tds_list,
                current_user=current_user,
                employee_id=employee_id,
                tax_year=tax_year
            )
            
            # Determine filename and content type
            filename = f"form_16_{employee_id}_{tax_year}.csv"
            content_type = "text/csv"
            
            return file_data, filename, content_type
            
        except Exception as e:
            logger.error(f"Error exporting Form 16: {e}")
            raise

    async def export_form_24q(
        self,
        quarter: int,
        tax_year: int,
        format_type: str,
        current_user: CurrentUser
    ) -> Tuple[bytes, str, str]:
        """Export Form 24Q for specific quarter and year"""
        try:
            logger.info(f"Exporting Form 24Q for Q{quarter} {tax_year} in {format_type} format")
            
            # Determine months for the quarter
            quarter_months = {
                1: [4, 5, 6],    # Q1: Apr-Jun
                2: [7, 8, 9],    # Q2: Jul-Sep
                3: [10, 11, 12], # Q3: Oct-Dec
                4: [1, 2, 3]     # Q4: Jan-Mar
            }
            
            months = quarter_months.get(quarter, [])
            if not months:
                raise ValueError(f"Invalid quarter: {quarter}")
            
            # Fetch TDS data for all months in the quarter
            tds_list = []
            for month in months:
                if self.taxation_controller:
                    response = await self.taxation_controller.get_monthly_salaries_for_period(
                        month=month,
                        year=tax_year,
                        current_user=current_user,  # You may need to ensure current_user is available in this context
                        salary_status=None,
                        department=None,
                        skip=0,
                        limit=1000
                    )
                    salary_data = response.get('items', [])
                
                for salary in salary_data:
                    if isinstance(salary, dict):
                        # DTO object
                        if salary.get('tds', 0) > 0:
                            tds_list.append(salary)
                    elif hasattr(salary, 'basic_salary'):
                        # MonthlySalaryResponseDTO object - has flat fields
                        if salary.tds > 0:
                            tds_dict = {
                                'employee_id': salary.employee_id,
                                'employee_name': salary.employee_name,
                                'pan_number': None,  # Would need to fetch from user data
                                'month': salary.month,
                                'year': salary.year,
                                'gross_salary': salary.gross_salary,
                                'tds': salary.tds,
                                'department': salary.department,
                                'designation': salary.designation
                            }
                            tds_list.append(tds_dict)
                    else:
                        # Entity object (fallback)
                        if salary.tax_amount.to_float() > 0:
                            tds_dict = {
                                'employee_id': str(salary.employee_id),
                                'employee_name': None,
                                'pan_number': None,
                                'month': salary.month,
                                'year': salary.year,
                                'gross_salary': salary.salary.calculate_gross_salary().to_float(),
                                'tds': salary.tax_amount.to_float(),
                                'department': None,
                                'designation': None
                            }
                            tds_list.append(tds_dict)
            
            # Generate file
            if format_type.lower() == 'csv':
                file_data = await self.file_generation_service.generate_form_24q(
                    tds_data=tds_list,
                    current_user=current_user,
                    quarter=quarter,
                    tax_year=tax_year
                )
                content_type = "text/csv"
            elif format_type.lower() == 'fvu':
                file_data = await self.file_generation_service.generate_fvu_form_24q(
                    tds_data=tds_list,
                    current_user=current_user,
                    quarter=quarter,
                    tax_year=tax_year
                )
                content_type = "text/plain"
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            # Determine filename
            filename = f"form_24q_q{quarter}_{tax_year}_{format_type}.{'txt' if format_type == 'fvu' else 'csv'}"
            
            return file_data, filename, content_type
            
        except Exception as e:
            logger.error(f"Error exporting Form 24Q: {e}")
            raise

    def _get_filename_and_content_type(
        self,
        format_type: str,
        report_type: str,
        month: Optional[int] = None,
        year: Optional[int] = None,
        quarter: Optional[int] = None
    ) -> Tuple[str, str]:
        """Get filename and content type based on format and report type"""
        
        # Determine file extension and content type
        if format_type.lower() == 'csv':
            extension = 'csv'
            content_type = 'text/csv'
        elif format_type.lower() == 'excel':
            extension = 'xlsx'
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif format_type.lower() == 'bank_transfer':
            extension = 'csv'
            content_type = 'text/csv'
        elif format_type.lower() == 'form_16':
            extension = 'csv'
            content_type = 'text/csv'
        elif format_type.lower() == 'form_24q':
            extension = 'csv'
            content_type = 'text/csv'
        elif format_type.lower() == 'fvu':
            extension = 'txt'
            content_type = 'text/plain'
        else:
            extension = 'csv'
            content_type = 'text/csv'
        
        # Build filename
        filename_parts = [report_type]
        
        if month and year:
            filename_parts.append(f"{month:02d}_{year}")
        elif year:
            filename_parts.append(str(year))
        
        if quarter:
            filename_parts.append(f"Q{quarter}")
        
        filename_parts.append(format_type.lower())
        filename_parts.append(extension)
        
        filename = "_".join(filename_parts)
        
        return filename, content_type

    async def export_pf_report(
        self,
        format_type: str,
        filters: Dict[str, Any],
        quarter: Optional[int],
        tax_year: int,
        current_user: CurrentUser
    ) -> Tuple[bytes, str, str]:
        """Export PF report in specified format"""
        try:
            logger.info(f"Exporting PF report in {format_type} format for organisation {current_user.hostname}")
            
            # Use taxation controller to get salary data with proper DTOs
            if self.taxation_controller:
                response = await self.taxation_controller.get_monthly_salaries_for_period(
                    month=filters.get('month'),
                    year=filters.get('year'),
                    current_user=current_user,  # You may need to ensure current_user is available in this context
                    salary_status=filters.get('status'),
                    department=filters.get('department'),
                    skip=0,
                    limit=1000  # Get all records for export
                )
                salary_data = response.get('items', [])
            
            # Filter for PF data and convert to list of dictionaries
            pf_list = []
            for salary in salary_data:
                if isinstance(salary, dict):
                    # DTO object
                    if salary.get('epf_employee', 0) > 0:
                        pf_list.append(salary)
                elif hasattr(salary, 'basic_salary'):
                    # MonthlySalaryResponseDTO object - has flat fields
                    if salary.epf_employee > 0:
                        pf_dict = {
                            'employee_id': salary.employee_id,
                            'employee_name': salary.employee_name,
                            'department': salary.department,
                            'designation': salary.designation,
                            'month': salary.month,
                            'year': salary.year,
                            'gross_salary': salary.gross_salary,
                            'epf_employee': salary.epf_employee,
                            'epf_employer': salary.epf_employee,  # Assuming employer PF equals employee PF
                            'status': salary.status
                        }
                        pf_list.append(pf_dict)
                else:
                    # Entity object (fallback)
                    epf_amount = self._calculate_monthly_epf(salary.salary.calculate_gross_salary())
                    if epf_amount > 0:
                        pf_dict = {
                            'employee_id': str(salary.employee_id),
                            'employee_name': None,
                            'department': None,
                            'designation': None,
                            'month': salary.month,
                            'year': salary.year,
                            'gross_salary': salary.salary.calculate_gross_salary().to_float(),
                            'epf_employee': epf_amount,
                            'epf_employer': epf_amount,  # Assuming employer PF equals employee PF
                            'status': 'computed'
                        }
                        pf_list.append(pf_dict)
            
            # Generate file
            file_data = await self.file_generation_service.generate_pf_report_export(
                pf_data=pf_list,
                current_user=current_user,
                format_type=format_type,
                quarter=quarter,
                tax_year=tax_year,
                filters=filters
            )
            
            # Determine filename and content type
            filename, content_type = self._get_filename_and_content_type(
                format_type, 'pf_report', filters.get('month'), filters.get('year'), quarter
            )
            
            return file_data, filename, content_type
            
        except Exception as e:
            logger.error(f"Error exporting PF report: {e}")
            raise

    def _calculate_monthly_epf(self, gross_salary):
        """Calculate monthly EPF contribution (12% of basic + DA)."""
        from app.domain.value_objects.money import Money
        from decimal import Decimal
        return gross_salary.multiply(Decimal('0.12'))