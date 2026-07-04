import pytest

from race_dna.integrations.jolpica.mapping import (
    UnsupportedNationalityError,
    map_jolpica_driver,
)
from race_dna.integrations.jolpica.schemas import JolpicaDriver


def make_driver(
    nationality: str = "Dutch",
) -> JolpicaDriver:
    return JolpicaDriver.model_validate(
        {
            "driverId": "max_verstappen",
            "permanentNumber": "3",
            "code": "VER",
            "url": (
                "http://en.wikipedia.org/wiki/"
                "Max_Verstappen"
            ),
            "givenName": "Max",
            "familyName": "Verstappen",
            "dateOfBirth": "1997-09-30",
            "nationality": nationality,
        }
    )


def test_jolpica_driver_is_mapped_to_domain_schema() -> None:
    mapped = map_jolpica_driver(make_driver())

    assert mapped.slug == "max-verstappen"
    assert mapped.permanent_number == 3
    assert mapped.country_code == "NL"


def test_unknown_nationality_is_rejected() -> None:
    with pytest.raises(UnsupportedNationalityError):
        map_jolpica_driver(make_driver("Unknown"))