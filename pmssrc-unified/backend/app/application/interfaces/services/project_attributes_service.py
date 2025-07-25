"""
Project Attributes Service Interface
Following Interface Segregation Principle for project attributes business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class ProjectAttributesService(ABC):
    """Combined project attributes service interface."""
    
    @abstractmethod
    async def create_project_attributes(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create project attributes."""
        pass
    
    @abstractmethod
    async def get_project_attributes(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project attributes by ID."""
        pass
    
    @abstractmethod
    async def list_project_attributes(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List project attributes with optional filters."""
        pass 