"""
Employee Leave Service Interface
Following Interface Segregation Principle for employee leave business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.auth.auth_dependencies import CurrentUser


class EmployeeLeaveService(ABC):
    """Combined employee leave service interface."""
    
    @abstractmethod
    async def apply_leave(self, request: Dict[str, Any], current_user: CurrentUser) -> Dict[str, Any]:
        """Apply for employee leave. Organization context is derived from current_user."""
        pass
    
    @abstractmethod
    async def approve_leave(self, leave_id: str, request: Dict[str, Any], current_user: CurrentUser) -> Dict[str, Any]:
        """Approve employee leave. Organization context is derived from current_user."""
        pass
    
    @abstractmethod
    async def get_leave_by_id(self, leave_id: str, current_user: CurrentUser) -> Optional[Dict[str, Any]]:
        """Get employee leave by ID. Organization context is derived from current_user."""
        pass
    
    @abstractmethod
    async def list_leaves(self, filters: Optional[Dict[str, Any]] = None, current_user: CurrentUser = None) -> List[Dict[str, Any]]:
        """List employee leaves with optional filters. Organization context is derived from current_user."""
        pass 