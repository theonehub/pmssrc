"""
DEPRECATED TAXATION ROUTES
This file has been migrated to SOLID architecture.
All routes have been moved to taxation_routes_v2.py

This file is kept temporarily for backward compatibility.
It will be removed in the next release.
"""

from fastapi import APIRouter, HTTPException
from starlette.responses import RedirectResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Deprecation message for all routes
DEPRECATION_MESSAGE = {
    "status": "deprecated",
    "message": "These routes have been deprecated and moved to /api/v2/taxation/",
    "action_required": "Please update your API calls to use the new v2 endpoints",
    "new_base_url": "/api/v2/taxation/",
    "migration_guide": "See TAXATION_SOLID_MIGRATION_SUMMARY.md for endpoint mapping",
    "removal_date": "Next major release"
}

@router.get("/", status_code=410)
async def deprecated_root():
    """Deprecated root endpoint"""
    logger.warning("Deprecated taxation routes accessed - please migrate to v2")
    raise HTTPException(status_code=410, detail=DEPRECATION_MESSAGE)

@router.post("/calculate-tax", status_code=410)
async def deprecated_calculate_tax():
    """Deprecated calculate tax endpoint - Use POST /api/v2/taxation/calculate"""
    logger.warning("Deprecated /calculate-tax accessed - redirect to /api/v2/taxation/calculate")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "new_endpoint": "POST /api/v2/taxation/calculate"
    })

@router.post("/save-taxation-data", status_code=410) 
async def deprecated_save_taxation_data():
    """Deprecated save taxation data endpoint - Use POST /api/v2/taxation/"""
    logger.warning("Deprecated /save-taxation-data accessed - redirect to /api/v2/taxation/")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "new_endpoint": "POST /api/v2/taxation/"
    })

@router.get("/taxation/{emp_id}", status_code=410)
async def deprecated_get_taxation(emp_id: str):
    """Deprecated get taxation endpoint - Use GET /api/v2/taxation/{employee_id}/{tax_year}"""
    logger.warning(f"Deprecated /taxation/{emp_id} accessed - redirect to /api/v2/taxation/")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "new_endpoint": f"GET /api/v2/taxation/{emp_id}/2024-2025"
    })

@router.post("/update-tax-payment", status_code=410)
async def deprecated_update_tax_payment():
    """Deprecated update tax payment endpoint"""
    logger.warning("Deprecated /update-tax-payment accessed")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "new_endpoint": "POST /api/v2/taxation/update-payment"
    })

@router.post("/update-filing-status", status_code=410)
async def deprecated_update_filing_status():
    """Deprecated update filing status endpoint"""
    logger.warning("Deprecated /update-filing-status accessed")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "new_endpoint": "POST /api/v2/taxation/update-filing-status"
    })

@router.get("/all-taxation", status_code=410)
async def deprecated_get_all_taxation():
    """Deprecated get all taxation endpoint - Use POST /api/v2/taxation/search"""
    logger.warning("Deprecated /all-taxation accessed - redirect to /api/v2/taxation/search")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "new_endpoint": "POST /api/v2/taxation/search"
    })

@router.post("/compute-vrs", status_code=410)
async def deprecated_compute_vrs():
    """Deprecated compute VRS endpoint"""
    logger.warning("Deprecated /compute-vrs accessed")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "new_endpoint": "POST /api/v2/taxation/calculate-vrs"
    })

@router.get("/my-taxation", status_code=410)
async def deprecated_get_my_taxation():
    """Deprecated get my taxation endpoint"""
    logger.warning("Deprecated /my-taxation accessed")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "new_endpoint": "GET /api/v2/taxation/my-taxation"
    })

# Add catch-all route for any other deprecated endpoints
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], status_code=410)
async def deprecated_catch_all(path: str):
    """Catch-all for any other deprecated taxation endpoints"""
    logger.warning(f"Deprecated taxation route /{path} accessed")
    raise HTTPException(status_code=410, detail={
        **DEPRECATION_MESSAGE,
        "requested_path": f"/{path}",
        "suggestion": "Check TAXATION_SOLID_MIGRATION_SUMMARY.md for the correct v2 endpoint"
    }) 