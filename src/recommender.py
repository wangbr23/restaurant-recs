# Step 1: simple rule-based recommender
# This is the first building block of the app.
# We will add more features in later steps.

from src.constants import weights


RESTAURANTS = [
    {
        "name": "Sushi House",
        "distance": 2.0,
        "rating": 4.7,
        "vegetarian_friendly": False,
        "spicy": True,
        "late_night": False,
    },
    {
        "name": "Garden Cafe",
        "distance": 3.0,
        "rating": 4.2,
        "vegetarian_friendly": True,
        "spicy": False,
        "late_night": False,
    },
    {
        "name": "Fire Grill",
        "distance": 1.5,
        "rating": 4.8,
        "vegetarian_friendly": False,
        "spicy": True,
        "late_night": True,
    },
    {
        "name": "Pasta Place",
        "distance": 2.5,
        "rating": 4.4,
        "vegetarian_friendly": True,
        "spicy": False,
        "late_night": False,
    },
]


def build_preferences(args):
    return {
        "vegetarian": args.vegetarian,
        "spicy": args.spicy,
        "late_night": args.late_night,
        "max_distance": args.max_distance,
        "min_rating": args.min_rating,
    }


def score_restaurant(restaurant, preferences):
    score = 0.0
    reasons = []

    if preferences.get("vegetarian", False) and restaurant.get("vegetarian_friendly", False):
        score += weights["vegetarian"]
        reasons.append("vegetarian-friendly")

    if preferences.get("spicy", False) and restaurant.get("spicy", False):
        score += weights["spicy"]
        reasons.append("spicy")

    if preferences.get("late_night", False) and restaurant.get("late_night", False):
        score += weights["late_night"]
        reasons.append("late-night")

    if restaurant.get("distance", 999) <= preferences.get("max_distance", 999):
        score += weights["distance"]
        reasons.append("within distance")

    if restaurant.get("rating", 0) >= preferences.get("min_rating", 0):
        score += weights["rating"]
        reasons.append("high rating")

    return score, reasons


def explain_restaurant_score(restaurant, preferences):
    score, reasons = score_restaurant(restaurant, preferences)
    return {
        "name": restaurant["name"],
        "score": score,
        "reasons": reasons,
    }


def recommend_restaurants(restaurants, preferences, top_n=5):
    ranked = []

    for restaurant in restaurants:
        score, reasons = score_restaurant(restaurant, preferences)
        ranked.append((restaurant["name"], score, reasons))

    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[:top_n]
