import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DESTINATIONS = [
    {
        "name": "Meghalaya",
        "text": "nature waterfalls hills peaceful food adventure photography",
        "base": 12000
    },
    {
        "name": "Manali",
        "text": "mountains snow adventure nature trekking food photography",
        "base": 14500
    },
    {
        "name": "Coorg",
        "text": "coffee nature peaceful food hills photography relaxed",
        "base": 11000
    },
    {
        "name": "Goa",
        "text": "beach nightlife food adventure water sports relaxed",
        "base": 13500
    },
    {
        "name": "Jaipur",
        "text": "history culture food architecture shopping photography",
        "base": 10000
    },
    {
        "name": "Rishikesh",
        "text": "adventure river yoga nature trekking peaceful",
        "base": 9500
    },
    {
        "name": "Sikkim",
        "text": "mountains nature peaceful snow food photography trekking",
        "base": 14000
    },
    {
        "name": "Kerala",
        "text": "nature beaches food backwaters peaceful culture",
        "base": 12500
    }
]


vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2)
)

matrix = vectorizer.fit_transform(
    [destination["text"] for destination in DESTINATIONS]
)


STYLE_TERMS = {
    "budget": "affordable budget economical low cost",
    "balanced": "balanced comfortable value",
    "comfort": "comfortable premium luxury relaxed"
}


def destination_score(
    similarity,
    destination,
    requested_destination
):
    score = similarity * 100

    if requested_destination:
        requested = requested_destination.lower().strip()

        if requested == destination["name"].lower():
            score += 30
        elif requested in destination["name"].lower():
            score += 15

    return min(score, 99.0)


def recommend_destination(
    interests: str,
    style: str,
    destination: str = ""
):
    interests = interests or ""
    style = style or "balanced"
    destination = destination or ""

    style_text = STYLE_TERMS.get(
        style,
        STYLE_TERMS["balanced"]
    )

    query_text = (
        f"{interests} "
        f"{style_text} "
        f"{destination}"
    )

    query = vectorizer.transform([query_text])

    similarities = cosine_similarity(
        query,
        matrix
    )[0]

    ranked = np.argsort(
        similarities
    )[::-1]

    ranked_results = []

    for index in ranked:
        item = DESTINATIONS[int(index)]

        score = destination_score(
            float(similarities[int(index)]),
            item,
            destination
        )

        ranked_results.append({
            "destination": item["name"],
            "score": round(score, 1)
        })

    best_index = int(ranked[0])
    best = DESTINATIONS[best_index]

    match_score = destination_score(
        float(similarities[best_index]),
        best,
        destination
    )

    alternatives = ranked_results[:5]

    return (
        best,
        round(match_score, 1),
        alternatives
    )