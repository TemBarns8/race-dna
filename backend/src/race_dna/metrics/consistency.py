import re
from collections.abc import Sequence
from dataclasses import dataclass
from statistics import fmean, median


@dataclass(frozen=True)
class RaceConsistencySample:
    finish_position: int
    status: str

    def __post_init__(self) -> None:
        if self.finish_position < 1:
            raise ValueError(
                "finish_position must be positive."
            )
        if not self.status.strip():
            raise ValueError("status must not be empty.")


@dataclass(frozen=True)
class MetricComponent:
    key: str
    weight: float
    raw_value: float | None
    score: float


@dataclass(frozen=True)
class ConsistencyIndexResult:
    metric: str
    methodology_version: str
    score: float
    sample_size: int
    completed_races: int
    median_finish: float | None
    components: tuple[MetricComponent, ...]


def is_completed_status(status: str) -> bool:
    normalized_status = status.strip()

    return (
        normalized_status == "Finished"
        or re.fullmatch(
            r"\+\d+\s+Laps?",
            normalized_status,
        )
        is not None
    )


def calculate_consistency_index(
    samples: Sequence[RaceConsistencySample],
) -> ConsistencyIndexResult:
    if not samples:
        raise ValueError(
            "At least one race sample is required."
        )

    completed_samples = [
        sample
        for sample in samples
        if is_completed_status(sample.status)
    ]

    if completed_samples:
        positions = [
            sample.finish_position
            for sample in completed_samples
        ]
        median_finish = float(median(positions))
        mean_absolute_deviation = fmean(
            abs(position - median_finish)
            for position in positions
        )
        finish_stability = max(
            0.0,
            100.0 - 10.0 * mean_absolute_deviation,
        )
    else:
        median_finish = None
        mean_absolute_deviation = None
        finish_stability = 0.0

    completion_rate = (
        len(completed_samples) / len(samples) * 100.0
    )

    final_score = (
        0.70 * finish_stability
        + 0.30 * completion_rate
    )
    final_score = min(100.0, max(0.0, final_score))

    return ConsistencyIndexResult(
        metric="consistency_index",
        methodology_version="1.0",
        score=round(final_score, 2),
        sample_size=len(samples),
        completed_races=len(completed_samples),
        median_finish=median_finish,
        components=(
            MetricComponent(
                key="finish_stability",
                weight=0.70,
                raw_value=(
                    round(mean_absolute_deviation, 2)
                    if mean_absolute_deviation is not None
                    else None
                ),
                score=round(finish_stability, 2),
            ),
            MetricComponent(
                key="completion_rate",
                weight=0.30,
                raw_value=round(completion_rate, 2),
                score=round(completion_rate, 2),
            ),
        ),
    )