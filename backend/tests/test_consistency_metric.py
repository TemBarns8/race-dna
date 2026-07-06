import pytest

from race_dna.metrics.consistency import (
    RaceConsistencySample,
    calculate_consistency_index,
    is_completed_status,
)


def test_perfect_consistency_returns_maximum_score() -> None:
    samples = [
        RaceConsistencySample(1, "Finished"),
        RaceConsistencySample(1, "+1 Lap"),
        RaceConsistencySample(1, "+2 Laps"),
    ]

    result = calculate_consistency_index(samples)
    components = {
        component.key: component
        for component in result.components
    }

    assert result.metric == "consistency_index"
    assert result.methodology_version == "1.0"
    assert result.score == 100.0
    assert result.sample_size == 3
    assert result.completed_races == 3
    assert result.median_finish == 1.0
    assert components["finish_stability"].score == 100.0
    assert components["completion_rate"].score == 100.0


def test_retirement_reduces_completion_component() -> None:
    samples = [
        RaceConsistencySample(1, "Finished"),
        RaceConsistencySample(2, "+1 Lap"),
        RaceConsistencySample(20, "Engine"),
    ]

    result = calculate_consistency_index(samples)
    components = {
        component.key: component
        for component in result.components
    }

    assert result.score == pytest.approx(86.5)
    assert result.completed_races == 2
    assert result.median_finish == 1.5
    assert components["finish_stability"].raw_value == 0.5
    assert components["finish_stability"].score == 95.0
    assert components["completion_rate"].score == 66.67


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("Finished", True),
        ("+1 Lap", True),
        ("+2 Laps", True),
        ("Engine", False),
        ("Collision", False),
    ],
)
def test_completed_status_classification(
    status: str,
    expected: bool,
) -> None:
    assert is_completed_status(status) is expected


def test_metric_requires_at_least_one_sample() -> None:
    with pytest.raises(
        ValueError,
        match="At least one race sample is required",
    ):
        calculate_consistency_index([])


def test_sample_rejects_invalid_finish_position() -> None:
    with pytest.raises(
        ValueError,
        match="finish_position must be positive",
    ):
        RaceConsistencySample(0, "Finished")