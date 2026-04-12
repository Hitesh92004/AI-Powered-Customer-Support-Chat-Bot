"""
Auth routes — register, login, and current user.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from app.services import auth_service, db_service as db
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    """Register a new user."""
    existing = await db.get_user_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    password_hash = auth_service.hash_password(body.password)
    user = await db.create_user(body.email, password_hash)

    token = auth_service.create_access_token(str(user["id"]), user["email"])
    return AuthResponse(
        access_token=token,
        user_id=str(user["id"]),
        email=user["email"],
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest):
    """Login with email and password."""
    user = await db.get_user_by_email(body.email)
    if not user or not auth_service.verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = auth_service.create_access_token(str(user["id"]), user["email"])
    return AuthResponse(
        access_token=token,
        user_id=str(user["id"]),
        email=user["email"],
    )


@router.post("/demo", response_model=AuthResponse)
async def demo_login():
    """Auto-login as a guest demo user. Creates the user if they don't exist."""
    demo_email = "demo@example.com"
    demo_password = "demo_password_123"
    
    user = await db.get_user_by_email(demo_email)
    if not user:
        password_hash = auth_service.hash_password(demo_password)
        user = await db.create_user(demo_email, password_hash)
        
    token = auth_service.create_access_token(str(user["id"]), user["email"])
    return AuthResponse(
        access_token=token,
        user_id=str(user["id"]),
        email=user["email"],
    )


@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    """Get current authenticated user's info."""
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"id": str(user["id"]), "email": user["email"]}
