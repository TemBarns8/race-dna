# Overtake Index v1.0

## Status

Experimental proxy metric.

The metric estimates recovery through net position gains. It does
not represent an official count of on-track overtakes.

## Formula

```text
Overtake Index =
0.60 * Opportunity Conversion +
0.40 * Gain Frequency
```

### Eligible races

A race is eligible when:

- the driver started from position 2 or lower;
- the grid position is greater than 0;
- the race status is `Finished` or `+N Lap(s)`.

Pole starts are excluded because there are no positions ahead.
Pit-lane starts use grid position 0 and are excluded because their
starting opportunity cannot be represented accurately.
If a season has no eligible races, the metric is unavailable.

### Opportunity Conversion

For each eligible race:

```text
positions_gained =
max(grid_position - finish_position, 0)

available_positions =
grid_position - 1
```

The season component is:

```text
opportunity_conversion =
sum(positions_gained) /
sum(available_positions) * 100
```

This component gives more weight to races with more available
positions ahead.

### Gain Frequency

```text
gain_frequency =
races with positions_gained > 0 /
eligible races * 100
```

Each eligible race has equal weight in this component.

## Final score

The final score is rounded to two decimal places and constrained
to the range from 0 to 100.

The weights are an explicit v1 product hypothesis. They must be
recalibrated when verified overtake event data becomes available.

## Transparency fields

The API must expose:

- methodology version;
- proxy status;
- final score;
- total race sample size;
- eligible race count;
- total positions gained;
- total available positions;
- component weights;
- component raw values;
- component scores.

## Limitations

- Net position gain is not an official overtake count.
- Gains caused by retirements are included.
- Pit-stop position changes are included.
- Positions gained and later lost during a race are not visible.
- Sprint results are not included.
- Retirements and pit-lane starts are excluded.
- Car competitiveness and starting position affect the score.