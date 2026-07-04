from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from race_dna.db.base import Base


class DriverRaceResult(Base):
    __tablename__ = "driver_race_results"
    __table_args__ = (
        UniqueConstraint(
            "driver_id",
            "race_id",
            name="uq_driver_race_results_driver_race",
        ),
        CheckConstraint(
            "grid_position >= 0",
            name="grid_position_non_negative",
        ),
        CheckConstraint(
            "finish_position >= 1",
            name="finish_position_positive",
        ),
        CheckConstraint(
            "points >= 0",
            name="points_non_negative",
        ),
        CheckConstraint(
            "laps >= 0",
            name="laps_non_negative",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )
    driver_id: Mapped[UUID] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"),
        index=True,
    )
    race_id: Mapped[UUID] = mapped_column(
        ForeignKey("races.id", ondelete="CASCADE"),
        index=True,
    )
    car_number: Mapped[int] = mapped_column(Integer)
    finish_position: Mapped[int] = mapped_column(Integer)
    position_text: Mapped[str] = mapped_column(String(10))
    grid_position: Mapped[int] = mapped_column(Integer)
    points: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    laps: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(100))
    constructor_id: Mapped[str] = mapped_column(String(64))
    constructor_name: Mapped[str] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )