"""
Payout Service Interface
Following Interface Segregation Principle for payout business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class PayoutService(ABC):
    """Combined payout service interface."""
    
    @abstractmethod
    async def create_payout(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new payout."""
        pass
    
    @abstractmethod
    async def process_payout(self, payout_id: str) -> Dict[str, Any]:
        """Process a payout."""
        pass
    
    @abstractmethod
    async def get_payout_by_id(self, payout_id: str) -> Optional[Dict[str, Any]]:
        """Get payout by ID."""
        pass
    
    @abstractmethod
    async def list_payouts(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List payouts with optional filters."""
        pass 