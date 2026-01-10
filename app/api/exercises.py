from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from app.database import get_db
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseResponse,
    ExerciseCountResponse,
    ExerciseCountSingleResponse,
    ExerciseCountItem
)
from app.services import exercise_service
from app.api.deps import verify_api_key

router = APIRouter()


@router.post("/", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise_data: ExerciseCreate,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Add a new exercise record"""
    try:
        exercise = await exercise_service.add_exercise(
            db=db,
            telegram_id=exercise_data.telegram_id,
            day=exercise_data.day,
            description=exercise_data.description
        )
        return exercise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/count")
async def get_exercise_count(
    telegram_id: int | None = Query(None, description="Filter by telegram ID"),
    month: str | None = Query(None, description="Month in YYYY-MM format"),
    start_date: date | None = Query(None, description="Start date"),
    end_date: date | None = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Get exercise count by user and date range"""

    # Parse month parameter if provided
    if month:
        try:
            month_date = datetime.strptime(month, "%Y-%m")
            start_date = month_date.date()
            # Get last day of month
            next_month = month_date + relativedelta(months=1)
            end_date = next_month.date() - relativedelta(days=1)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid month format. Use YYYY-MM"
            )

    # Get counts
    counts = await exercise_service.count_exercises(
        db=db,
        telegram_id=telegram_id,
        start_date=start_date,
        end_date=end_date
    )

    # If specific telegram_id was requested, return single response
    if telegram_id:
        if counts:
            count_data = counts[0]
            return ExerciseCountSingleResponse(
                user_id=count_data.id,
                telegram_id=count_data.telegram_id,
                username=count_data.username,
                count=count_data.count,
                period={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
        else:
            # User exists but has no exercises in this period
            return ExerciseCountSingleResponse(
                user_id=0,
                telegram_id=telegram_id,
                username=None,
                count=0,
                period={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )

    # Return all users
    count_items = [
        ExerciseCountItem(
            user_id=row.id,
            telegram_id=row.telegram_id,
            username=row.username,
            count=row.count
        )
        for row in counts
    ]

    return ExerciseCountResponse(
        counts=count_items,
        period={
            "start_date": start_date,
            "end_date": end_date
        }
    )
