"""
Event Handler Interface
Abstract interface for handling domain events
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.domain.events.base_event import DomainEvent


class EventHandler(ABC):
    """
    Abstract interface for handling domain events.
    
    Follows SOLID principles:
    - SRP: Only handles specific event types
    - OCP: Can be extended with new handlers
    - LSP: All implementations must be substitutable
    - ISP: Focused interface for event handling
    - DIP: Depends on abstractions
    """
    
    @abstractmethod
    def can_handle(self, event: DomainEvent) -> bool:
        """
        Check if this handler can handle the given event.
        
        Args:
            event: Domain event to check
            
        Returns:
            True if handler can process this event, False otherwise
        """
        pass
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """
        Handle the domain event.
        
        Args:
            event: Domain event to handle
        """
        pass
    
    @abstractmethod
    def get_supported_event_types(self) -> List[str]:
        """
        Get list of event types this handler supports.
        
        Returns:
            List of event type names
        """
        pass
    
    def get_priority(self) -> int:
        """
        Get handler priority (lower numbers = higher priority).
        
        Returns:
            Priority value (default: 100)
        """
        return 100
    
    def get_handler_name(self) -> str:
        """
        Get handler name for logging and debugging.
        
        Returns:
            Handler name
        """
        return self.__class__.__name__


class BaseEventHandler(EventHandler):
    """
    Base implementation of event handler with common functionality.
    """
    
    def __init__(self, supported_event_types: List[str], priority: int = 100):
        """
        Initialize base event handler.
        
        Args:
            supported_event_types: List of event types this handler supports
            priority: Handler priority (lower = higher priority)
        """
        self._supported_event_types = supported_event_types
        self._priority = priority
    
    def can_handle(self, event: DomainEvent) -> bool:
        """Check if this handler can handle the given event"""
        return event.get_event_type() in self._supported_event_types
    
    def get_supported_event_types(self) -> List[str]:
        """Get list of supported event types"""
        return self._supported_event_types.copy()
    
    def get_priority(self) -> int:
        """Get handler priority"""
        return self._priority


class EventHandlerRegistry:
    """
    Registry for managing event handlers.
    
    Provides centralized registration and lookup of event handlers.
    """
    
    def __init__(self):
        """Initialize event handler registry"""
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._all_handlers: List[EventHandler] = []
    
    def register_handler(self, handler: EventHandler) -> None:
        """
        Register an event handler.
        
        Args:
            handler: Event handler to register
        """
        # Add to all handlers list
        self._all_handlers.append(handler)
        
        # Register for each supported event type
        for event_type in handler.get_supported_event_types():
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            
            self._handlers[event_type].append(handler)
            
            # Sort by priority (lower numbers first)
            self._handlers[event_type].sort(key=lambda h: h.get_priority())
    
    def unregister_handler(self, handler: EventHandler) -> bool:
        """
        Unregister an event handler.
        
        Args:
            handler: Event handler to unregister
            
        Returns:
            True if handler was found and removed, False otherwise
        """
        removed = False
        
        # Remove from all handlers list
        if handler in self._all_handlers:
            self._all_handlers.remove(handler)
            removed = True
        
        # Remove from event type mappings
        for event_type in handler.get_supported_event_types():
            if event_type in self._handlers and handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                removed = True
        
        return removed
    
    def get_handlers_for_event(self, event: DomainEvent) -> List[EventHandler]:
        """
        Get handlers that can process the given event.
        
        Args:
            event: Domain event to find handlers for
            
        Returns:
            List of handlers sorted by priority
        """
        event_type = event.get_event_type()
        
        if event_type in self._handlers:
            # Return handlers that can handle this specific event
            return [h for h in self._handlers[event_type] if h.can_handle(event)]
        
        return []
    
    def get_all_handlers(self) -> List[EventHandler]:
        """
        Get all registered handlers.
        
        Returns:
            List of all registered handlers
        """
        return self._all_handlers.copy()
    
    def get_handlers_by_type(self, event_type: str) -> List[EventHandler]:
        """
        Get handlers for specific event type.
        
        Args:
            event_type: Event type to find handlers for
            
        Returns:
            List of handlers for the event type
        """
        return self._handlers.get(event_type, []).copy()
    
    def clear_handlers(self) -> None:
        """Clear all registered handlers"""
        self._handlers.clear()
        self._all_handlers.clear()
    
    def get_handler_count(self) -> int:
        """Get total number of registered handlers"""
        return len(self._all_handlers)
    
    def get_event_type_count(self) -> int:
        """Get number of event types with registered handlers"""
        return len(self._handlers)


class EventHandlerError(Exception):
    """Base exception for event handler operations"""
    pass


class EventHandlerRegistrationError(EventHandlerError):
    """Exception raised when event handler registration fails"""
    
    def __init__(self, handler_name: str, reason: str):
        self.handler_name = handler_name
        self.reason = reason
        super().__init__(f"Failed to register event handler '{handler_name}': {reason}")


class EventHandlerExecutionError(EventHandlerError):
    """Exception raised when event handler execution fails"""
    
    def __init__(self, handler_name: str, event_type: str, reason: str):
        self.handler_name = handler_name
        self.event_type = event_type
        self.reason = reason
        super().__init__(f"Event handler '{handler_name}' failed to process event '{event_type}': {reason}") 