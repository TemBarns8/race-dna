from race_dna.integrations.jolpica.qualifying_results import (
    JolpicaQualifyingResponse,
)


def test_jolpica_qualifying_result_is_parsed() -> None:
    payload = {
        "MRData": {
            "limit": "1",
            "offset": "0",
            "total": "241",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2015",
                        "round": "1",
                        "raceName": "Australian Grand Prix",
                        "Circuit": {
                            "circuitId": "albert_park",
                            "circuitName": (
                                "Albert Park Grand Prix Circuit"
                            ),
                            "Location": {
                                "locality": "Melbourne",
                                "country": "Australia",
                            },
                        },
                        "date": "2015-03-15",
                        "QualifyingResults": [
                            {
                                "number": "33",
                                "position": "12",
                                "Driver": {
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
                                },
                                "Constructor": {
                                    "constructorId": "toro_rosso",
                                    "name": "Toro Rosso",
                                    "nationality": "Italian",
                                },
                                "Q1": "1:29.248",
                                "Q2": "1:28.868",
                            }
                        ],
                    }
                ]
            },
        }
    }

    parsed = JolpicaQualifyingResponse.model_validate(payload)
    race = parsed.mr_data.race_table.races[0]
    result = race.qualifying_results[0]

    assert parsed.mr_data.total == 241
    assert race.season == 2015
    assert race.round == 1
    assert result.position == 12
    assert result.q1 == "1:29.248"
    assert result.q2 == "1:28.868"
    assert result.q3 is None