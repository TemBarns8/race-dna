# Consistency Index v1.0

## Purpose

The Consistency Index measures how predictable a driver's race
results are. It does not measure outright performance or speed.

## Formula

```text
Consistency Index =
0.70 * Finish Stability +
0.30 * Completion Rate
```

### Finish Stability

Finish Stability is calculated only from completed races.

```text
median_finish = median(completed finish positions)

mean_absolute_deviation =
mean(abs(finish_position - median_finish))

finish_stability =
max(0, 100 - 10 * mean_absolute_deviation)
```

Each position of average deviation from the median reduces the
component by 10 points.

### Completion Rate

```text
completion_rate =
completed races / all races * 100
```

A race is treated as completed when its status is:

- `Finished`;
- `+1 Lap`;
- `+N Laps`.

## Final score

The final result is rounded to two decimal places and constrained
to the range from 0 to 100.

## Transparency fields

The API must expose:

- methodology version;
- final score;
- race sample size;
- completed race count;
- component weights;
- component raw values;
- component scores.

## Limitations

- Sprint results are not included.
- The metric does not account for car competitiveness.
- A consistently slow driver may still receive a high score.
- Status classification depends on the source data.
- Small and incomplete seasons have lower statistical reliability.