import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DESTINATIONS = [
    {
        "name": "Meghalaya",
        "tags": "nature waterfalls hills peaceful food adventure photography",
        "base": 9000,
        "daily": 1500,
        "best_time": "October to April",
        "best_time_note": "Cooler, clearer months are ideal for waterfalls, viewpoints and outdoor exploration.",
        "places": [
            {"name": "Sohra (Cherrapunji)", "description": "A misty hill region known for dramatic waterfalls, caves and lush landscapes.", "tags": "nature waterfall adventure photography"},
            {"name": "Dawki", "description": "A scenic riverside destination famous for the clear Umngot River and boating.", "tags": "nature adventure peaceful photography"},
            {"name": "Mawlynnong", "description": "A peaceful village surrounded by greenery, bamboo bridges and scenic viewpoints.", "tags": "nature peaceful photography culture"},
            {"name": "Shillong", "description": "A lively hill city with cafes, viewpoints, local food and a relaxed cultural scene.", "tags": "food culture shopping peaceful photography"},
            {"name": "Nongriat", "description": "A rewarding trek through forest trails to the famous living root bridges.", "tags": "adventure nature trekking photography"},
        ],
        "risks": [
            ("Heavy rain", "high", "Rain can make roads, trails and waterfall areas slippery or temporarily inaccessible."),
            ("Road conditions", "moderate", "Hill roads can be slow or difficult during heavy rainfall."),
            ("Trekking fatigue", "moderate", "Some attractions require long walks, steep steps or trekking."),
        ],
    },
    {
        "name": "Manali",
        "tags": "mountains snow adventure nature trekking food photography peaceful",
        "base": 10500,
        "daily": 1750,
        "best_time": "March to June and October to February",
        "best_time_note": "Spring and early summer are good for general sightseeing; winter is best for snow experiences.",
        "places": [
            {"name": "Solang Valley", "description": "A mountain valley popular for scenic views and seasonal adventure activities.", "tags": "adventure snow nature photography"},
            {"name": "Old Manali", "description": "A relaxed area with cafes, local shops, riverside walks and mountain views.", "tags": "food peaceful shopping culture"},
            {"name": "Rohtang Pass", "description": "A high-altitude mountain pass offering dramatic Himalayan scenery when accessible.", "tags": "snow adventure nature photography"},
            {"name": "Hadimba Temple", "description": "A historic wooden temple set among tall cedar trees near Manali.", "tags": "culture peaceful nature photography"},
            {"name": "Vashisht", "description": "A hillside village known for its temple, hot springs and panoramic views.", "tags": "peaceful culture nature"},
        ],
        "risks": [
            ("Altitude effects", "moderate", "Higher areas can cause headache, breathlessness or fatigue for some travelers."),
            ("Snow and road closures", "high", "Winter weather can affect access to high-altitude roads and passes."),
            ("Adventure activity risk", "moderate", "Trekking and outdoor activities require proper equipment and local guidance."),
        ],
    },
    {
        "name": "Coorg",
        "tags": "coffee nature peaceful food hills photography relaxed",
        "base": 8500,
        "daily": 1400,
        "best_time": "October to March",
        "best_time_note": "Pleasant weather makes these months comfortable for plantations, viewpoints and outdoor activities.",
        "places": [
            {"name": "Abbey Falls", "description": "A popular waterfall surrounded by dense greenery and coffee-growing landscapes.", "tags": "nature waterfall photography"},
            {"name": "Raja's Seat", "description": "A scenic viewpoint known for beautiful valley views and sunsets.", "tags": "peaceful nature photography"},
            {"name": "Mandalpatti", "description": "A high viewpoint offering expansive views across the Western Ghats.", "tags": "adventure nature photography"},
            {"name": "Coffee Plantations", "description": "A chance to explore Coorg's coffee culture, plantations and local produce.", "tags": "food nature culture peaceful"},
            {"name": "Dubare", "description": "A riverside forest area suited to nature experiences and outdoor activities.", "tags": "nature adventure peaceful"},
        ],
        "risks": [
            ("Monsoon rain", "moderate", "Rain can make trails and roads slippery and may affect waterfall access."),
            ("Road travel", "low", "Curvy hill roads can make journeys slower, especially in poor weather."),
            ("Leeches on trails", "low", "Forest trails during wet periods may have leeches."),
        ],
    },
    {
        "name": "Goa",
        "tags": "beach nightlife food adventure water sports relaxed culture shopping",
        "base": 10000,
        "daily": 1900,
        "best_time": "November to February",
        "best_time_note": "The dry season is generally the most comfortable for beaches, sightseeing and outdoor activities.",
        "places": [
            {"name": "Baga and Calangute", "description": "Busy North Goa beaches with restaurants, nightlife and water activities.", "tags": "beach food adventure shopping"},
            {"name": "Palolem", "description": "A scenic South Goa beach with a calmer atmosphere and beautiful sunsets.", "tags": "beach peaceful photography"},
            {"name": "Fontainhas", "description": "A colorful heritage quarter with Portuguese-era architecture and narrow lanes.", "tags": "culture photography food"},
            {"name": "Old Goa", "description": "A historic area with landmark churches and important heritage sites.", "tags": "culture history photography"},
            {"name": "Dudhsagar Falls", "description": "A spectacular waterfall experience surrounded by forested Western Ghats.", "tags": "nature adventure photography"},
        ],
        "risks": [
            ("Strong sea conditions", "moderate", "Swimming and water activities can be unsafe when waves or currents are strong."),
            ("Heat and dehydration", "moderate", "Sun exposure can be significant, especially during hotter months."),
            ("Crowds and peak-season prices", "moderate", "Popular areas can become crowded and accommodation can cost more in peak season."),
        ],
    },
    {
        "name": "Jaipur",
        "tags": "history culture food architecture shopping photography",
        "base": 7500,
        "daily": 1350,
        "best_time": "October to March",
        "best_time_note": "Cooler winter months are more comfortable for forts, markets and walking tours.",
        "places": [
            {"name": "Amber Fort", "description": "A grand hilltop fort showcasing Rajput architecture, courtyards and historic views.", "tags": "culture history architecture photography"},
            {"name": "City Palace", "description": "A royal complex combining museums, courtyards and traditional Jaipur architecture.", "tags": "culture history architecture photography"},
            {"name": "Hawa Mahal", "description": "Jaipur's iconic palace facade, especially striking from the surrounding old-city streets.", "tags": "culture architecture photography"},
            {"name": "Jantar Mantar", "description": "An impressive historic observatory featuring large astronomical instruments.", "tags": "culture history architecture"},
            {"name": "Johari Bazaar", "description": "A lively market area known for jewelry, handicrafts, textiles and local shopping.", "tags": "shopping culture food"},
        ],
        "risks": [
            ("Heat", "moderate", "Daytime temperatures can be uncomfortable outside the cooler season."),
            ("Crowded tourist areas", "moderate", "Major forts and markets can be busy during peak hours."),
            ("Traffic", "low", "Urban traffic can increase travel time between attractions."),
        ],
    },
    {
        "name": "Rishikesh",
        "tags": "adventure river yoga nature trekking peaceful culture food",
        "base": 7000,
        "daily": 1300,
        "best_time": "September to November and February to May",
        "best_time_note": "Pleasant temperatures support river activities, trekking, yoga and sightseeing.",
        "places": [
            {"name": "Laxman Jhula Area", "description": "A scenic riverside area surrounded by temples, cafes and views of the Ganga.", "tags": "culture peaceful food photography"},
            {"name": "Neer Garh Waterfall", "description": "A forested waterfall trail suited to a short nature outing.", "tags": "nature adventure peaceful"},
            {"name": "Ganga Riverside", "description": "A peaceful setting for walks, sunsets and the area's spiritual atmosphere.", "tags": "peaceful culture photography"},
            {"name": "River Rafting", "description": "A popular adventure experience on suitable stretches of the Ganga with trained operators.", "tags": "adventure river"},
            {"name": "Beatles Ashram", "description": "A distinctive cultural and artistic site with murals and a quiet forest setting.", "tags": "culture photography peaceful"},
        ],
        "risks": [
            ("River activity risk", "high", "Rafting and water activities should only be done with reputable trained operators."),
            ("Monsoon river levels", "high", "Heavy rain can raise river levels and affect access to water activities."),
            ("Trekking terrain", "moderate", "Uneven trails and wet surfaces can increase slip and fall risk."),
        ],
    },
    {
        "name": "Sikkim",
        "tags": "mountains nature peaceful snow food photography trekking culture",
        "base": 11000,
        "daily": 1800,
        "best_time": "March to May and October to December",
        "best_time_note": "Spring and autumn generally offer good visibility for mountain views and comfortable sightseeing.",
        "places": [
            {"name": "Gangtok", "description": "Sikkim's main hill city with monasteries, viewpoints, markets and mountain scenery.", "tags": "culture food shopping peaceful"},
            {"name": "Tsomgo Lake", "description": "A high-altitude glacial lake surrounded by dramatic mountain landscapes.", "tags": "nature snow photography"},
            {"name": "Nathula Pass", "description": "A high mountain pass with striking Himalayan scenery, subject to access conditions and permits.", "tags": "adventure snow nature"},
            {"name": "Pelling", "description": "A quieter mountain destination known for panoramic views of the Kanchenjunga range.", "tags": "peaceful nature photography"},
            {"name": "Rumtek Monastery", "description": "An important Buddhist monastery with architecture, spiritual atmosphere and mountain surroundings.", "tags": "culture peaceful photography"},
        ],
        "risks": [
            ("High altitude", "high", "High-altitude locations can cause altitude-related symptoms and require gradual acclimatization."),
            ("Weather changes", "moderate", "Mountain weather can change quickly and affect road access."),
            ("Permit restrictions", "moderate", "Some border and high-altitude areas require permits and may have access restrictions."),
        ],
    },
    {
        "name": "Kerala",
        "tags": "nature beaches food backwaters peaceful culture photography relaxed",
        "base": 9500,
        "daily": 1700,
        "best_time": "October to March",
        "best_time_note": "The cooler, drier season is well suited to beaches, backwaters, wildlife and cultural sightseeing.",
        "places": [
            {"name": "Alleppey Backwaters", "description": "A relaxing network of canals and lagoons best experienced by boat or houseboat.", "tags": "nature peaceful photography"},
            {"name": "Munnar", "description": "A cool hill destination surrounded by tea plantations, viewpoints and greenery.", "tags": "nature peaceful photography"},
            {"name": "Fort Kochi", "description": "A historic coastal neighborhood with colonial architecture, art and local food.", "tags": "culture food photography"},
            {"name": "Varkala", "description": "A dramatic cliffside beach destination with sea views, cafes and sunset walks.", "tags": "beach peaceful food photography"},
            {"name": "Thekkady", "description": "A forested destination known for wildlife experiences, spice plantations and outdoor activities.", "tags": "nature adventure photography"},
        ],
        "risks": [
            ("Monsoon disruption", "moderate", "Heavy rain can affect outdoor plans, roads and some activities."),
            ("Heat and humidity", "moderate", "Humidity can make long outdoor sightseeing tiring."),
            ("Wildlife activity precautions", "low", "Follow local guides and park rules during wildlife experiences."),
        ],
    },
]

vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))


def recommend_places(destination: str, interests: str, limit: int = 5):
    item = next(
        (d for d in DESTINATIONS if d["name"].lower() == destination.lower()),
        None,
    )
    if not item:
        return []

    places = item["places"]
    documents = [f'{place["name"]} {place["tags"]} {place["description"]}' for place in places]
    matrix = vectorizer.fit_transform(documents)
    query = vectorizer.transform([interests or "nature sightseeing"])
    similarities = cosine_similarity(query, matrix)[0]

    ranked = np.argsort(similarities)[::-1][:limit]
    results = []
    for index in ranked:
        place = places[int(index)]
        results.append({
            "name": place["name"],
            "description": place["description"],
            "match_score": round(float(similarities[int(index)]) * 100, 1),
            "tags": place["tags"].split(),
        })
    return results
