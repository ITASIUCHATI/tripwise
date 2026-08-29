import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from recommend import (
    INTEREST_ALIASES,
    best_time_from_weather,
    build_dynamic_risks,
    haversine_km,
    recommend_places,
    resolve_destination,
    wikipedia_summary,
)

INTERESTS = list(INTEREST_ALIASES.keys())


def interest_flags(interests):
    text = str(interests or "").lower()
    return [1 if interest in text else 0 for interest in INTERESTS]


rng = np.random.default_rng(42)
TRAIN_X = []
TRAIN_Y = []
RISK_X = []
RISK_Y = []

for _ in range(22000):
    days = int(rng.integers(1, 31))
    people = int(rng.integers(1, 11))
    distance_km = float(rng.uniform(5, 6000))
    latitude = float(rng.uniform(-55, 70))
    rain = float(rng.uniform(0, 15))
    temp = float(rng.uniform(-5, 35))
    flags = rng.integers(0, 2, size=len(INTERESTS)).tolist()

    international_index = 1.18 if distance_km > 2500 else 1.0
    climate_factor = 1 + max(0, abs(temp - 22) - 8) * 0.008
    interest_factor = 1 + flags[1] * 0.04 + flags[2] * 0.025 + flags[5] * 0.015
    transport = 1800 + distance_km * 4.2 * (1.35 if distance_km > 1500 else 1.0)
    stay_food = 2800 + 1150 * days + 850 * people * days + 1200 * max(people - 1, 0)
    activities = 600 * days * (1 + 0.18 * flags[1] + 0.08 * flags[7])
    cost = (transport + stay_food + activities) * international_index * climate_factor * interest_factor

    features = [days, people, distance_km, latitude, rain, temp, *flags]
    TRAIN_X.append(features)
    TRAIN_Y.append(cost)

    pressure = 0
    pressure += 2 if rain > 7 else 1 if rain > 3 else 0
    pressure += 2 if temp >= 32 or temp <= 2 else 1 if temp >= 28 or temp <= 10 else 0
    pressure += 1 if days > 10 else 0
    pressure += 1 if people > 6 else 0
    pressure += 1 if flags[1] else 0
    pressure += 1 if flags[7] else 0
    pressure += 1 if distance_km > 2500 else 0
    RISK_X.append(features)
    RISK_Y.append(int(pressure >= 3))

cost_model = RandomForestRegressor(
    n_estimators=280,
    random_state=42,
    min_samples_leaf=5,
    n_jobs=-1,
).fit(TRAIN_X, TRAIN_Y)

risk_model = RandomForestClassifier(
    n_estimators=280,
    random_state=42,
    min_samples_leaf=5,
    n_jobs=-1,
).fit(RISK_X, RISK_Y)


def _features(origin_data, destination_data, days, people, interests, weather):
    distance = haversine_km(
        origin_data.get("latitude"),
        origin_data.get("longitude"),
        destination_data.get("latitude"),
        destination_data.get("longitude"),
    )
    distance = float(distance if distance is not None else 500.0)
    latitude = float(destination_data.get("latitude") or 20.0)
    rain = float(weather.get("average_precipitation") or 3.0)
    temp = float(weather.get("average_temperature") or 22.0)
    return [[days, people, distance, latitude, rain, temp, *interest_flags(interests)]], distance


def predict_cost(origin_data, destination_data, days, people, interests, weather):
    features, distance = _features(origin_data, destination_data, days, people, interests, weather)
    value = float(cost_model.predict(features)[0])
    return max(3500.0, value), distance


def predict_risk(origin_data, destination_data, days, people, interests, weather):
    features, _ = _features(origin_data, destination_data, days, people, interests, weather)
    probability = float(risk_model.predict_proba(features)[0][1])
    weather_pressure = min(0.28, float(weather.get("average_precipitation") or 0) / 50)
    return round(min(100.0, probability * 100 + weather_pressure * 100), 1)


def risk_level(score):
    if score >= 65:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Low"


def build_risk_analysis(destination_data, days, people, summary_text, weather):
    raw = build_dynamic_risks(summary_text, weather, destination_data.get("latitude"))
    risks = []
    for name, severity, description in raw:
        adjusted = severity
        if days > 10 and adjusted == "low":
            adjusted = "moderate"
        if people > 6 and adjusted == "low":
            adjusted = "moderate"
        risks.append({"risk": name, "severity": adjusted, "description": description})
    return risks


def build_itinerary(days, places):
    if not places:
        return []
    itinerary = []
    for day in range(1, days + 1):
        first = places[(day - 1) % len(places)]
        second = places[day % len(places)] if len(places) > 1 else None
        items = [first["name"]]
        if second and second["name"] != first["name"]:
            items.append(second["name"])
        itinerary.append({"day": day, "items": items})
    return itinerary


def plan_trip(data):
    destination_input = str(data.get("destination", "")).strip()
    origin_input = str(data.get("origin", "")).strip()
    days = int(data.get("days", 5))
    people = int(data.get("people", 2))
    interests = str(data.get("interests", "nature,food")).strip()

    if not origin_input:
        raise ValueError("Starting location is required.")
    if days < 1 or days > 30:
        raise ValueError("Days must be between 1 and 30.")
    if people < 1 or people > 20:
        raise ValueError("People must be between 1 and 20.")

    origin = resolve_destination(origin_input, data.get("origin_selection"), require_unique=False)
    destination = resolve_destination(destination_input, data.get("destination_selection"), require_unique=False)

    if origin["latitude"] is None or origin["longitude"] is None:
        raise ValueError("TripWise could not get coordinates for the starting location. Please choose a more specific place.")
    if destination["latitude"] is None or destination["longitude"] is None:
        raise ValueError("TripWise could not get coordinates for the destination. Please choose a more specific place.")

    destination_name = destination["name"]
    summary = wikipedia_summary(destination_name) or {"description": "", "image": None, "url": None}
    summary_text = summary.get("description", "")

    weather_info = best_time_from_weather(destination.get("latitude"), destination.get("longitude"))
    weather = weather_info.get("weather", {})
    cost, distance = predict_cost(origin, destination, days, people, interests, weather)
    per_person = cost / people
    risk = predict_risk(origin, destination, days, people, interests, weather)
    places = recommend_places(destination_name, interests)
    risks = build_risk_analysis(destination, days, people, summary_text, weather)

    transport_share = min(0.48, max(0.18, 0.20 + distance / 10000))
    stay = cost * (0.34 - (transport_share - 0.24) * 0.5)
    transport = cost * transport_share
    food = cost * 0.18
    activities = cost * 0.12
    buffer = max(0.0, cost - stay - transport - food - activities)

    return {
        "origin": origin["name"],
        "origin_display": origin.get("display_name", origin["name"]),
        "origin_input": origin_input,
        "destination": destination_name,
        "destination_display": destination.get("display_name", destination_name),
        "destination_input": destination_input,
        "origin_corrected": origin.get("corrected", False),
        "destination_corrected": destination.get("corrected", False),
        "correction_confidence": destination.get("correction_confidence", 0),
        "origin_latitude": origin.get("latitude"),
        "origin_longitude": origin.get("longitude"),
        "latitude": destination.get("latitude"),
        "longitude": destination.get("longitude"),
        "distance_km": round(distance, 1),
        "days": days,
        "people": people,
        "interests": interests,
        "predicted_cost": round(cost, 2),
        "per_person_cost": round(per_person, 2),
        "cost_range": [round(cost * 0.90), round(cost * 1.12)],
        "cost_breakdown": {
            "stay": round(stay),
            "transport": round(transport),
            "food": round(food),
            "activities": round(activities),
            "buffer": round(buffer),
        },
        "risk_score": risk,
        "risk_level": risk_level(risk),
        "risks": risks,
        "best_time": weather_info["best_time"],
        "best_time_note": weather_info["best_time_note"],
        "destination_image": summary.get("image"),
        "destination_url": summary.get("url"),
        "places": places,
        "itinerary": build_itinerary(days, places),
        "model_explanation": {
            "cost": "Random Forest regression estimates the trip budget using duration, group size, travel distance from the starting point, destination latitude, climate signals and interest patterns. Transport therefore changes when the starting point changes.",
            "risk": "Random Forest classification combines trip characteristics, travel distance and climate signals; destination-specific risk items are generated from retrieved destination and weather information.",
            "places": "TF-IDF cosine similarity ranks live destination pages discovered from Wikimedia against the user's interests.",
            "best_time": "The recommended window is calculated from 10 years of historical Open-Meteo temperature and precipitation data for the resolved destination coordinates.",
            "training_note": "The ML budget and risk models use reproducible synthetic training scenarios. Destination information is retrieved at request time, so new destinations do not need to be added to the codebase. The budget is an estimate, not a live booking quote.",
        },
    }
