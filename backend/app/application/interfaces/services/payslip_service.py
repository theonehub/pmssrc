"""
Payslip Service Interface
Following Interface Segregation Principle for payslip business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class PayslipService(ABC):
    """Combined payslip service interface."""
    
    @abstractmethod
    async def generate_payslip(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new payslip."""
        pass
    
    @abstractmethod
    async def email_payslip(self, payslip_id: str, email: str) -> bool:
        """Email a payslip to an employee."""
        pass
    
    @abstractmethod
    async def get_payslip_by_id(self, payslip_id: str) -> Optional[Dict[str, Any]]:
        """Get payslip by ID."""
        pass
    
    @abstractmethod
    async def list_payslips(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List payslips with optional filters."""
        pass 