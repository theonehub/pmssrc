from datetime import datetime
import logging
import uuid
import os
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from openpyxl import load_workbook
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import decode_access_token
from models.activity_tracker import ActivityTracker
from models.user_model import UserInfo
from auth.auth import extract_emp_id, get_current_user
from auth.dependencies import role_checker
from auth.password_handler import hash_password
from fastapi.responses import JSONResponse
import services.user_service as us
from bson import ObjectId
from io import BytesIO
from services.activity_tracker_service import track_activity

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    os.makedirs(os.path.join(UPLOAD_DIR, "pan"))
    os.makedirs(os.path.join(UPLOAD_DIR, "aadhar"))
    os.makedirs(os.path.join(UPLOAD_DIR, "photos"))

def serialize_user(user):
    user = user.copy()
    for key in user:
        if isinstance(user[key], ObjectId):
            user[key] = str(user[key])
    return user

def save_uploaded_file(file: UploadFile, directory: str) -> str:
    if not file:
        return None
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf'}
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(directory, filename)
    
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

logger = logging.getLogger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/users/create", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserInfo = Depends(),
    pan_file: UploadFile = File(None),
    aadhar_file: UploadFile = File(None),
    photo: UploadFile = File(None),
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Endpoint to create a new user with document uploads.
    """
    logger.info("Creating user: %s", user_data.name)
    us.validate_user_data(user_data)

    # Handle file uploads
    if pan_file:
        user_data.pan_file_path = save_uploaded_file(pan_file, os.path.join(UPLOAD_DIR, "pan"))
    if aadhar_file:
        user_data.aadhar_file_path = save_uploaded_file(aadhar_file, os.path.join(UPLOAD_DIR, "aadhar"))
    if photo:
        user_data.photo_path = save_uploaded_file(photo, os.path.join(UPLOAD_DIR, "photos"))

    activity = ActivityTracker(
        activityId=str(uuid.uuid4()),
        emp_id=current_user.emp_id,
        activity="createUser",
        date=datetime.now(),
        metadata=user_data.model_dump()
    )
    track_activity(activity)
    result = us.create_user(user_data)
    logger.info(result)
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
    expected_headers = ["emp_id", "email","name", "gender", "dob", "doj", "mobile", "manager_id", "password", "role"]
    logger.info("Parsed headers from Excel: %s", headers)

    if headers != expected_headers:
        logger.warning("Invalid headers in uploaded Excel: %s", headers)
        raise HTTPException(status_code=400, detail=f"Invalid headers. Expected: {expected_headers}")

    created, failed = 0, 0
    errors = []

    logger.info("Starting user creation loop")
    for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        try:
            logger.info("Processing row %d: %s", idx, row)
            user = UserInfo(
                emp_id=row[0],
                email=row[1],
                name=row[2],
                gender=row[3],
                dob=row[4],
                doj=row[5], 
                mobile=row[6],
                manager_id=row[7],
                password=row[8],
                role=row[9]
            )
            await us.create_user(user)
            created += 1
            activity = ActivityTracker(
                emp_id=current_user.emp_id,
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
                emp_id=current_user.emp_id,
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
    logger.info("read_users_me successful for username: %s", current_user.emp_id)
    return current_user

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    role: str = Depends(role_checker("admin", "superadmin", "manager")),
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Lists all login info entries, paginated.
    Only accessible by admin or superadmin.
    """
    logger.info("Listing users with skip=%d, limit=%d", skip, limit)
    if role == "manager":
        logger.info("Listing users for manager: %s", current_user.emp_id)
        users = us.get_users_by_manager_id(current_user.emp_id)
    else:
        logger.info("Listing all users")
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
    return us.get_user_by_manager_id(current_user.emp_id)

@router.get("/users/manager/directs")
def get_user_by_manager_id(manager_id: str):
        return us.get_user_by_manager_id(manager_id)
