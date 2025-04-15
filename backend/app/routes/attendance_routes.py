from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List
from services import attendance_service
from auth.auth import get_current_user
from models.user_model import User
from pydantic import BaseModel, Field
import logging

routes = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

# ----------- Pydantic Models -----------

class LWPUpdateRequest(BaseModel):
    user_id: str
    month: str  # Format: "YYYY-MM"
    lwp_days: int = Field(..., ge=0, le=31)


class LWPMultiUserRequest(BaseModel):
    month: str
    data: List[LWPUpdateRequest]


# ----------- Routes -----------

@routes.post("/update", summary="Upsert LWP for a single user")
def update_lwp(data: LWPUpdateRequest, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "superadmin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied")

    #logger.info(f"[LWP-Update] {current_user.email} updating LWP for user {data.user_id}, month: {data.month}, days: {data.lwp_days}")
    return attendance_service.upsert_lwp_for_user(data.user_id, data.month, data.lwp_days)


@routes.post("/bulk-update", summary="Upsert LWP for multiple users")
def bulk_update_lwp(data: LWPMultiUserRequest, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "superadmin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied")

    #logger.info(f"[LWP-Bulk-Update] {current_user.email} bulk updating LWP for {len(data.data)} users for month {data.month}")

    responses = []
    for record in data.data:
        if record.lwp_days < 0 or record.lwp_days > 31:
            logger.warning(f"Skipping invalid LWP for {record.user_id} (lwp_days: {record.lwp_days})")
            continue
        res = attendance_service.upsert_lwp_for_user(record.user_id, data.month, record.lwp_days)
        responses.append(res)

    return {"results": responses}


@routes.get("/month/{month}", summary="Get LWP for all users for a specific month")
def get_lwp_by_month(month: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "superadmin", "hr"]:
        raise HTTPException(status_code=403, detail="Access denied")

    logger.info(f"[LWP-Fetch] {current_user.username} fetching LWP records for month: {month}")
    return attendance_service.get_lwp_by_month(month)


@routes.get("/user/{user_id}", summary="Get LWP history for a specific user")
def get_lwp_for_user(user_id: str, current_user: User = Depends(get_current_user)):
    # Employees can only view their own LWP
    if current_user.role == "user" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    #logger.info(f"[LWP-User-Fetch] {current_user.email} fetching LWP history for user: {user_id}")
    return attendance_service.get_lwp_for_user(user_id)
