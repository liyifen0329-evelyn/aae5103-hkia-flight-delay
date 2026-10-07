# HKIA Flight Delay Analysis (AAE5103 Assignment 2)

Analysis of aircraft departure records from Hong Kong International Airport (HKIA),
1–18 June 2023, for Cathay Pacific (CX), HK Express (UO) and Hong Kong Airlines (HX).

## What the script does

1. Reads the 18 daily departure CSV files and merges them into one table (4,687 rows).
2. Computes `delay_min = actual departure time - scheduled departure time`.
3. Q1 – delay rate and average delay per airline (delay = actual - scheduled >= 30 min).
4. Q2 – number of delayed flights by hour of the day -> `q2_delayed_by_hour.png`.
5. Q3 – boarding gate usage frequency per airline -> `q3_gates.png`.

## How to run

```bash
pip install pandas matplotlib
python3 my_work.py
```

Run it from the folder that contains `flight_data/`.

## Data notes (why the numbers look the way they do)

- **Cancelled flights (24 rows)** have no actual departure time, so they are excluded from
  the delay statistics and reported separately.
- **71 flights departed after midnight.** Their `status` field carries a second date, e.g.
  `Dep 09:35 (03/06/2023)`. The actual timestamp must be rebuilt from that date.
  Example: CX 5820 was scheduled at 07:00 on 2 June and departed at 09:35 on 3 June —
  a true delay of 1595 minutes; subtracting the clock times only would give 155 minutes.
- **988 flights left earlier than scheduled** (earliest by 33 minutes). Negative delays are
  kept as they are, not truncated to zero.
- **12 records have no gate assignment** and are dropped in Q3 only.

## Results

| Airline | Records | Cancelled | Departed | Delayed (>=30 min) | Delay rate | Mean delay (all) | Mean delay (delayed only) |
|---|---|---|---|---|---|---|---|
| CX | 951 | 1 | 950 | 155 | 16.32% | 20.86 min | 84.57 min |
| UO | 469 | 0 | 469 | 26 | 5.54% | 6.08 min | 49.88 min |
| HX | 218 | 8 | 210 | 30 | 14.29% | 16.97 min | 91.53 min |

- Delays worsen towards the end of the day: the 21:00–23:59 block has the highest delay rate
  (48/195 = 24.6%), against 5.8% around midday.
- Gate usage reflects the business model: CX spreads 947 departures over 62 gates, while UO
  concentrates 469 departures on a small set (top five gates = 33.7% of its flights).

## Files

- `my_work.py` – the analysis script (pandas + matplotlib).
- `flight_data/depart/` – the 18 daily CSV files used (source: HKIA departure records).
- `q2_delayed_by_hour.png`, `q3_gates.png` – outputs of the script.
