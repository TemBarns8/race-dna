from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
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


class Race(Base):
    __tablename__ = "races"
    __table_args__ = (
        UniqueConstraint(
            "season_year",
            "round",
            name="uq_races_season_round",
        ),
        CheckConstraint(
            "round >= 1",
            name="round_positive",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )
    season_year: Mapped[int] = mapped_column(
        ForeignKey("seasons.year", ondelete="CASCADE"),
        index=True,
    )
    round: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(150))
    date: Mapped[date] = mapped_column(Date)
    circuit_id: Mapped[str] = mapped_column(String(64))
    circuit_name: Mapped[str] = mapped_column(String(150))
    locality: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )