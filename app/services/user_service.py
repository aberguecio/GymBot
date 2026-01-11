from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    """Get user by telegram ID"""
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_or_update_user(
    db: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None
) -> User:
    """Create a new user or update existing one"""
    user = await get_user_by_telegram_id(db, telegram_id)

    if user:
        # Update existing user
        if username is not None:
            user.username = username
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        await db.commit()
        await db.refresh(user)
    else:
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


