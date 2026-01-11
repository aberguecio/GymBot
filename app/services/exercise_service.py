from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.exercise import Exercise
from app.models.user import User


async def add_exercise(
    db: AsyncSession,
    telegram_id: int,
    day: date,
    description: str
) -> Exercise:
    """Add a new exercise record"""
    # Get user by telegram_id
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError(f"User with telegram_id {telegram_id} not found")

    exercise = Exercise(
        user_id=user.id,
        day=day,
        description=description
    )
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    return exercise


async def count_exercises(
    db: AsyncSession,
    telegram_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None
):
    """Count exercises by user and date range"""
    # Build query
    query = select(
        User.id,
        User.telegram_id,
        User.username,
        func.count(Exercise.id).label("count")
    ).join(Exercise, User.id == Exercise.user_id)

    # Apply filters
    filters = []
    if telegram_id:
        filters.append(User.telegram_id == telegram_id)
    if start_date:
        filters.append(Exercise.day >= start_date)
    if end_date:
        filters.append(Exercise.day <= end_date)

    if filters:
        query = query.where(and_(*filters))

    query = query.group_by(User.id, User.telegram_id, User.username)

    result = await db.execute(query)
    return result.all()


async def get_recent_exercises(
    db: AsyncSession,
    telegram_id: int,
    limit: int = 5
) -> list[Exercise]:
    """Get recent exercises for a user"""
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return []

    result = await db.execute(
        select(Exercise)
        .where(Exercise.user_id == user.id)
        .order_by(Exercise.day.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_exercises_by_date_range(
    db: AsyncSession,
    start_date: date,
    end_date: date
) -> list[Exercise]:
    """Get all exercises within a date range (for groups)"""
    result = await db.execute(
        select(Exercise)
        .where(Exercise.day >= start_date)
        .where(Exercise.day <= end_date)
        .order_by(Exercise.day.desc())
    )
    return list(result.scalars().all())
