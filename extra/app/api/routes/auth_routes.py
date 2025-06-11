"""
Authentication Routes (Placeholder)
API endpoints for authentication operations
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/auth/placeholder")
async def auth_placeholder():
    """Placeholder auth endpoint."""
    return {"message": "Authentication routes - Coming soon"} 