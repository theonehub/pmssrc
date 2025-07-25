"""
MongoDB Event Publisher Implementation
Concrete implementation of event publisher using MongoDB for persistence
"""

import logging
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING

from app.application.interfaces.services.event_publisher import EventPublisher
from app.domain.events.employee_events import DomainEvent
from app.database.database_connector import connect_to_database


class MongoDBEventPublisher(EventPublisher):
    """
    MongoDB implementation of event publisher.
    
    Follows SOLID principles:
    - SRP: Only handles event publishing and storage
    - OCP: Can be extended with new event types
    - LSP: Can be substituted with other implementations
    - ISP: Implements only event publishing operations
    - DIP: Depends on MongoDB abstractions
    """
    
    def __init__(self, hostname: str):
        self._hostname = hostname
        self._logger = logging.getLogger(__name__)
        self._db = connect_to_database(hostname)
        self._collection: Collection = self._db["domain_events"]
        self._subscribers: Dict[str, List[Callable]] = {}
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure necessary indexes exist"""
        try:
            self._collection.create_index([("event_type", ASCENDING)])
            self._collection.create_index([("aggregate_id", ASCENDING)])
            self._collection.create_index([("occurred_at", DESCENDING)])
            self._collection.create_index([("processed", ASCENDING)])
        except Exception as e:
            self._logger.warning(f"Error creating event indexes: {e}")
    
    def publish(self, event: DomainEvent) -> bool:
        """Publish a single domain event"""
        try:
            # Store event in MongoDB
            event_document = self._event_to_document(event)
            result = self._collection.insert_one(event_document)
            
            if result.inserted_id:
                # Notify in-memory subscribers
                self._notify_subscribers(event)
                self._logger.info(f"Published event: {event.get_event_type()}")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error publishing event: {e}")
            return False
    
    def publish_batch(self, events: List[DomainEvent]) -> Dict[str, bool]:
        """Publish multiple domain events in batch"""
        results = {}
        
        try:
            # Prepare documents for batch insert
            documents = []
            for event in events:
                documents.append(self._event_to_document(event))
            
            # Batch insert to MongoDB
            if documents:
                insert_result = self._collection.insert_many(documents)
                
                # Process results and notify subscribers
                for i, event in enumerate(events):
                    event_id = f"{event.get_aggregate_id()}_{event.occurred_at.isoformat()}"
                    success = i < len(insert_result.inserted_ids) and insert_result.inserted_ids[i] is not None
                    results[event_id] = success
                    
                    if success:
                        self._notify_subscribers(event)
                
                self._logger.info(f"Published {len(documents)} events in batch")
            
        except Exception as e:
            self._logger.error(f"Error publishing event batch: {e}")
            # Mark all as failed
            for event in events:
                event_id = f"{event.get_aggregate_id()}_{event.occurred_at.isoformat()}"
                results[event_id] = False
        
        return results
    
    def subscribe(
        self, 
        event_type: str, 
        handler: Callable[[DomainEvent], None]
    ) -> str:
        """Subscribe to events of a specific type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        
        # Generate subscription ID
        subscription_id = f"{event_type}_{len(self._subscribers[event_type])}"
        
        self._logger.info(f"Added subscription for {event_type}")
        return subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events"""
        try:
            # Parse subscription ID to find event type and handler
            parts = subscription_id.split('_')
            if len(parts) >= 2:
                event_type = '_'.join(parts[:-1])
                handler_index = int(parts[-1]) - 1
                
                if (event_type in self._subscribers and 
                    0 <= handler_index < len(self._subscribers[event_type])):
                    
                    del self._subscribers[event_type][handler_index]
                    self._logger.info(f"Removed subscription: {subscription_id}")
                    return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Error unsubscribing: {e}")
            return False
    
    def get_event_history(
        self,
        aggregate_id: Optional[str] = None,
        event_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DomainEvent]:
        """Get event history with optional filtering"""
        try:
            # Build query
            query = {}
            
            if aggregate_id:
                query["aggregate_id"] = aggregate_id
            
            if event_type:
                query["event_type"] = event_type
            
            if from_date or to_date:
                date_query = {}
                if from_date:
                    date_query["$gte"] = from_date
                if to_date:
                    date_query["$lte"] = to_date
                query["occurred_at"] = date_query
            
            # Execute query
            cursor = self._collection.find(query).sort("occurred_at", DESCENDING).limit(limit)
            documents = list(cursor)
            
            # Convert documents back to events
            events = []
            for doc in documents:
                try:
                    event = self._document_to_event(doc)
                    if event:
                        events.append(event)
                except Exception as e:
                    self._logger.warning(f"Error converting document to event: {e}")
            
            return events
            
        except Exception as e:
            self._logger.error(f"Error retrieving event history: {e}")
            return []
    
    def _event_to_document(self, event: DomainEvent) -> Dict[str, Any]:
        """Convert domain event to MongoDB document"""
        return {
            "event_type": event.get_event_type(),
            "aggregate_id": event.get_aggregate_id(),
            "occurred_at": event.occurred_at,
            "event_data": self._serialize_event_data(event),
            "processed": False,
            "created_at": datetime.utcnow()
        }
    
    def _document_to_event(self, document: Dict[str, Any]) -> Optional[DomainEvent]:
        """Convert MongoDB document back to domain event"""
        try:
            # This would need to be implemented based on your event registry
            # For now, return a generic event structure
            event_type = document["event_type"]
            event_data = document["event_data"]
            
            # You would use your event registry here to reconstruct the proper event type
            # For example:
            # from app.domain.events.leave_events import get_leave_event_class
            # event_class = get_leave_event_class(event_type)
            # if event_class:
            #     return event_class(**event_data)
            
            return None  # Placeholder - implement based on your event system
            
        except Exception as e:
            self._logger.error(f"Error converting document to event: {e}")
            return None
    
    def _serialize_event_data(self, event: DomainEvent) -> Dict[str, Any]:
        """Serialize event data for storage"""
        try:
            # Convert event to dictionary, handling special types
            event_dict = {}
            
            for key, value in event.__dict__.items():
                if key.startswith('_'):
                    continue
                
                if isinstance(value, datetime):
                    event_dict[key] = value.isoformat()
                elif hasattr(value, '__dict__'):
                    # Handle value objects and entities
                    event_dict[key] = self._serialize_object(value)
                else:
                    event_dict[key] = value
            
            return event_dict
            
        except Exception as e:
            self._logger.error(f"Error serializing event data: {e}")
            return {}
    
    def _serialize_object(self, obj: Any) -> Dict[str, Any]:
        """Serialize complex objects"""
        try:
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if key.startswith('_'):
                        continue
                    
                    if isinstance(value, datetime):
                        result[key] = value.isoformat()
                    elif hasattr(value, 'value'):  # Handle enums
                        result[key] = value.value
                    elif hasattr(value, '__dict__'):
                        result[key] = self._serialize_object(value)
                    else:
                        result[key] = value
                
                return result
            else:
                return str(obj)
                
        except Exception as e:
            self._logger.error(f"Error serializing object: {e}")
            return {}
    
    def _notify_subscribers(self, event: DomainEvent):
        """Notify in-memory subscribers"""
        try:
            event_type = event.get_event_type()
            if event_type in self._subscribers:
                for handler in self._subscribers[event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        self._logger.error(f"Error in event handler: {e}")
        except Exception as e:
            self._logger.error(f"Error notifying subscribers: {e}")
    
    def mark_event_processed(self, event_id: str) -> bool:
        """Mark an event as processed"""
        try:
            result = self._collection.update_one(
                {"_id": event_id},
                {"$set": {"processed": True, "processed_at": datetime.utcnow()}}
            )
            return result.matched_count > 0
        except Exception as e:
            self._logger.error(f"Error marking event as processed: {e}")
            return False
    
    def get_unprocessed_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get unprocessed events for background processing"""
        try:
            cursor = self._collection.find(
                {"processed": False}
            ).sort("created_at", ASCENDING).limit(limit)
            
            return list(cursor)
        except Exception as e:
            self._logger.error(f"Error retrieving unprocessed events: {e}")
            return [] 