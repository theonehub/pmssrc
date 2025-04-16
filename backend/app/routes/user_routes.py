from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from openpyxl import load_workbook
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import decode_access_token
from models.activity_tracker import ActivityTracker
from models.user_model import UserInfo
from auth.auth import extract_empId, get_current_user
from auth.dependencies import role_checker
from auth.password_handler import hash_password
from fastapi.responses import JSONResponse
import services.user_service as us
from bson import ObjectId
from io import BytesIO
from services.activity_tracker_service import track_activity

def serialize_user(user):
    user = user.copy()
    for key in user:
        if isinstance(user[key], ObjectId):
            user[key] = str(user[key])
    return user


logger = logging.getLogger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserInfo, current_user: UserInfo = Depends(extract_empId)):
    """
    Endpoint to create a new user.
    Stores general user info and, if login is required, creates a login entry.
    """
    logger.info("Creating user: %s", user.name)
    us.validate_user_data(user)
    activity = ActivityTracker(
        empId=current_user.empId,
        activity="createUser",
        date=datetime.now(),
        metadata=user.model_dump()
    )
    track_activity(activity)
    result = us.create_user(user)
    logger.info("User creation result: %s", result)
    return result


@router.post("/users/import", status_code=status.HTTP_201_CREATED)
async def import_users_from_excel(file: UploadFile = File(...), current_user: UserInfo = Depends(get_current_user)):
    """
    Imports users from an Excel (.xlsx) file.
    """
    logger.info("Received file for user import: %s", file.filename)

    if not file.filename.endswith('.xlsx'):
        logger.warning("Invalid file type uploaded: %s", file.filename)
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    contents = await file.read()

    try:
        logger.info("Attempting to load Excel workbook")
        wb = load_workbook(BytesIO(contents), data_only=True)
        sheet = wb.active
    except Exception as e:
        logger.error("Failed to read Excel file: %s", str(e))
        raise HTTPException(status_code=500, detail="Error reading Excel file")

    headers = [cell.value for cell in sheet[1]]
    expected_headers = ["empId", "email","name", "gender", "dob", "doj", "mobile", "managerId", "login_required", "password", "role"]
    logger.info("Parsed headers from Excel: %s", headers)

    if headers != expected_headers:
        logger.warning("Invalid headers in uploaded Excel: %s", headers)
        raise HTTPException(status_code=400, detail=f"Invalid headers. Expected: {expected_headers}")

    created, failed = 0, 0
    errors = []

    logger.info("Starting user creation loop")
    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        try:
            logger.debug("Processing row %d: %s", idx, row)
            user = UserInfo(
                empId=row[0],
                email=row[1],
                name=row[2],
                gender=row[3],
                dob=row[4],
                doj=row[5], 
                mobile=row[6],
                managerId=row[7],
                login_required=row[8],
                password=row[9],
                role=row[10]
            )
            us.create_user(user)
            created += 1
            activity = ActivityTracker(
                empId=current_user.empId,
                activity="importUsersSuccess",
                date=datetime.now(),
                metadata=user.model_dump()
            )
            track_activity(activity)
        except Exception as e:
            failed += 1
            error_msg = f"Row {idx}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            activity = ActivityTracker(
                empId=current_user.empId,
                activity="importUsersFailed",
                date=datetime.now(),
                metadata=user.model_dump()
            )
            track_activity(activity)

    logger.info("User import completed: %d created, %d failed", created, failed)
    return {
        "created": created,
        "failed": failed,
        "errors": errors
    }


@router.get("/users/me")
async def read_users_me(current_user: UserInfo = Depends(get_current_user)):
    """
    Returns the username of the current logged-in user.
    """
    logger.info("read_users_me successful for username: %s", current_user.empId)
    return current_user

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    role: str = Depends(role_checker("admin", "superadmin"))
):
    """
    Lists all login info entries, paginated.
    Only accessible by admin or superadmin.
    """
    logger.info("Listing users with skip=%d, limit=%d", skip, limit)
    users = us.get_all_users()
    paginated_users = [serialize_user(u) for u in users[skip:skip + limit]]

    logger.info("Returning %d users out of %d", len(paginated_users), len(users))
    return {
        "total": len(users),
        "users": paginated_users
    }
    
@router.get("/users/stats")
def get_user_stats():
    return us.get_users_stats()

@router.get("/users/my/directs")
async def get_my_directs(current_user: UserInfo = Depends(get_current_user)):
    return us.get_user_by_managerId(current_user.empId)

@router.get("/users/manager/directs")
def get_user_by_managerId(managerId: str):
    return us.get_user_by_managerId(managerId)
