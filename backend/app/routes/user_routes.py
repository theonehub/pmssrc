import logging
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from openpyxl import load_workbook
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import decode_access_token
from models.user_model import UserInfo
from auth.auth import get_current_user
from auth.dependencies import role_checker
from auth.password_handler import hash_password
from fastapi.responses import JSONResponse
import services.user_service as us
from bson import ObjectId
from io import BytesIO

def serialize_user(user):
    user = user.copy()
    for key in user:
        if isinstance(user[key], ObjectId):
            user[key] = str(user[key])
    return user


logger = logging.getLogger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/createUser", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserInfo):
    """
    Endpoint to create a new user.
    Stores general user info and, if login is required, creates a login entry.
    """
    logger.info("Creating user: %s", user.name)
    login_data = {}
    user_data = {
        "empId":user.empId,
        "email":user.email,
        "name": user.name,
        "gender": user.gender,
        "dob": str(user.dob),
        "doj": str(user.doj),
        "mobile": user.mobile
    }
    # If login is required, verify additional fields and prepare login data.
    if user.login_required:
        if not user.username or not user.password or not user.role:
            logger.error("Login required but missing username, password, or role.")
            raise HTTPException(status_code=400, detail="Username, password, and role are required for login-enabled users")
        login_data = {
            "username": user.username,
            "password": hash_password(user.password),
            "role": user.role.lower()
        }
    result = us.create_user(user_data, login_data)
    logger.info("User creation result: %s", result)
    return result

@router.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    Returns the username of the current logged-in user.
    """
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if not username:
            logger.warning("Token payload missing username.")
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error("Error in read_users_me: %s", e)
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = us.get_login_info_by_username(username)
    if not user:
        logger.warning("User not found for username: %s", username)
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("read_users_me successful for username: %s", username)
    return {"username": username}

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

@router.post("/users/import", status_code=status.HTTP_201_CREATED)
async def import_users_from_excel(file: UploadFile = File(...)):
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
    expected_headers = ["empId", "email","name", "gender", "dob", "doj", "mobile", "login_required", "username", "password", "role"]
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
            user_data = {
                "empId": row[0],
                "email": row[1],
                "name": row[2],
                "gender": row[3],
                "dob": str(row[4]),
                "doj": str(row[5]),
                "mobile": str(row[6])
            }

            login_required = row[5]
            login_data = {}

            if login_required:
                if not row[6] or not row[7] or not row[8]:
                    raise ValueError("Missing login fields for login-required user")
                login_data = {
                    "username": row[7],
                    "password": hash_password(row[8]),
                    "role": row[8].lower()
                }

            result = us.create_user(user_data, login_data)
            logger.debug("Result for row %d: %s", idx, result)

            if "successfully" in result.get("msg", "").lower():
                created += 1
            else:
                failed += 1
                error_msg = f"Row {idx}: {result.get('msg')}"
                logger.warning(error_msg)
                errors.append(error_msg)

        except Exception as e:
            failed += 1
            error_msg = f"Row {idx}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

    logger.info("User import completed: %d created, %d failed", created, failed)
    return {
        "created": created,
        "failed": failed,
        "errors": errors
    }
    
    
    @router.get("/my-lwp", summary="Get LWP for current logged-in user")
    def get_my_lwp(current_user: User = Depends(get_current_user)):
        return attendance_service.get_lwp_for_user(current_user.id)

    