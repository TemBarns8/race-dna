from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from race_dna.db.base import Base


class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (
        CheckConstraint(
            "year >= 1950",
            name="year_since_1950",
        ),
    )

    year: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )