from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from race_dna.db.base import Base


class DriverQualifyingResult(Base):
    __tablename__ = "driver_qualifying_results"
    __table_args__ = (
        UniqueConstraint(
            "driver_id",
            "race_id",
            name="uq_driver_qualifying_results_driver_race",
        ),
        CheckConstraint(
            "position >= 1",
            name="position_positive",
        ),
        CheckConstraint(
            "car_number >= 0",
            name="car_number_non_negative",
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
    position: Mapped[int] = mapped_column(Integer)
    constructor_id: Mapped[str] = mapped_column(String(64))
    constructor_name: Mapped[str] = mapped_column(String(150))
    q1: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    q2: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    q3: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )