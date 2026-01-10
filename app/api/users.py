from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.api.deps import verify_api_key

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Create a new user"""
    # Check if user already exists
    existing_user = await user_service.get_user_by_telegram_id(db, user_data.telegram_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with telegram_id {user_data.telegram_id} already exists"
        )

    user = await user_service.create_user(db, user_data)
    return user


@router.get("/{telegram_id}", response_model=UserResponse)
async def get_user(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Get user by telegram ID"""
    user = await user_service.get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )
    return user
