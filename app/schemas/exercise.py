from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime


class ExerciseBase(BaseModel):
    telegram_id: int
    day: date
    description: str = Field(..., min_length=1)


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseResponse(BaseModel):
    id: int
    user_id: int
    day: date
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseCountItem(BaseModel):
    user_id: int
    telegram_id: int
    username: str | None
    count: int


class ExerciseCountResponse(BaseModel):
    counts: list[ExerciseCountItem]
    period: dict[str, date | None]


class ExerciseCountSingleResponse(BaseModel):
    user_id: int
    telegram_id: int
    username: str | None
    count: int
    period: dict[str, date | None]
