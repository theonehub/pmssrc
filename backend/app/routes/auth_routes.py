import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models.user_model import Token, UserCreate
from auth.password_handler import hash_password, verify_password
from auth.jwt_handler import create_access_token
from services.user_service import get_login_info_by_username, create_login_info

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint for user login.
    Verifies user credentials and returns a JWT token on success.
    """
    logger.info("Login attempt for user: %s", form_data.username)
    user = get_login_info_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        logger.warning("Invalid credentials for user: %s", form_data.username)
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    logger.info("User %s logged in successfully.", form_data.username)
    return {"access_token": token, "token_type": "bearer"}
