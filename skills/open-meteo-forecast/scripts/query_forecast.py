#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def geocode(location, expected_admin1=None):
    tried = []
    seen = set()
    all_results = []
    for candidate in geocode_candidates(location):
        tried.append(candidate)
        for result in geocode_once(candidate):
            key = (result["name"], result["latitude"], result["longitude"])
            if key in seen:
                continue
            seen.add(key)
            result["query"] = candidate
            all_results.append(result)

    if expected_admin1:
        for result in all_results:
            if result.get("admin1") == expected_admin1:
                result["tried"] = tried
                result["expected_admin1"] = expected_admin1
                return result
        raise SystemExit(
            "No geocoding result matched "
            f"admin1={expected_admin1!r} for: {location}. "
            "Use explicit --lat and --lon for this local area."
        )

    if all_results:
        result = all_results[0]
        result["tried"] = tried
        return result

    raise SystemExit(f"No geocoding result found for: {location}. Tried: {', '.join(tried)}")


def infer_admin1(location):
    mappings = {
        "北京": "北京市",
        "上海": "上海市",
        "天津": "天津市",
        "重庆": "重庆市",
    }
    for marker, admin1 in mappings.items():
        if marker in location:
            return admin1
    return None


def geocode_candidates(location):
    yield location
    normalized = location.strip()
    replacements = [
        ("北京市", ""),
        ("上海市", ""),
        ("天津市", ""),
        ("重庆市", ""),
        ("自治州", ""),
        ("地区", ""),
        ("市", ""),
        ("区", ""),
        ("县", ""),
    ]
    for old, new in replacements:
        normalized = normalized.replace(old, new)
    normalized = normalized.strip()
    if normalized and normalized != location:
        yield normalized


def geocode_once(location):
    params = {
        "name": location,
        "count": 10,
        "language": "zh",
        "format": "json",
    }
    url = GEOCODING_URL + "?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    results = data.get("results") or []
    items = []
    for result in results:
        items.append({
            "name": result.get("name") or location,
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "country": result.get("country"),
            "admin1": result.get("admin1"),
            "admin2": result.get("admin2"),
            "admin3": result.get("admin3"),
        })
    return items


def select_location(args):
    if args.location:
        expected_admin1 = args.admin1 or infer_admin1(args.location)
        geo = geocode(args.location, expected_admin1=expected_admin1)
        return geo, geo["latitude"], geo["longitude"], args.label or geo["name"]
    return None, args.lat, args.lon, args.label or f"{args.lat},{args.lon}"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Query hourly weather forecast from the Open-Meteo Forecast API."
    )
    location = parser.add_mutually_exclusive_group(required=True)
    location.add_argument("--location", help="Location name to geocode before querying.")
    location.add_argument("--lat", type=float, help="Latitude for direct coordinate query.")
    parser.add_argument("--lon", type=float, help="Longitude for direct coordinate query.")
    parser.add_argument("--label", help="Human-readable label for the query result.")
    parser.add_argument("--admin1", help="Expected first-level administrative area.")
    parser.add_argument("--hours", type=int, default=6, help="Future hours to summarize.")
    parser.add_argument("--timezone", default="auto", help="Timezone, such as Asia/Shanghai.")
    args = parser.parse_args()

    if args.lat is not None and args.lon is None:
        parser.error("--lon is required when --lat is used")
    if args.hours <= 0:
        parser.error("--hours must be greater than 0")
    return args


def main():
    args = parse_args()
    geo, lat, lon, label = select_location(args)

    hourly_fields = [
        "temperature_2m",
        "precipitation_probability",
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        "wind_speed_10m",
    ]
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(hourly_fields),
        "timezone": args.timezone,
        "forecast_days": max(1, min(16, (args.hours // 24) + 2)),
    }
    url = FORECAST_URL + "?" + urllib.parse.urlencode(params)
    data = fetch_json(url)

    timezone = data.get("timezone") or args.timezone
    tz = ZoneInfo(timezone) if timezone != "GMT" else ZoneInfo("UTC")
    now = datetime.now(tz).replace(second=0, microsecond=0)
    end = now + timedelta(hours=args.hours)

    hourly = data["hourly"]
    times = hourly["time"]
    rows = []
    for index, value in enumerate(times):
        timestamp = datetime.fromisoformat(value).replace(tzinfo=tz)
        if now < timestamp <= end:
            row = {"time": timestamp.strftime("%Y-%m-%d %H:%M")}
            for field in hourly_fields:
                values = hourly.get(field)
                row[field] = values[index] if values is not None else None
            rows.append(row)

    total_precipitation = round(
        sum((row.get("precipitation") or 0) for row in rows),
        2,
    )

    result = {
        "source": "Open-Meteo Forecast API",
        "label": label,
        "latitude": lat,
        "longitude": lon,
        "timezone": timezone,
        "window_start": now.strftime("%Y-%m-%d %H:%M"),
        "window_end": end.strftime("%Y-%m-%d %H:%M"),
        "total_precipitation_mm": total_precipitation,
        "hourly": rows,
        "geocoding": geo,
        "request_url": url,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
