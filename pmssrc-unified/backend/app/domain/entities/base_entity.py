"""
Base Entity
Base class for all domain entities providing common functionality
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import List, Any
from datetime import datetime


@dataclass
class BaseEntity(ABC):
    """
    Base class for all domain entities.
    
    Provides common functionality like domain event handling
    and basic entity operations following DDD principles.
    """
    
    # Domain events
    _domain_events: List[Any] = field(default_factory=list, init=False)
    
    def add_domain_event(self, event: Any) -> None:
        """Add a domain event to be published"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[Any]:
        """Get all domain events"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear all domain events after publishing"""
        self._domain_events.clear()
    
    def has_domain_events(self) -> bool:
        """Check if entity has domain events"""
        return len(self._domain_events) > 0 