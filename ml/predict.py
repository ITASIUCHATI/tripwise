import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from recommend import recommend_destination
from optimizer import build_itinerary


TRAIN_X = []
TRAIN_Y = []

for days in range(1, 31):
    for people in range(1, 11):
        for style_value in range(3):
            base = (
                4500
                + days * 1800
                + people * 2200
                + style_value * 3500
            )

            TRAIN_X.append([
                days,
                people,
                style_value,
            ])

            TRAIN_Y.append(base)


cost_model = RandomForestRegressor(
    n_estimators=150,
    random_state=42,
).fit(
    TRAIN_X,
    TRAIN_Y,
)


RISK_X = []
RISK_Y = []

for days in range(1, 31):
    for budget_ratio in np.linspace(0.4, 1.8, 20):
        for people in range(1, 6):
            RISK_X.append([
                days,
                budget_ratio,
                people,
            ])

            RISK_Y.append(
                int(
                    days > 10
                    or budget_ratio < 0.75
                    or people > 4
                )
            )


risk_model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
).fit(
    RISK_X,
    RISK_Y,
)


def style_value(style):
    return {
        "budget": 0,
        "balanced": 1,
        "comfort": 2,
    }.get(style, 1)


def predict_cost(days, people, style):
    value = cost_model.predict(
        [[
            days,
            people,
            style_value(style),
        ]]
    )[0]

    return float(value)


def predict_risk(
    days,
    people,
    budget,
    predicted_cost,
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
        ]]
    )[0][1]

    return round(
        float(probability) * 100,
        1,
    )


def predict_price(days, style):
    factor = {
        "budget": 0.94,
        "balanced": 1.0,
        "comfort": 1.14,
    }.get(style, 1.0)

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
    ]

    activities = []

    for word in words:
        activities.extend(
            catalog.get(
                word,
                [],
            )
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


def activity_score(
    interests,
    activities,
):
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
    )

    risk = predict_risk(
        days,
        people,
        budget,
        cost,
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

    return {
        "destination": destination_name,
        "match_score": round(match, 1),
        "predicted_cost": round(cost, 2),
        "cost_range": [
            round(cost * 0.9),
            round(cost * 1.12),
        ],
        "risk_score": risk,
        "price_prediction": price,
        "weather_suitability": weather,
        "activity_match": activity_match,
        "overall_score": score,
        "activities": activities,
        "itinerary": itinerary,
        "alternatives": alternatives,
    }