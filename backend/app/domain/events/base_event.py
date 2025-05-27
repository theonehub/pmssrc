"""
Base Domain Event
Abstract base class for all domain events
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any
import uuid


class DomainEvent(ABC):
    """
    Abstract base class for all domain events.
    
    Follows SOLID principles:
    - SRP: Only defines event structure
    - OCP: Can be extended by specific event types
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for events
    - DIP: Depends on abstractions
    """
    
    def __init__(self, aggregate_id: str, occurred_at: datetime = None):
        self.event_id = str(uuid.uuid4())
        self.aggregate_id = aggregate_id
        self.occurred_at = occurred_at or datetime.utcnow()
    
    @abstractmethod
    def get_event_type(self) -> str:
        """Get the event type identifier"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainEvent':
        """Create event from dictionary representation"""
        pass
    
    def get_aggregate_id(self) -> str:
        """Get the aggregate ID this event belongs to"""
        return self.aggregate_id
    
    def get_event_id(self) -> str:
        """Get the unique event ID"""
        return self.event_id
    
    def get_occurred_at(self) -> datetime:
        """Get when the event occurred"""
        return self.occurred_at 