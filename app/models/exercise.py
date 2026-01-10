from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    day = Column(Date, nullable=False, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con usuario
    user = relationship("User", back_populates="exercises")

    # Índice compuesto para queries eficientes
    __table_args__ = (
        Index('ix_exercises_user_day', 'user_id', 'day'),
    )
