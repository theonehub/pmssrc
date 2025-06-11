"""
User Routes (Placeholder)
API endpoints for user management operations
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/users/placeholder")
async def users_placeholder():
    """Placeholder users endpoint."""
    return {"message": "User routes - Coming soon"} 