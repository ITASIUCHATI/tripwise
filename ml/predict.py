import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from recommend import DESTINATIONS, recommend_destination
from optimizer import build_itinerary

STYLE_VALUES = {
    "budget": 0,
    "balanced": 1,
    "comfort": 2,
}

DESTINATION_VALUES = {
    item["name"].lower(): index
    for index, item in enumerate(DESTINATIONS)
}

DESTINATION_PROFILES = {
    "Meghalaya": {"base": 9000, "daily": 1500},
    "Manali": {"base": 10500, "daily": 1750},
    "Coorg": {"base": 8500, "daily": 1400},
    "Goa": {"base": 10000, "daily": 1900},
    "Jaipur": {"base": 7500, "daily": 1350},
    "Rishikesh": {"base": 7000, "daily": 1300},
    "Sikkim": {"base": 11000, "daily": 1800},
    "Kerala": {"base": 9500, "daily": 1700},
}

STYLE_MULTIPLIERS = {
    "budget": 0.88,
    "balanced": 1.0,
    "comfort": 1.22,
}

TRAIN_X = []
TRAIN_Y = []

for destination, profile in DESTINATION_PROFILES.items():
    destination_value = DESTINATION_VALUES[destination.lower()]

    for days in range(1, 31):
        for people in range(1, 11):
            for style, style_value in STYLE_VALUES.items():
                multiplier = STYLE_MULTIPLIERS[style]
                base_cost = profile["base"]
                daily_cost = profile["daily"] * days
                traveler_cost = 1200 * people * days
                group_adjustment = 1800 * max(people - 1, 0)
                cost = (
                    base_cost
                    + daily_cost
                    + traveler_cost
                    + group_adjustment
                ) * multiplier

                TRAIN_X.append([
                    days,
                    people,
                    style_value,
                    destination_value,
                ])
                TRAIN_Y.append(cost)

cost_model = RandomForestRegressor(
    n_estimators=220,
    random_state=42,
    min_samples_leaf=3,
).fit(
    TRAIN_X,
    TRAIN_Y,
)

RISK_X = []
RISK_Y = []

for days in range(1, 31):
    for budget_ratio in np.linspace(0.35, 1.8, 30):
        for people in range(1, 11):
            for style_value in range(3):
                pressure = 0
                pressure += 1 if budget_ratio < 0.75 else 0
                pressure += 1 if days > 10 else 0
                pressure += 1 if people > 5 else 0
                pressure += 1 if style_value == 2 and budget_ratio < 0.95 else 0

                RISK_X.append([
                    days,
                    budget_ratio,
                    people,
                    style_value,
                ])
                RISK_Y.append(int(pressure >= 2))

risk_model = RandomForestClassifier(
    n_estimators=220,
    random_state=42,
    min_samples_leaf=4,
).fit(
    RISK_X,
    RISK_Y,
)


def style_value(style):
    return STYLE_VALUES.get(style, 1)


def destination_value(destination):
    return DESTINATION_VALUES.get(
        destination.lower(),
        len(DESTINATION_VALUES),
    )


def destination_profile(destination):
    if destination in DESTINATION_PROFILES:
        return DESTINATION_PROFILES[destination]

    return {
        "base": 8500,
        "daily": 1600,
    }


def predict_cost(
    days,
    people,
    style,
    destination,
):
    value = cost_model.predict(
        [[
            days,
            people,
            style_value(style),
            destination_value(destination),
        ]]
    )[0]

    return float(value)


def predict_risk(
    days,
    people,
    budget,
    predicted_cost,
    style,
):
    budget_ratio = budget / max(
        predicted_cost,
        1,
    )

    probability = risk_model.predict_proba(
        [[
            days,
            budget_ratio,
            people,
            style_value(style),
        ]]
    )[0][1]

    return round(
        float(probability) * 100,
        1,
    )


def predict_price(days, style):
    factor = STYLE_MULTIPLIERS.get(
        style,
        1.0,
    )

    return round(
        (1200 + days * 180) * factor,
        2,
    )


def weather_score(destination):
    scores = {
        "Meghalaya": 84,
        "Manali": 89,
        "Coorg": 91,
        "Goa": 86,
        "Jaipur": 88,
        "Rishikesh": 92,
        "Sikkim": 83,
        "Kerala": 90,
    }

    return scores.get(
        destination,
        80,
    )


def activity_recommendations(
    interests,
    destination,
):
    catalog = {
        "nature": [
            "Sunrise viewpoint",
            "Waterfall walk",
            "Nature photography",
        ],
        "adventure": [
            "Guided trek",
            "River activity",
            "Outdoor trail",
        ],
        "food": [
            "Local food tour",
            "Traditional cafe",
            "Market tasting",
        ],
        "culture": [
            "Heritage walk",
            "Local museum",
            "Cultural performance",
        ],
        "peaceful": [
            "Quiet scenic walk",
            "Sunset spot",
            "Cafe afternoon",
        ],
        "shopping": [
            "Local market",
            "Handicraft shopping",
            "Souvenir street",
        ],
        "beach": [
            "Beach walk",
            "Water activity",
            "Sunset viewpoint",
        ],
    }

    words = [
        word.strip().lower()
        for word in interests.split(",")
        if word.strip()
    ]

    activities = []

    for word in words:
        activities.extend(
            catalog.get(word, [])
        )

    if not activities:
        activities = [
            "Local sightseeing",
            "Scenic walk",
            "Local food experience",
        ]

    return list(
        dict.fromkeys(activities)
    )[:6]


def activity_score(interests, activities):
    requested = {
        word.strip().lower()
        for word in interests.split(",")
        if word.strip()
    }

    if not requested:
        return 70.0

    matched = 0

    for activity in activities:
        activity_text = activity.lower()

        if any(
            interest in activity_text
            for interest in requested
        ):
            matched += 1

    score = (
        60
        + (
            matched
            / max(len(activities), 1)
        )
        * 40
    )

    return round(
        min(score, 100),
        1,
    )


def overall_score(
    match_score,
    weather,
    activity_match,
    risk_score,
):
    score = (
        match_score * 0.35
        + weather * 0.20
        + activity_match * 0.25
        + (100 - risk_score) * 0.20
    )

    return round(
        min(max(score, 0), 100),
        1,
    )


def plan_trip(data):
    requested_destination = (
        data.get("destination", "")
        or ""
    ).strip()

    days = int(data["days"])
    people = int(data["people"])
    budget = float(data["budget"])
    interests = data["interests"]
    style = data["style"]

    recommended, match, alternatives = (
        recommend_destination(
            interests,
            style,
            requested_destination,
        )
    )

    if requested_destination:
        destination = next(
            (
                item
                for item in [
                    recommended,
                    *[
                        {
                            "name": result["destination"]
                        }
                        for result in alternatives
                    ],
                ]
                if item["name"].lower()
                == requested_destination.lower()
            ),
            None,
        )

        if destination is None:
            destination = {
                "name": requested_destination,
                "base": 0,
            }

        destination_name = destination["name"]

        if destination_name.lower() == requested_destination.lower():
            destination_match = next(
                (
                    result["score"]
                    for result in alternatives
                    if result["destination"].lower()
                    == requested_destination.lower()
                ),
                match,
            )

            match = max(
                float(destination_match),
                70.0,
            )
    else:
        destination = recommended
        destination_name = destination["name"]

    cost = predict_cost(
        days,
        people,
        style,
        destination_name,
    )

    risk = predict_risk(
        days,
        people,
        budget,
        cost,
        style,
    )

    price = predict_price(
        days,
        style,
    )

    weather = weather_score(
        destination_name,
    )

    activities = activity_recommendations(
        interests,
        destination_name,
    )

    activity_match = activity_score(
        interests,
        activities,
    )

    itinerary = build_itinerary(
        days,
        activities,
        budget,
        people,
        style,
    )

    score = overall_score(
        match,
        weather,
        activity_match,
        risk,
    )

    profile = destination_profile(
        destination_name,
    )

    return {
        "destination": destination_name,
        "match_score": round(match, 1),
        "predicted_cost": round(cost, 2),
        "cost_range": [
            round(cost * 0.92),
            round(cost * 1.08),
        ],
        "risk_score": risk,
        "risk_level": (
            "High"
            if risk >= 60
            else "Moderate"
            if risk >= 30
            else "Low"
        ),
        "price_prediction": price,
        "weather_suitability": weather,
        "activity_match": activity_match,
        "overall_score": score,
        "activities": activities,
        "itinerary": itinerary,
        "alternatives": alternatives,
        "model_explanation": {
            "cost": "Random Forest regression predicts total trip cost from destination, days, travelers, and travel style.",
            "risk": "Random Forest classification estimates trip budget risk from duration, group size, travel style, and budget-to-predicted-cost ratio.",
            "destination": "TF-IDF cosine similarity ranks destinations against the requested interests, travel style, and destination text.",
            "supporting_signals": "Weather suitability and itinerary optimization are rule-based supporting components, not ML predictions.",
            "training_note": "The current prototype models are trained on generated travel scenarios for demonstration and should be retrained on real historical travel data for production-grade accuracy.",
        },
        "prediction_inputs": {
            "destination": destination_name,
            "days": days,
            "people": people,
            "budget": budget,
            "interests": interests,
            "style": style,
            "destination_base_cost": profile["base"],
            "destination_daily_cost": profile["daily"],
        },
    }
