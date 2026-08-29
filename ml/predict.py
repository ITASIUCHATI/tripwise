import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from recommend import DESTINATIONS, recommend_places

INTERESTS = [
    "nature", "adventure", "food", "culture", "peaceful",
    "shopping", "beach", "photography", "snow", "history",
]

DESTINATION_INDEX = {
    item["name"].lower(): index
    for index, item in enumerate(DESTINATIONS)
}

STYLE_MULTIPLIERS = {
    "budget": 0.88,
    "balanced": 1.0,
    "comfort": 1.22,
}


def interest_flags(interests):
    text = (interests or "").lower()
    return [1 if interest in text else 0 for interest in INTERESTS]


def cost_features(destination, days, people, interests):
    destination_index = DESTINATION_INDEX.get(destination.lower(), -1)
    return [[destination_index, days, people, *interest_flags(interests)]]


TRAIN_X = []
TRAIN_Y = []
rng = np.random.default_rng(42)

for destination in DESTINATIONS:
    destination_index = DESTINATION_INDEX[destination["name"].lower()]
    for _ in range(2500):
        days = int(rng.integers(1, 31))
        people = int(rng.integers(1, 11))
        flags = rng.integers(0, 2, size=len(INTERESTS)).tolist()
        interest_effect = 1 + flags[1] * 0.04 + flags[2] * 0.025 + flags[5] * 0.015
        cost = (
            destination["base"]
            + destination["daily"] * days
            + 1200 * people * days
            + 1800 * max(people - 1, 0)
        ) * interest_effect
        TRAIN_X.append([destination_index, days, people, *flags])
        TRAIN_Y.append(cost)

cost_model = RandomForestRegressor(
    n_estimators=220,
    random_state=42,
    min_samples_leaf=3,
).fit(TRAIN_X, TRAIN_Y)


RISK_X = []
RISK_Y = []

for destination in DESTINATIONS:
    destination_index = DESTINATION_INDEX[destination["name"].lower()]
    base_risk = sum(1 for _, level, _ in destination["risks"] if level == "high")
    for _ in range(2500):
        days = int(rng.integers(1, 31))
        people = int(rng.integers(1, 11))
        flags = rng.integers(0, 2, size=len(INTERESTS)).tolist()
        pressure = base_risk
        pressure += 1 if days > 10 else 0
        pressure += 1 if people > 6 else 0
        pressure += 1 if flags[1] else 0
        pressure += 1 if flags[7] else 0
        RISK_X.append([destination_index, days, people, *flags])
        RISK_Y.append(int(pressure >= 2))

risk_model = RandomForestClassifier(
    n_estimators=220,
    random_state=42,
    min_samples_leaf=4,
).fit(RISK_X, RISK_Y)



def predict_cost(destination, days, people, interests):
    value = cost_model.predict(cost_features(destination, days, people, interests))[0]
    return float(value)


def predict_risk(destination, days, people, interests):
    features = cost_features(destination, days, people, interests)
    probability = risk_model.predict_proba(features)[0][1]
    return round(float(probability) * 100, 1)


def risk_level(score):
    if score >= 65:
        return "High"
    if score >= 35:
        return "Moderate"
    return "Low"


def build_risk_analysis(destination, days, people):
    item = next((d for d in DESTINATIONS if d["name"].lower() == destination.lower()), None)
    if not item:
        return []

    risks = []
    for name, severity, description in item["risks"]:
        adjusted = severity
        if name == "Trekking fatigue" and days > 10:
            adjusted = "high"
        if name in {"Heat", "Heat and dehydration", "Heat and humidity"} and days > 7:
            adjusted = "high"
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

    destination = next(
        (item for item in DESTINATIONS if item["name"].lower() == destination_input.lower()),
        None,
    )

    if destination is None:
        raise ValueError("Destination not supported yet. Try Meghalaya, Manali, Coorg, Goa, Jaipur, Rishikesh, Sikkim or Kerala.")

    destination_name = destination["name"]
    cost = predict_cost(destination_name, days, people, interests)
    per_person = cost / people
    risk = predict_risk(destination_name, days, people, interests)
    places = recommend_places(destination_name, interests)
    risks = build_risk_analysis(destination_name, days, people)

    stay = cost * 0.34
    transport = cost * 0.24
    food = cost * 0.20
    activities = cost * 0.14
    buffer = cost * 0.08

    return {
        "destination": destination_name,
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
        "best_time": destination["best_time"],
        "best_time_note": destination["best_time_note"],
        "places": places,
        "itinerary": build_itinerary(days, places),
        "model_explanation": {
            "cost": "Random Forest regression estimates total trip cost from destination, trip duration, group size and interest signals.",
            "risk": "Random Forest classification estimates overall travel-risk pressure from destination, duration, group size and interest signals.",
            "places": "TF-IDF cosine similarity ranks places whose descriptions and tags best match the selected interests.",
            "best_time": "Best-time guidance is destination knowledge data, not a machine-learning prediction.",
            "training_note": "The current model is a reproducible prototype trained on generated travel scenarios. Real historical travel data would improve production accuracy.",
        },
    }
