import pytest

from race_dna.metrics.overtake import (
    RaceOvertakeSample,
    calculate_overtake_index,
)


def test_full_opportunity_conversion_returns_maximum() -> None:
    result = calculate_overtake_index(
        [
            RaceOvertakeSample(
                grid_position=5,
                finish_position=1,
                status="Finished",
            )
        ]
    )

    assert result.score == 100.0
    assert result.proxy is True
    assert result.eligible_races == 1
    assert result.total_positions_gained == 4
    assert result.total_available_positions == 4


def test_metric_excludes_poles_pit_lane_and_retirements() -> None:
    samples = [
        RaceOvertakeSample(5, 3, "Finished"),
        RaceOvertakeSample(10, 8, "+1 Lap"),
        RaceOvertakeSample(1, 1, "Finished"),
        RaceOvertakeSample(0, 5, "Finished"),
        RaceOvertakeSample(6, 2, "Engine"),
    ]

    result = calculate_overtake_index(samples)
    components = {
        component.key: component
        for component in result.components
    }

    assert result.score == pytest.approx(58.46)
    assert result.sample_size == 5
    assert result.eligible_races == 2
    assert result.total_positions_gained == 4
    assert result.total_available_positions == 13
    assert (
        components["opportunity_conversion"].score
        == 30.77
    )
    assert components["gain_frequency"].score == 100.0


def test_no_position_gain_returns_zero_score() -> None:
    result = calculate_overtake_index(
        [
            RaceOvertakeSample(
                grid_position=5,
                finish_position=7,
                status="Finished",
            )
        ]
    )

    assert result.score == 0.0
    assert result.total_positions_gained == 0


def test_metric_requires_an_eligible_race() -> None:
    samples = [
        RaceOvertakeSample(1, 1, "Finished"),
        RaceOvertakeSample(5, 1, "Collision"),
    ]

    with pytest.raises(
        ValueError,
        match="At least one eligible race sample is required",
    ):
        calculate_overtake_index(samples)


def test_metric_requires_at_least_one_sample() -> None:
    with pytest.raises(
        ValueError,
        match="At least one race sample is required",
    ):
        calculate_overtake_index([])


def test_sample_rejects_negative_grid_position() -> None:
    with pytest.raises(
        ValueError,
        match="grid_position must not be negative",
    ):
        RaceOvertakeSample(-1, 1, "Finished")