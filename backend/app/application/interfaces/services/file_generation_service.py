"""
File Generation Service Interface
Defines contracts for generating various export file formats
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal


class FileGenerationService(ABC):
    """
    Service interface for generating various export file formats.
    
    Supports:
    - CSV exports (salary, TDS)
    - Excel exports (salary, TDS)
    - Form 16 format
    - Form 24Q format
    - FVU (File Validation Utility) format
    - Bank transfer format
    """
    
    @abstractmethod
    async def generate_salary_csv(
        self,
        salary_data: List[Dict[str, Any]],
        organisation_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate CSV file for salary data"""
        pass
    
    @abstractmethod
    async def generate_salary_excel(
        self,
        salary_data: List[Dict[str, Any]],
        organisation_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate Excel file for salary data"""
        pass
    
    @abstractmethod
    async def generate_salary_bank_transfer(
        self,
        salary_data: List[Dict[str, Any]],
        organisation_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate bank transfer format file for salary data"""
        pass
    
    @abstractmethod
    async def generate_tds_csv(
        self,
        tds_data: List[Dict[str, Any]],
        organisation_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate CSV file for TDS data"""
        pass
    
    @abstractmethod
    async def generate_tds_excel(
        self,
        tds_data: List[Dict[str, Any]],
        organisation_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate Excel file for TDS data"""
        pass
    
    @abstractmethod
    async def generate_form_16(
        self,
        tds_data: List[Dict[str, Any]],
        organisation_id: str,
        employee_id: Optional[str] = None,
        tax_year: Optional[str] = None
    ) -> bytes:
        """Generate Form 16 format file"""
        pass
    
    @abstractmethod
    async def generate_form_24q(
        self,
        tds_data: List[Dict[str, Any]],
        organisation_id: str,
        quarter: int,
        tax_year: int
    ) -> bytes:
        """Generate Form 24Q format file"""
        pass
    
    @abstractmethod
    async def generate_fvu_form_24q(
        self,
        tds_data: List[Dict[str, Any]],
        organisation_id: str,
        quarter: int,
        tax_year: int
    ) -> bytes:
        """Generate FVU (File Validation Utility) format for Form 24Q"""
        pass
    
    @abstractmethod
    async def generate_processed_salaries_export(
        self,
        salary_data: List[Dict[str, Any]],
        organisation_id: str,
        format_type: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate processed salaries export in specified format"""
        pass
    
    @abstractmethod
    async def generate_tds_report_export(
        self,
        tds_data: List[Dict[str, Any]],
        organisation_id: str,
        format_type: str,
        quarter: Optional[int] = None,
        tax_year: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Generate TDS report export in specified format"""
        pass 