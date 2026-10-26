"""
Authentication API Routes.
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import hash_password, verify_password, create_access_token
import uuid
from datetime import datetime

router = APIRouter()

# In-memory user store (replace with database in production)
_users_db = {}


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user account."""
    # Check if email exists
    for u in _users_db.values():
        if u["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    user_id = str(uuid.uuid4())
    _users_db[user_id] = {
        "id": user_id,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "full_name": user.full_name,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
    }

    token = create_access_token(data={"sub": user_id})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login with email and password."""
    user = None
    for u in _users_db.values():
        if u["email"] == credentials.email:
            user = u
            break

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": user["id"]})
    return Token(access_token=token)


@router.get("/me")
async def get_me():
    """Get current user info (placeholder)."""
    return {"message": "Auth endpoint active"}
