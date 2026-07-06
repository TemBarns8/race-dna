from collections.abc import Sequence
from dataclasses import dataclass

from race_dna.metrics.consistency import (
    MetricComponent,
    is_completed_status,
)


@dataclass(frozen=True)
class RaceOvertakeSample:
    grid_position: int
    finish_position: int
    status: str

    def __post_init__(self) -> None:
        if self.grid_position < 0:
            raise ValueError(
                "grid_position must not be negative."
            )
        if self.finish_position < 1:
            raise ValueError(
                "finish_position must be positive."
            )
        if not self.status.strip():
            raise ValueError("status must not be empty.")


@dataclass(frozen=True)
class OvertakeIndexResult:
    metric: str
    methodology_version: str
    proxy: bool
    score: float
    sample_size: int
    eligible_races: int
    total_positions_gained: int
    total_available_positions: int
    components: tuple[MetricComponent, ...]


def calculate_overtake_index(
    samples: Sequence[RaceOvertakeSample],
) -> OvertakeIndexResult:
    if not samples:
        raise ValueError(
            "At least one race sample is required."
        )

    eligible_samples = [
        sample
        for sample in samples
        if sample.grid_position > 1
        and is_completed_status(sample.status)
    ]

    if not eligible_samples:
        raise ValueError(
            "At least one eligible race sample is required."
        )

    positions_gained = [
        max(
            sample.grid_position - sample.finish_position,
            0,
        )
        for sample in eligible_samples
    ]
    available_positions = [
        sample.grid_position - 1
        for sample in eligible_samples
    ]

    total_positions_gained = sum(positions_gained)
    total_available_positions = sum(available_positions)

    opportunity_conversion = (
        total_positions_gained
        / total_available_positions
        * 100.0
    )
    gain_frequency = (
        sum(gain > 0 for gain in positions_gained)
        / len(eligible_samples)
        * 100.0
    )

    final_score = (
        0.60 * opportunity_conversion
        + 0.40 * gain_frequency
    )
    final_score = min(100.0, max(0.0, final_score))

    return OvertakeIndexResult(
        metric="overtake_index",
        methodology_version="1.0",
        proxy=True,
        score=round(final_score, 2),
        sample_size=len(samples),
        eligible_races=len(eligible_samples),
        total_positions_gained=total_positions_gained,
        total_available_positions=total_available_positions,
        components=(
            MetricComponent(
                key="opportunity_conversion",
                weight=0.60,
                raw_value=round(
                    opportunity_conversion,
                    2,
                ),
                score=round(opportunity_conversion, 2),
            ),
            MetricComponent(
                key="gain_frequency",
                weight=0.40,
                raw_value=round(gain_frequency, 2),
                score=round(gain_frequency, 2),
            ),
        ),
    )