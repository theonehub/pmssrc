"""
Base Domain Events
Base classes for domain events
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events"""
    # Override in subclasses to add required fields first, then these defaults
    pass
    
    def __post_init__(self):
        """Initialize the domain event"""
        # This can be overridden in subclasses for additional initialization
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    @property
    def event_type(self) -> str:
        """Get the event type name"""
        return self.__class__.__name__ 