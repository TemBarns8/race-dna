from datetime import date

from race_dna.integrations.jolpica.schemas import (
    JolpicaDriverResponse,
)


def test_jolpica_driver_response_is_parsed() -> None:
    payload = {
        "MRData": {
            "DriverTable": {
                "Drivers": [
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
                        "nationality": "Dutch",
                    }
                ]
            }
        }
    }

    response = JolpicaDriverResponse.model_validate(payload)
    driver = response.mr_data.driver_table.drivers[0]

    assert driver.driver_id == "max_verstappen"
    assert driver.permanent_number == 3
    assert driver.date_of_birth == date(1997, 9, 30)