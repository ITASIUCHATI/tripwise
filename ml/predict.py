import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from recommend import (
    INTEREST_ALIASES,
    best_time_from_weather,
    build_dynamic_risks,
    recommend_places,
    resolve_destination,
    wikipedia_summary,
)

INTERESTS = list(INTEREST_ALIASES.keys())
STYLE_MULTIPLIERS = {
    "budget": 0.82,
    "balanced": 1.0,
    "comfort": 1.25,
}


def interest_flags(interests):
    text = str(interests or "").lower()
    return [1 if interest in text else 0 for interest in INTERESTS]


rng = np.random.default_rng(42)
TRAIN_X = []
TRAIN_Y = []
RISK_X = []
RISK_Y = []

for _ in range(18000):
    days = int(rng.integers(1, 31))
    people = int(rng.integers(1, 11))
    latitude = float(rng.uniform(-55, 70))
    rain = float(rng.uniform(0, 15))
    temp = float(rng.uniform(-5, 35))
    flags = rng.integers(0, 2, size=len(INTERESTS)).tolist()

    domestic_index = 0.85 if rng.random() < 0.72 else 1.18
    climate_factor = 1 + max(0, abs(temp - 22) - 8) * 0.008
    interest_factor = 1 + flags[1] * 0.04 + flags[2] * 0.025 + flags[5] * 0.015
    base = 5500 + abs(latitude) * 18 + rain * 70
    cost = (
        base
        + 1200 * days
        + 900 * people * days
        + 1600 * max(people - 1, 0)
    ) * domestic_index * climate_factor * interest_factor

    features = [days, people, latitude, rain, temp, *flags]
    TRAIN_X.append(features)
    TRAIN_Y.append(cost)

    pressure = 0
    pressure += 2 if rain > 7 else 1 if rain > 3 else 0
    pressure += 2 if temp >= 32 or temp <= 2 else 1 if temp >= 28 or temp <= 10 else 0
    pressure += 1 if days > 10 else 0
    pressure += 1 if people > 6 else 0
    pressure += 1 if flags[1] else 0
    pressure += 1 if flags[7] else 0
    RISK_X.append(features)
    RISK_Y.append(int(pressure >= 3))


cost_model = RandomForestRegressor(
    n_estimators=260,
    random_state=42,
    min_samples_leaf=5,
    n_jobs=-1,
).fit(TRAIN_X, TRAIN_Y)

risk_model = RandomForestClassifier(
    n_estimators=260,
    random_state=42,
    min_samples_leaf=5,
    n_jobs=-1,
).fit(RISK_X, RISK_Y)


def _features(destination_data, days, people, interests, weather):
    latitude = float(destination_data.get("latitude") or 20.0)
    rain = float(weather.get("average_precipitation") or 3.0)
    temp = float(weather.get("average_temperature") or 22.0)
    return [[days, people, latitude, rain, temp, *interest_flags(interests)]]


def predict_cost(destination_data, days, people, interests, weather):
    value = float(cost_model.predict(_features(destination_data, days, people, interests, weather))[0])
    return max(3500.0, value)


def predict_risk(destination_data, days, people, interests, weather):
    features = _features(destination_data, days, people, interests, weather)
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
    raw = build_dynamic_risks(
        summary_text,
        weather,
        destination_data.get("latitude"),
    )
    risks = []
    for name, severity, description in raw:
        adjusted = severity
        if days > 10 and adjusted == "low":
            adjusted = "moderate"
        if people > 6 and adjusted == "low":
            adjusted = "moderate"
        risks.append({
            "risk": name,
            "severity": adjusted,
            "description": description,
        })
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
    days = int(data.get("days", 5))
    people = int(data.get("people", 2))
    interests = str(data.get("interests", "nature,food")).strip()

    if days < 1 or days > 30:
        raise ValueError("Days must be between 1 and 30.")
    if people < 1 or people > 20:
        raise ValueError("People must be between 1 and 20.")

    destination = resolve_destination(destination_input)
    destination_name = destination["name"]

    summary = wikipedia_summary(destination_name) or {
        "description": ""
    }
    summary_text = summary.get("description", "")

    weather_info = best_time_from_weather(
        destination.get("latitude"),
        destination.get("longitude"),
    )
    weather = weather_info.get("weather", {})

    cost = predict_cost(destination, days, people, interests, weather)
    per_person = cost / people
    risk = predict_risk(destination, days, people, interests, weather)
    places = recommend_places(destination_name, interests)
    risks = build_risk_analysis(
        destination,
        days,
        people,
        summary_text,
        weather,
    )

    stay = cost * 0.34
    transport = cost * 0.24
    food = cost * 0.20
    activities = cost * 0.14
    buffer = cost * 0.08

    return {
        "destination": destination_name,
        "destination_display": destination.get("display_name", destination_name),
        "destination_input": destination_input,
        "destination_corrected": destination.get("corrected", False),
        "correction_confidence": destination.get("correction_confidence", 0),
        "latitude": destination.get("latitude"),
        "longitude": destination.get("longitude"),
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
        "places": places,
        "itinerary": build_itinerary(days, places),
        "model_explanation": {
            "cost": "Random Forest regression estimates a trip budget from duration, group size, latitude and destination climate signals plus interest patterns. It is a prototype estimate, not a live booking quote.",
            "risk": "Random Forest classification combines trip characteristics and climate signals; destination-specific risk items are generated from retrieved destination and weather information.",
            "places": "TF-IDF cosine similarity ranks live destination pages discovered from Wikimedia against the user's interests.",
            "best_time": "The recommended window is calculated from 10 years of historical Open-Meteo temperature and precipitation data for the resolved destination coordinates.",
            "training_note": "The ML budget and risk models use reproducible synthetic training scenarios. Live destination information is retrieved at request time, so new destinations do not need to be added to the codebase.",
        },
    }
