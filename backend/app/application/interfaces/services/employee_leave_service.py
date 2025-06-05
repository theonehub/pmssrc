"""
Employee Leave Service Interface
Following Interface Segregation Principle for employee leave business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class EmployeeLeaveService(ABC):
    """Combined employee leave service interface."""
    
    @abstractmethod
    async def apply_leave(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Apply for employee leave."""
        pass
    
    @abstractmethod
    async def approve_leave(self, leave_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Approve employee leave."""
        pass
    
    @abstractmethod
    async def get_leave_by_id(self, leave_id: str) -> Optional[Dict[str, Any]]:
        """Get employee leave by ID."""
        pass
    
    @abstractmethod
    async def list_leaves(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List employee leaves with optional filters."""
        pass 