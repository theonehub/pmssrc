import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models.user_model import Token
from auth.password_handler import verify_password
from auth.jwt_handler import create_access_token
from services.user_service import get_user_by_emp_id
from models.OAuth2PasswordRequestFormWithHost import OAuth2PasswordRequestFormWithHost
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestFormWithHost = Depends()):
    """
    Endpoint for user login.
    Verifies user credentials and returns a JWT token on success.
    """
    logger.info("Login attempt for user: %s", form_data.username + " " + form_data.hostname)
    user = get_user_by_emp_id(form_data.username, form_data.hostname)
    logger.info("User: %s", user)
    if not user:
        user = get_user_by_emp_id(form_data.username, "global_database")
        logger.info("Global User: %s", user)
    if not user or not verify_password(form_data.password, user["password"]):
        logger.warning("Invalid credentials for user: %s", form_data.username)
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    token = create_access_token(data={"sub": user["emp_id"], "role": user["role"], "hostname": form_data.hostname})
    logger.info("User %s logged in successfully.", form_data.username)
    return {"access_token": token, "token_type": "bearer"}
