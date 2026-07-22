---
name: open-meteo-forecast
description: Query weather forecasts with the unauthenticated Open-Meteo Forecast API. Use for hourly or daily weather data such as temperature, precipitation, precipitation probability, and wind speed by coordinates or location; do not use for tasks requiring a commercial SLA, official weather alerts, or another specified weather provider.
---

# Open-Meteo Forecast

- The free Forecast API does not require an `API key`; request `https://api.open-meteo.com/v1/forecast` directly
- For commercial use, high request volume, or high reliability requirements, remind the user to review Open-Meteo's terms and paid plans
- Prefer coordinate-based queries. Use the Open-Meteo Geocoding API only when the user provides a location name without coordinates
- Do not rely only on a city-center point for local weather. Query each district, street, or user-provided coordinate separately
- The Open-Meteo Geocoding API may have incomplete coverage of Chinese district names. If a place name does not match the target administrative area, use explicit coordinates
- Every answer must state the data source, coordinates, timezone, time window, and units

## Workflow

1. Determine the location, time window, and metrics the user wants, such as `<next 6 hours>`, `<next 3 days>`, `<precipitation amount>`, or `<precipitation probability>`
2. Obtain coordinates:
   - Existing coordinates: use `latitude` and `longitude` directly
   - Location name only: request `https://geocoding-api.open-meteo.com/v1/search?name={location}&count=10&language=zh&format=json`
   - If the location is ambiguous, missing, or matched to the wrong administrative area, confirm with the user or use coordinates
3. Request the Forecast API:
   - Hourly: use `hourly=temperature_2m,precipitation_probability,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m`
   - Daily: use `daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code`
   - Use `timezone={timezone}` and default to the user's timezone or the target location's timezone
4. Parse the results:
   - `precipitation`, `rain`, and `showers` are usually measured in `mm`
   - `snowfall` is usually measured in `cm`
   - `precipitation_probability` is measured in `%`
   - For the next `<N>` hours, select hourly records after the current time and within the N-hour window, then calculate cumulative precipitation
5. Present the conclusion:
   - Lead with the cumulative value and risk assessment, followed by hourly details
   - Distinguish between "forecast precipitation" and "precipitation probability"
   - Explain that this is a model forecast, not real-time radar or an official alert

## Reusable script

Use [@skills/open-meteo-forecast/scripts/query_forecast.py](/skills/open-meteo-forecast/scripts/query_forecast.py) to query hourly forecasts.

Query by coordinates:

```bash
python3 skills/open-meteo-forecast/scripts/query_forecast.py \
  --label "北京市朝阳区" \
  --lat 39.9219 \
  --lon 116.4435 \
  --hours 6 \
  --timezone Asia/Shanghai
```

Query by location name. Check that `geocoding.admin1`, `latitude`, and `longitude` in the output match the expected location:

```bash
python3 skills/open-meteo-forecast/scripts/query_forecast.py \
  --location "北京市海淀区" \
  --hours 6 \
  --timezone Asia/Shanghai
```

Filter by first-level administrative area:

```bash
python3 skills/open-meteo-forecast/scripts/query_forecast.py \
  --location "海淀" \
  --admin1 "北京市" \
  --hours 6 \
  --timezone Asia/Shanghai
```

The output is JSON. Key fields:

| Field | Description |
|---|---|
| `label` | Query location label |
| `latitude` / `longitude` | Coordinates actually used |
| `timezone` | Result timezone |
| `window_start` / `window_end` | Statistical window |
| `total_precipitation_mm` | Cumulative forecast precipitation within the window |
| `hourly[]` | Hourly precipitation, precipitation probability, temperature, wind speed, and other data |

## API examples

Precipitation for the next 6 hours:

```text
https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation,precipitation_probability,rain,showers&timezone={timezone}&forecast_days=2
```

Daily forecast for the next 3 days:

```text
https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min,weather_code&timezone={timezone}&forecast_days=3
```

## GWT examples

| Given | When | Then |
|---|---|---|
| The user asks, "How much rain will Chaoyang District, Beijing, receive in the next 6 hours?" | Query hourly `precipitation` using the place name or district-center coordinates | Return cumulative precipitation over 6 hours, hourly details, precipitation probability, and coordinates |
| The user asks, "Which Beijing districts will receive more rain over the next 3 days?" | Query coordinates and daily `precipitation_sum` separately for each district | Compare cumulative precipitation over 3 days by district in a table and explain the confidence of the differences |
| The user provides only "Beijing" | Use city-center coordinates or ask whether to query a specific district | Do not present city-center results as representative of every local area in the city |
