def activity_priority(activity, style):
    text = activity.lower()

    scores = {
        "budget": {
            "walk": 5,
            "market": 5,
            "viewpoint": 4,
            "museum": 4,
            "cafe": 3,
            "trek": 4,
            "tour": 3,
            "activity": 2
        },
        "balanced": {
            "walk": 4,
            "market": 4,
            "viewpoint": 5,
            "museum": 4,
            "cafe": 4,
            "trek": 5,
            "tour": 4,
            "activity": 4
        },
        "comfort": {
            "walk": 3,
            "market": 2,
            "viewpoint": 5,
            "museum": 4,
            "cafe": 5,
            "trek": 3,
            "tour": 5,
            "activity": 4
        }
    }

    style_scores = scores.get(style, scores["balanced"])

    return sum(
        value
        for keyword, value in style_scores.items()
        if keyword in text
    )


def estimate_activity_cost(activity, style):
    text = activity.lower()

    base_cost = 500

    if any(word in text for word in ["trek", "river", "activity", "tour"]):
        base_cost = 1200
    elif any(word in text for word in ["museum", "market", "shopping"]):
        base_cost = 700
    elif any(word in text for word in ["cafe", "food"]):
        base_cost = 900
    elif any(word in text for word in ["walk", "viewpoint", "sunset"]):
        base_cost = 300

    multiplier = {
        "budget": 0.85,
        "balanced": 1.0,
        "comfort": 1.25
    }.get(style, 1.0)

    return round(base_cost * multiplier)


def select_activities(activities, budget, people, style):
    if not activities:
        return []

    available_budget = max(
        budget / max(people, 1),
        1000
    )

    scored = []

    for activity in activities:
        cost = estimate_activity_cost(activity, style)
        priority = activity_priority(activity, style)

        affordability = max(
            0,
            100 - (cost / available_budget) * 100
        )

        score = priority * 10 + affordability

        scored.append({
            "activity": activity,
            "cost": cost,
            "score": score
        })

    scored.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return [
        item["activity"]
        for item in scored
    ]


def build_itinerary(
    days,
    activities,
    budget=25000,
    people=2,
    style="balanced"
):
    if not activities:
        activities = [
            "Local sightseeing",
            "Scenic walk",
            "Local food experience"
        ]

    selected = select_activities(
        activities,
        budget,
        people,
        style
    )

    if not selected:
        selected = activities

    result = []

    for day in range(1, days + 1):
        first = selected[(day - 1) % len(selected)]
        second = selected[day % len(selected)]
        third = selected[(day + 1) % len(selected)]

        items = list(
            dict.fromkeys([
                first,
                second,
                third
            ])
        )

        result.append({
            "day": day,
            "items": items
        })

    return result
