from race_dna.integrations.jolpica.schemas import JolpicaDriver
from race_dna.schemas.driver import DriverCreate


COUNTRY_CODE_BY_NATIONALITY = {
    "Dutch": "NL",
}


class UnsupportedNationalityError(ValueError):
    pass


def map_jolpica_driver(
    source: JolpicaDriver,
) -> DriverCreate:
    country_code = COUNTRY_CODE_BY_NATIONALITY.get(
        source.nationality
    )

    if country_code is None:
        raise UnsupportedNationalityError(
            f"Unsupported nationality: {source.nationality}"
        )

    return DriverCreate(
        slug=source.driver_id.replace("_", "-"),
        given_name=source.given_name,
        family_name=source.family_name,
        code=source.code,
        permanent_number=source.permanent_number,
        country_code=country_code,
        date_of_birth=source.date_of_birth,
    )