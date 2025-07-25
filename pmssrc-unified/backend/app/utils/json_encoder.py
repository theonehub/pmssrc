from datetime import datetime, date
from typing import Any, Dict, List, Callable, Optional
from functools import wraps
import asyncio
import inspect
import json

from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi import Response
from starlette.responses import JSONResponse

class MongoJSONEncoder:
    """Custom JSON encoder for MongoDB documents."""
    
    @staticmethod
    def encode_document(obj: Dict[str, Any]) -> Dict[str, Any]:
        """Encode a MongoDB document for JSON serialization."""
        if not isinstance(obj, dict):
            return obj
            
        result = {}
        for key, value in obj.items():
            # Convert ObjectId to string
            if isinstance(value, ObjectId):
                result[key] = str(value)
            # Handle nested dictionaries
            elif isinstance(value, dict):
                result[key] = MongoJSONEncoder.encode_document(value)
            # Handle lists
            elif isinstance(value, list):
                result[key] = MongoJSONEncoder.encode_list(value)
            # Handle datetime objects
            elif isinstance(value, (datetime, date)):
                result[key] = value.isoformat() if hasattr(value, "isoformat") else str(value)
            # Pass through other types
            else:
                result[key] = value
                
        return result
    
    @staticmethod
    def encode_list(obj_list: List[Any]) -> List[Any]:
        """Encode a list of MongoDB documents or other values."""
        result = []
        for item in obj_list:
            if isinstance(item, dict):
                result.append(MongoJSONEncoder.encode_document(item))
            elif isinstance(item, list):
                result.append(MongoJSONEncoder.encode_list(item))
            elif isinstance(item, ObjectId):
                result.append(str(item))
            elif isinstance(item, (datetime, date)):
                result.append(item.isoformat() if hasattr(item, "isoformat") else str(item))
            else:
                result.append(item)
        return result
    
def mongodb_jsonable_encoder(obj: Any, **kwargs) -> Any:
    """
    A wrapper around FastAPI's jsonable_encoder that handles MongoDB ObjectId.
    
    Args:
        obj: The object to encode to JSON-compatible data
        **kwargs: Additional arguments to pass to jsonable_encoder
        
    Returns:
        JSON-compatible data
    """
    if isinstance(obj, dict):
        return MongoJSONEncoder.encode_document(obj)
    elif isinstance(obj, list):
        return MongoJSONEncoder.encode_list(obj)
    elif isinstance(obj, ObjectId):
        return str(obj)
    
    # Use FastAPI's encoder as a fallback
    return jsonable_encoder(obj, **kwargs)

def mongo_encoder_response(func: Callable) -> Callable:
    """
    Decorator to automatically encode MongoDB documents in a route handler's response.
    
    Args:
        func: The route handler function to decorate
        
    Returns:
        A wrapper function that encodes the response
    """
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # If the response is already a Response object, return it as-is
            if isinstance(result, Response):
                return result
                
            # Otherwise, encode the result
            return mongodb_jsonable_encoder(result)
            
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # If the response is already a Response object, return it as-is
            if isinstance(result, Response):
                return result
                
            # Otherwise, encode the result
            return mongodb_jsonable_encoder(result)
            
        return sync_wrapper 

class MongoJSONResponse(JSONResponse):
    """
    Custom JSONResponse that properly handles MongoDB ObjectId and other special types.
    """
    def render(self, content: Any) -> bytes:
        """
        Override the render method to use our mongodb_jsonable_encoder.
        """
        encoded_content = mongodb_jsonable_encoder(content)
        return json.dumps(
            encoded_content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8") 