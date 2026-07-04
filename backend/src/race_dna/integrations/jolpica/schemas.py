from datetime import date

from pydantic import BaseModel, Field, HttpUrl


class JolpicaDriver(BaseModel):
    driver_id: str = Field(alias="driverId")
    permanent_number: int | None = Field(
        default=None,
        alias="permanentNumber",
    )
    code: str | None = None
    url: HttpUrl
    given_name: str = Field(alias="givenName")
    family_name: str = Field(alias="familyName")
    date_of_birth: date = Field(alias="dateOfBirth")
    nationality: str


class JolpicaDriverTable(BaseModel):
    drivers: list[JolpicaDriver] = Field(alias="Drivers")


class JolpicaMRData(BaseModel):
    driver_table: JolpicaDriverTable = Field(alias="DriverTable")


class JolpicaDriverResponse(BaseModel):
    mr_data: JolpicaMRData = Field(alias="MRData")