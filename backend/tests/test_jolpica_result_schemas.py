from decimal import Decimal

from race_dna.integrations.jolpica.race_results import (
    JolpicaRaceResultsResponse,
)


def test_jolpica_race_result_is_parsed() -> None:
    payload = {
        "MRData": {
            "limit": "100",
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
                        "Results": [
                            {
                                "number": "33",
                                "position": "13",
                                "positionText": "R",
                                "points": "0",
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
                                "grid": "11",
                                "laps": "32",
                                "status": "Engine",
                            }
                        ],
                    }
                ]
            },
        }
    }

    parsed = JolpicaRaceResultsResponse.model_validate(payload)
    race = parsed.mr_data.race_table.races[0]
    result = race.results[0]

    assert parsed.mr_data.total == 241
    assert race.season == 2015
    assert race.round == 1
    assert result.position == 13
    assert result.grid == 11
    assert result.points == Decimal("0")