from datetime import datetime
import logging
import uuid
import os
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File, Form
from openpyxl import load_workbook, Workbook
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import decode_access_token
from models.activity_tracker import ActivityTracker
from models.user_model import UserInfo
from auth.auth import extract_emp_id, extract_hostname, get_current_user
from auth.dependencies import role_checker
from auth.password_handler import hash_password
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
import services.user_service as us
from bson import ObjectId
from io import BytesIO
from services.activity_tracker_service import track_activity
import json

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
def create_user(
    user_data: str = Form(...),
    pan_file: UploadFile = File(None),
    aadhar_file: UploadFile = File(None),
    photo: UploadFile = File(None),
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
):
    """
    Endpoint to create a new user with document uploads.
    """
    try:
        # Parse the JSON string into UserInfo model
        user_data_dict = json.loads(user_data)
        user_info = UserInfo(**user_data_dict)
        
        logger.info("Creating user: %s", user_info.name)
        us.validate_user_data(user_info)

        # Handle file uploads
        if pan_file:
            user_info.pan_file_path = save_uploaded_file(pan_file, os.path.join(UPLOAD_DIR, "pan"))
        if aadhar_file:
            user_info.aadhar_file_path = save_uploaded_file(aadhar_file, os.path.join(UPLOAD_DIR, "aadhar"))
        if photo:
            user_info.photo_path = save_uploaded_file(photo, os.path.join(UPLOAD_DIR, "photos"))

        activity = ActivityTracker(
            activity_id=str(uuid.uuid4()),
            emp_id=current_emp_id,
            activity="createUser",
            date=datetime.now(),
            metadata=user_info.model_dump()
        )
        track_activity(activity, hostname)
        result = us.create_user(user_info, hostname)
        logger.info(result)
        return result
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/import", status_code=status.HTTP_201_CREATED)
def import_users_from_excel(file: UploadFile = File(...), 
                                  hostname: str = Depends(extract_hostname),
                                  current_emp_id: str = Depends(extract_emp_id)
                                  ):
    """
    Imports users from an Excel (.xlsx) file.
    """
    logger.info("Received file for user import: %s", file.filename)

    if not file.filename.endswith('.xlsx'):
        logger.warning("Invalid file type uploaded: %s", file.filename)
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")

    contents = file.read()

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
            us.create_user(user, hostname)
            created += 1
            activity = ActivityTracker(
                emp_id=current_emp_id,
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
                emp_id=current_emp_id,
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
def read_users_me(hostname: str = Depends(extract_hostname),
                        current_emp_id: str = Depends(extract_emp_id)):
    """
    Returns the username of the current logged-in user.
    """
    logger.info("read_users_me successful for username: %s", current_emp_id)
    user = us.get_user_by_emp_id(current_emp_id, hostname)
    return user

@router.get("/users")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    role: str = Depends(role_checker("admin", "superadmin", "manager")),
    hostname: str = Depends(extract_hostname),
    current_emp_id: str = Depends(extract_emp_id)
):
    """
    Lists all login info entries, paginated.
    Only accessible by admin or superadmin.
    """
    logger.info("Listing users with skip=%d, limit=%d", skip, limit)
    if role == "manager":
        logger.info("Listing users for manager: %s", current_emp_id)
        users = us.get_users_by_manager_id(current_emp_id, hostname)
    else:
        logger.info("Listing all users")
        users = us.get_all_users(hostname)
    paginated_users = [serialize_user(u) for u in users[skip:skip + limit]]

    logger.info("Returning %d users out of %d", len(paginated_users), len(users))
    return {
        "total": len(users),
        "users": paginated_users
    }
    
@router.get("/users/stats")
def get_user_stats(hostname: str = Depends(extract_hostname)):
    return us.get_users_stats(hostname)

@router.get("/users/my/directs")
def get_my_directs(hostname: str = Depends(extract_hostname),
                        current_emp_id: str = Depends(extract_emp_id)):
    return us.get_user_by_manager_id(current_emp_id, hostname)

@router.get("/users/manager/directs")
def get_user_by_manager_id(manager_id: str, hostname: str = Depends(extract_hostname)):
    return us.get_user_by_manager_id(manager_id, hostname)

@router.get("/users/template")
def download_template():
    """
    Endpoint to download the user import template file.
    """
    try:
        # Create a new workbook
        wb = Workbook()
        ws = wb.active
        
        # Add headers
        headers = ["emp_id", "email", "name", "gender", "dob", "doj", "mobile", "manager_id", "password", "role"]
        ws.append(headers)
        
        # Add example row
        example_row = [
            "EMP001",
            "example@company.com",
            "John Doe",
            "male",
            "1990-01-01",
            "2023-01-01",
            "1234567890",
            "MAN001",
            "password123",
            "user"
        ]
        ws.append(example_row)
        
        # Save to BytesIO
        template_file = BytesIO()
        wb.save(template_file)
        template_file.seek(0)
        
        return StreamingResponse(
            template_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=user_import_template.xlsx"
            }
        )
    except Exception as e:
        logger.error(f"Error generating template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate template file")
