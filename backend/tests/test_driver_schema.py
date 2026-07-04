from datetime import date

import pytest
from pydantic import ValidationError

from race_dna.schemas.driver import DriverCreate


VALID_DRIVER_DATA = {
    "slug": "max-verstappen",
    "given_name": "Max",
    "family_name": "Verstappen",
    "code": "ver",
    "permanent_number": 33,
    "country_code": "nl",
    "date_of_birth": "1997-09-30",
}


def test_driver_schema_normalizes_codes() -> None:
    driver = DriverCreate(**VALID_DRIVER_DATA)

    assert driver.code == "VER"
    assert driver.country_code == "NL"
    assert driver.date_of_birth == date(1997, 9, 30)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("slug", "Max Verstappen"),
        ("permanent_number", 100),
        ("country_code", "NLD"),
        ("code", "MV"),
    ],
)
def test_driver_schema_rejects_invalid_values(
    field: str,
    value: object,
) -> None:
    data = VALID_DRIVER_DATA | {field: value}

    with pytest.raises(ValidationError):
        DriverCreate(**data)