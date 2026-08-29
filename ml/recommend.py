import json
import math
import re
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


USER_AGENT = "TripWise/3.0 (travel-planning prototype)"

INTEREST_ALIASES = {
    "nature": "nature landscape forest waterfall lake mountain",
    "adventure": "adventure trekking hiking rafting outdoor",
    "food": "food cuisine restaurant market street food",
    "culture": "culture heritage temple museum tradition",
    "peaceful": "peaceful quiet scenic relaxing village",
    "shopping": "shopping market bazaar mall handicraft",
    "beach": "beach coast sea island waterfront",
    "photography": "photography scenic viewpoint architecture landscape",
    "snow": "snow winter skiing glacier mountain",
    "history": "history fort palace monument historic heritage",
}


def _request_json(url, timeout=12):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _slug(value):
    return urllib.parse.quote(str(value).replace(" ", "_"), safe="")


@lru_cache(maxsize=256)
def geocode_destination(query):
    params = urllib.parse.urlencode(
        {
            "name": query,
            "count": 5,
            "language": "en",
            "format": "json",
        }
    )
    data = _request_json(
        f"https://geocoding-api.open-meteo.com/v1/search?{params}"
    )
    return data.get("results", [])


@lru_cache(maxsize=256)
def wikipedia_search(query):
    params = urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 12,
            "format": "json",
            "utf8": 1,
        }
    )
    data = _request_json(
        f"https://en.wikipedia.org/w/api.php?{params}"
    )
    return data.get("query", {}).get("search", [])


@lru_cache(maxsize=512)
def wikipedia_summary(title):
    try:
        data = _request_json(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{_slug(title)}"
        )
    except Exception:
        return None

    if data.get("type") == "disambiguation":
        return None

    thumbnail = data.get("thumbnail") or {}
    return {
        "name": _clean_text(data.get("title") or title),
        "description": _clean_text(
            data.get("extract")
            or data.get("description")
            or "Information is available from the destination reference source."
        ),
        "image": thumbnail.get("source"),
        "url": (data.get("content_urls") or {}).get("desktop", {}).get("page"),
        "coordinates": data.get("coordinates") or [],
    }


def _match_score(query, candidate):
    a = re.sub(r"[^a-z0-9]", "", query.lower())
    b = re.sub(r"[^a-z0-9]", "", candidate.lower())
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio() * 100


def resolve_destination(query):
    original = _clean_text(query)
    if not original:
        raise ValueError("Destination is required.")

    geocode_results = []
    try:
        geocode_results = geocode_destination(original)
    except Exception:
        geocode_results = []

    if geocode_results:
        best = geocode_results[0]
        name = _clean_text(best.get("name")) or original
        country = _clean_text(best.get("country"))
        display_name = f"{name}, {country}" if country else name
        confidence = _match_score(original, name)
        return {
            "input": original,
            "name": name,
            "display_name": display_name,
            "country": country,
            "latitude": best.get("latitude"),
            "longitude": best.get("longitude"),
            "timezone": best.get("timezone"),
            "corrected": name.lower() != original.lower(),
            "correction_confidence": round(confidence, 1),
        }

    searches = []
    for search_query in [original, f"{original} travel", f"{original} tourist attractions"]:
        try:
            searches.extend(wikipedia_search(search_query))
        except Exception:
            continue

    candidates = []
    seen = set()
    for item in searches:
        title = _clean_text(item.get("title"))
        if not title or title.lower() in seen:
            continue
        seen.add(title.lower())
        candidates.append(title)

    if not candidates:
        raise ValueError(
            "I could not identify this destination. Check the spelling and try a city, region or country name."
        )

    scored = sorted(
        ((candidate, _match_score(original, candidate)) for candidate in candidates),
        key=lambda item: item[1],
        reverse=True,
    )
    candidate, score = scored[0]
    if score < 45:
        raise ValueError(
            "I could not confidently identify this destination. Check the spelling and try again."
        )

    summary = wikipedia_summary(candidate)
    coordinates = (summary or {}).get("coordinates") or []
    latitude = coordinates[0].get("lat") if coordinates else None
    longitude = coordinates[0].get("lon") if coordinates else None

    if latitude is None or longitude is None:
        try:
            fallback = geocode_destination(candidate)
            if fallback:
                latitude = fallback[0].get("latitude")
                longitude = fallback[0].get("longitude")
        except Exception:
            pass

    return {
        "input": original,
        "name": candidate,
        "display_name": candidate,
        "country": "",
        "latitude": latitude,
        "longitude": longitude,
        "timezone": None,
        "corrected": candidate.lower() != original.lower(),
        "correction_confidence": round(score, 1),
    }


def _interest_text(interests):
    tokens = [x.strip().lower() for x in str(interests or "").split(",") if x.strip()]
    expanded = []
    for token in tokens:
        expanded.append(INTEREST_ALIASES.get(token, token))
    return " ".join(expanded) or "nature sightseeing culture food"


def _search_place_candidates(destination_name, interests):
    queries = [
        f"{destination_name} tourist attractions",
        f"{destination_name} places to visit",
    ]
    for interest in [x.strip().lower() for x in str(interests or "").split(",") if x.strip()][:4]:
        queries.append(f"{destination_name} {interest}")

    candidates = []
    seen = set()
    destination_key = destination_name.lower()
    for query in queries:
        try:
            results = wikipedia_search(query)
        except Exception:
            continue
        for item in results:
            title = _clean_text(item.get("title"))
            if not title or title.lower() in seen or title.lower() == destination_key:
                continue
            seen.add(title.lower())
            candidates.append(title)
    return candidates[:30]


def recommend_places(destination_name, interests, limit=8):
    candidates = _search_place_candidates(destination_name, interests)
    documents = []
    records = []
    interest_text = _interest_text(interests)

    for title in candidates:
        summary = wikipedia_summary(title)
        if not summary:
            continue
        text = f"{summary['name']} {summary['description']}"
        records.append(summary)
        documents.append(text)

    if not records:
        return []

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(documents + [interest_text])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    ranked = sorted(
        zip(records, scores),
        key=lambda pair: pair[1],
        reverse=True,
    )

    places = []
    for record, score in ranked[:limit]:
        places.append(
            {
                "name": record["name"],
                "description": record["description"],
                "match_score": round(float(score) * 100, 1),
                "tags": [
                    token
                    for token in str(interests or "").split(",")
                    if token.strip()
                ],
                "image": record.get("image"),
                "url": record.get("url"),
            }
        )
    return places


def _month_name(month):
    return [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ][month - 1]


def _season_label(months):
    if not months:
        return "Weather data unavailable"
    names = [_month_name(m) for m in months]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{names[0]} to {names[-1]}"


@lru_cache(maxsize=128)
def historical_weather(latitude, longitude):
    if latitude is None or longitude is None:
        return None

    params = urllib.parse.urlencode(
        {
            "latitude": round(float(latitude), 4),
            "longitude": round(float(longitude), 4),
            "start_date": "2016-01-01",
            "end_date": "2025-12-31",
            "daily": "temperature_2m_mean,precipitation_sum,snowfall_sum",
            "timezone": "auto",
        }
    )
    try:
        return _request_json(
            f"https://archive-api.open-meteo.com/v1/archive?{params}",
            timeout=20,
        )
    except Exception:
        return None


def best_time_from_weather(latitude, longitude):
    data = historical_weather(latitude, longitude)
    if not data:
        return {
            "best_time": "Weather history unavailable",
            "best_time_note": "Live destination data was found, but historical weather data could not be retrieved right now.",
            "weather": {},
        }

    daily = data.get("daily") or {}
    dates = daily.get("time") or []
    temps = daily.get("temperature_2m_mean") or []
    rain = daily.get("precipitation_sum") or []
    snow = daily.get("snowfall_sum") or []
    buckets = {m: {"temps": [], "rain": [], "snow": []} for m in range(1, 13)}

    for index, date in enumerate(dates):
        try:
            month = int(date[5:7])
        except Exception:
            continue
        if month not in buckets:
            continue
        if index < len(temps) and temps[index] is not None:
            buckets[month]["temps"].append(float(temps[index]))
        if index < len(rain) and rain[index] is not None:
            buckets[month]["rain"].append(float(rain[index]))
        if index < len(snow) and snow[index] is not None:
            buckets[month]["snow"].append(float(snow[index]))

    stats = []
    for month, bucket in buckets.items():
        if not bucket["temps"]:
            continue
        avg_temp = float(np.mean(bucket["temps"]))
        avg_rain = float(np.mean(bucket["rain"])) if bucket["rain"] else 0.0
        avg_snow = float(np.mean(bucket["snow"])) if bucket["snow"] else 0.0
        comfort = max(0.0, 1.0 - abs(avg_temp - 22.0) / 25.0)
        rain_factor = 1.0 / (1.0 + avg_rain / 5.0)
        snow_penalty = 0.25 if avg_snow > 5 else 0.0
        score = comfort * 0.55 + rain_factor * 0.45 - snow_penalty
        stats.append((month, score, avg_temp, avg_rain, avg_snow))

    if not stats:
        return {
            "best_time": "Weather history unavailable",
            "best_time_note": "Historical weather data did not contain enough observations to calculate a reliable travel window.",
            "weather": {},
        }

    stats.sort(key=lambda item: item[1], reverse=True)
    selected = sorted(item[0] for item in stats[:4])
    top = [item for item in stats if item[0] in selected]
    average_temp = float(np.mean([item[2] for item in top]))
    average_rain = float(np.mean([item[3] for item in top]))

    return {
        "best_time": _season_label(selected),
        "best_time_note": (
            f"This window is selected from 10 years of historical temperature and precipitation patterns. "
            f"The selected months average about {average_temp:.0f}°C with roughly {average_rain:.1f} mm of precipitation per day."
        ),
        "weather": {
            "average_temperature": round(average_temp, 1),
            "average_precipitation": round(average_rain, 1),
            "selected_months": selected,
        },
    }


def build_dynamic_risks(summary_text, weather, latitude=None):
    text = str(summary_text or "").lower()
    risks = []

    avg_rain = float(weather.get("average_precipitation", 0) or 0)
    avg_temp = float(weather.get("average_temperature", 22) or 22)

    if avg_rain >= 6:
        risks.append((
            "Heavy rainfall",
            "high",
            "Wet conditions can affect roads, trails, visibility and outdoor activities during rainy periods.",
        ))
    elif avg_rain >= 3:
        risks.append((
            "Rain and slippery surfaces",
            "moderate",
            "Rain can make outdoor paths and roads slippery and may disrupt some activities.",
        ))

    if avg_temp >= 30:
        risks.append((
            "Heat and dehydration",
            "high",
            "Hot weather can increase dehydration and heat-exposure risk during sightseeing and outdoor activities.",
        ))
    elif avg_temp >= 26:
        risks.append((
            "Heat exposure",
            "moderate",
            "Warm conditions can make long outdoor sightseeing sessions tiring without adequate hydration and shade.",
        ))

    if avg_temp <= 5:
        risks.append((
            "Cold weather",
            "high",
            "Low temperatures can require suitable clothing and can affect outdoor comfort and transport.",
        ))
    elif avg_temp <= 12:
        risks.append((
            "Cold conditions",
            "moderate",
            "Cool weather may require warm clothing, especially for early-morning and evening activities.",
        ))

    if "mountain" in text or "himalaya" in text or "high-altitude" in text:
        risks.append((
            "Altitude and mountain travel",
            "moderate",
            "Mountain destinations can involve altitude changes, winding roads and physically demanding excursions.",
        ))

    if any(word in text for word in ["trek", "hiking", "trail", "climb"]):
        risks.append((
            "Trekking and terrain",
            "moderate",
            "Trails and uneven terrain can cause fatigue or falls; conditions may change with weather.",
        ))

    if any(word in text for word in ["coast", "beach", "sea", "island", "ocean"]):
        risks.append((
            "Sea and water conditions",
            "moderate",
            "Swimming and water activities depend on local currents, waves, weather and operator guidance.",
        ))

    if any(word in text for word in ["desert", "arid"]):
        risks.append((
            "Dry conditions",
            "moderate",
            "Dry environments can increase dehydration and heat exposure, particularly during daytime excursions.",
        ))

    risks.append((
        "Local transport and access",
        "low",
        "Travel time and accessibility can change because of traffic, local conditions, closures or seasonal disruption.",
    ))

    unique = []
    seen = set()
    for risk in risks:
        if risk[0] not in seen:
            seen.add(risk[0])
            unique.append(risk)
    return unique
