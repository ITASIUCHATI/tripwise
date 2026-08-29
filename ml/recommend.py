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

USER_AGENT = "TripWise/4.0 (travel-planning prototype)"

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
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _clean_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _slug(value):
    return urllib.parse.quote(str(value).replace(" ", "_"), safe="")


def _normalise_geo(item):
    name = _clean_text(item.get("name"))
    admin1 = _clean_text(item.get("admin1"))
    country = _clean_text(item.get("country"))
    parts = [part for part in [name, admin1, country] if part]
    display_name = ", ".join(dict.fromkeys(parts))
    return {
        "name": name,
        "admin1": admin1,
        "country": country,
        "country_code": _clean_text(item.get("country_code")),
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
        "timezone": item.get("timezone"),
        "population": item.get("population"),
        "feature_code": _clean_text(item.get("feature_code")),
        "display_name": display_name or name,
    }


@lru_cache(maxsize=256)
def geocode_destination(query):
    params = urllib.parse.urlencode(
        {
            "name": query,
            "count": 10,
            "language": "en",
            "format": "json",
        }
    )
    data = _request_json(f"https://geocoding-api.open-meteo.com/v1/search?{params}")
    return [_normalise_geo(item) for item in data.get("results", [])]


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
    data = _request_json(f"https://en.wikipedia.org/w/api.php?{params}")
    return data.get("query", {}).get("search", [])


@lru_cache(maxsize=256)
def wikipedia_opensearch(query):
    params = urllib.parse.urlencode(
        {
            "action": "opensearch",
            "search": query,
            "limit": 10,
            "namespace": 0,
            "format": "json",
        }
    )
    data = _request_json(f"https://en.wikipedia.org/w/api.php?{params}")
    return data[1] if isinstance(data, list) and len(data) > 1 else []


@lru_cache(maxsize=256)
def wikidata_search(query):
    params = urllib.parse.urlencode(
        {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "limit": 10,
            "format": "json",
        }
    )
    data = _request_json(f"https://www.wikidata.org/w/api.php?{params}")
    results = []
    for item in data.get("search", []):
        label = _clean_text(item.get("label"))
        description = _clean_text(item.get("description"))
        if label:
            results.append({"label": label, "description": description})
    return results


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


def _dedupe_locations(locations):
    unique = []
    seen = set()
    for item in locations:
        key = (
            item.get("name", "").lower(),
            item.get("admin1", "").lower(),
            item.get("country", "").lower(),
        )
        if not key[0] or key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _fuzzy_location_candidates(query):
    candidates = []
    seen = set()

    def add(value, source_score):
        value = _clean_text(value)
        if not value or value.lower() in seen:
            return
        seen.add(value.lower())
        candidates.append((value, source_score))

    try:
        for item in wikidata_search(query):
            add(item.get("label"), 1.0)
    except Exception:
        pass

    for search_query in [query, f"{query} travel", f"{query} city", f"{query} tourist"]:
        try:
            for item in wikipedia_search(search_query):
                add(item.get("title"), 0.8)
        except Exception:
            pass

    try:
        for title in wikipedia_opensearch(query):
            add(title, 0.9)
    except Exception:
        pass

    scored = []
    for candidate, source_score in candidates:
        raw = _match_score(query, candidate)
        score = min(100.0, raw + source_score * 2.0)
        if raw >= 45:
            scored.append((candidate, score, raw))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:8]


def search_destination_options(query):
    original = _clean_text(query)
    if not original:
        return []

    try:
        direct = geocode_destination(original)
    except Exception:
        direct = []

    if direct:
        exact = [item for item in direct if item["name"].lower() == original.lower()]
        if exact:
            return _dedupe_locations(exact + [item for item in direct if item not in exact])[:8]
        return _dedupe_locations(direct)[:8]

    locations = []
    for candidate, score, raw in _fuzzy_location_candidates(original):
        try:
            geocoded = geocode_destination(candidate)
        except Exception:
            geocoded = []
        for location in geocoded[:4]:
            location["correction_score"] = round(min(100.0, score), 1)
            location["raw_match_score"] = round(raw, 1)
            locations.append(location)

    return _dedupe_locations(locations)[:8]


def _selected_location(value):
    if not isinstance(value, dict):
        return None
    name = _clean_text(value.get("name"))
    latitude = value.get("latitude")
    longitude = value.get("longitude")
    if not name or latitude is None or longitude is None:
        return None
    return {
        "name": name,
        "admin1": _clean_text(value.get("admin1")),
        "country": _clean_text(value.get("country")),
        "country_code": _clean_text(value.get("country_code")),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "timezone": _clean_text(value.get("timezone")),
        "display_name": _clean_text(value.get("display_name")) or name,
    }


def resolve_destination(query, selected=None, require_unique=False):
    original = _clean_text(query)
    if not original:
        raise ValueError("Destination is required.")

    selected_location = _selected_location(selected)
    if selected_location:
        return {
            "input": original,
            **selected_location,
            "corrected": selected_location["name"].lower() != original.lower(),
            "correction_confidence": float(selected.get("correction_score") or 100),
        }

    options = search_destination_options(original)
    if not options:
        raise ValueError(
            "I could not identify this destination. Check the spelling and try a city, region or country name."
        )

    if require_unique and len(options) > 1:
        raise ValueError("Please choose the destination from the suggestions so TripWise uses the correct location.")

    best = options[0]
    confidence = _match_score(original, best["name"])
    return {
        "input": original,
        **best,
        "corrected": best["name"].lower() != original.lower(),
        "correction_confidence": round(float(best.get("correction_score") or confidence), 1),
    }


def _interest_text(interests):
    tokens = [x.strip().lower() for x in str(interests or "").split(",") if x.strip()]
    return " ".join(INTEREST_ALIASES.get(token, token) for token in tokens) or "nature sightseeing culture food"


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


def recommend_places(destination_name, interests, limit=6):
    candidates = _search_place_candidates(destination_name, interests)
    documents = []
    records = []
    interest_text = _interest_text(interests)

    for title in candidates:
        summary = wikipedia_summary(title)
        if not summary:
            continue
        records.append(summary)
        documents.append(f"{summary['name']} {summary['description']}")

    if not records:
        return []

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(documents + [interest_text])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    ranked = sorted(zip(records, scores), key=lambda pair: pair[1], reverse=True)

    places = []
    for record, score in ranked[:limit]:
        places.append(
            {
                "name": record["name"],
                "description": record["description"],
                "match_score": round(float(score) * 100, 1),
                "tags": [token.strip() for token in str(interests or "").split(",") if token.strip()],
                "url": record.get("url"),
            }
        )
    return places


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
        return _request_json(f"https://archive-api.open-meteo.com/v1/archive?{params}", timeout=20)
    except Exception:
        return None


def _month_name(month):
    return ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][month - 1]


def _season_label(months):
    if not months:
        return "Weather data unavailable"
    names = [_month_name(m) for m in months]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{names[0]} to {names[-1]}"


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
        "best_time_note": f"This window is selected from 10 years of historical temperature and precipitation patterns. The selected months average about {average_temp:.0f}°C with roughly {average_rain:.1f} mm of precipitation per day.",
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
        risks.append(("Heavy rainfall", "high", "Wet conditions can affect roads, trails, visibility and outdoor activities during rainy periods."))
    elif avg_rain >= 3:
        risks.append(("Rain and slippery surfaces", "moderate", "Rain can make outdoor paths and roads slippery and may disrupt some activities."))
    if avg_temp >= 30:
        risks.append(("Heat and dehydration", "high", "Hot weather can increase dehydration and heat-exposure risk during sightseeing and outdoor activities."))
    elif avg_temp >= 26:
        risks.append(("Heat exposure", "moderate", "Warm conditions can make long outdoor sightseeing sessions tiring without adequate hydration and shade."))
    if avg_temp <= 5:
        risks.append(("Cold weather", "high", "Low temperatures can require suitable clothing and can affect outdoor comfort and transport."))
    elif avg_temp <= 12:
        risks.append(("Cold conditions", "moderate", "Cool weather may require warm clothing, especially for early-morning and evening activities."))
    if any(word in text for word in ["mountain", "himalaya", "high-altitude"]):
        risks.append(("Altitude and mountain travel", "moderate", "Mountain destinations can involve altitude changes, winding roads and physically demanding excursions."))
    if any(word in text for word in ["trek", "hiking", "trail", "climb"]):
        risks.append(("Trekking and terrain", "moderate", "Trails and uneven terrain can cause fatigue or falls; conditions may change with weather."))
    if any(word in text for word in ["coast", "beach", "sea", "island", "ocean"]):
        risks.append(("Sea and water conditions", "moderate", "Swimming and water activities depend on local currents, waves, weather and operator guidance."))
    if any(word in text for word in ["desert", "arid"]):
        risks.append(("Dry conditions", "moderate", "Dry environments can increase dehydration and heat exposure, particularly during daytime excursions."))
    risks.append(("Local transport and access", "low", "Travel time and accessibility can change because of traffic, local conditions, closures or seasonal disruption."))

    unique = []
    seen = set()
    for risk in risks:
        if risk[0] not in seen:
            seen.add(risk[0])
            unique.append(risk)
    return unique


def haversine_km(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return None
    radius = 6371.0
    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))
    dp = math.radians(float(lat2) - float(lat1))
    dl = math.radians(float(lon2) - float(lon1))
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
