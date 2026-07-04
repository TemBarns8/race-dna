from datetime import date, datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class DriverCreate(BaseModel):
    slug: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )
    given_name: str = Field(min_length=1, max_length=100)
    family_name: str = Field(min_length=1, max_length=100)
    code: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )
    permanent_number: int | None = Field(
        default=None,
        ge=1,
        le=99,
    )
    country_code: str = Field(
        min_length=2,
        max_length=2,
    )
    date_of_birth: date

    @field_validator("code", "country_code")
    @classmethod
    def normalize_uppercase(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        return value.upper()


class DriverRead(DriverCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime