import os
import re

import requests
from dotenv import load_dotenv
from src.constants.tags import NAME_TAG_RULES


PLACES_URL = "https://api.geoapify.com/v2/places"



class GeoapifyError(RuntimeError):
    """Raised when nearby restaurants cannot be retrieved."""


def infer_name_tags(name):
    """Infer explainable recommendation tags from words in a restaurant name."""
    normalized_name = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
    words = set(normalized_name.split())
    tags = []

    for keyword, keyword_tags in NAME_TAG_RULES.items():
        if keyword in words:
            for tag in keyword_tags:
                if tag not in tags:
                    tags.append(tag)

    return tags


def _cuisine_tags(properties):
    cuisine = properties.get("catering", {}).get("cuisine")
    tags = []

    if isinstance(cuisine, str):
        tags.extend(
            tag.strip().lower()
            for tag in re.split(r"[;,]", cuisine)
            if tag.strip()
        )
    elif isinstance(cuisine, list):
        tags.extend(str(tag).lower() for tag in cuisine)

    category_prefix = "catering.restaurant."
    for category in properties.get("categories", []):
        if category.startswith(category_prefix):
            tags.append(category[len(category_prefix) :])

    return list(dict.fromkeys(tags))


def _diet_value(properties, diet_name):
    diet = properties.get("catering", {}).get("diet", {})
    if diet_name in diet:
        return bool(diet[diet_name])
    if diet_name in properties.get("categories", []):
        return True
    return None


def normalize_restaurant(feature):
    """Convert one Geoapify feature into the app's restaurant structure."""
    properties = feature.get("properties", {})
    geometry_coordinates = feature.get("geometry", {}).get("coordinates", [])
    name = properties.get("name") or "Unnamed restaurant"
    api_cuisine = _cuisine_tags(properties)
    name_tags = infer_name_tags(name)

    recommendation_tags = list(api_cuisine)
    for tag in name_tags:
        if tag not in recommendation_tags:
            recommendation_tags.append(tag)

    longitude = properties.get("lon")
    latitude = properties.get("lat")
    if len(geometry_coordinates) >= 2:
        longitude = longitude if longitude is not None else geometry_coordinates[0]
        latitude = latitude if latitude is not None else geometry_coordinates[1]

    return {
        "place_id": properties.get("place_id"),
        "name": name,
        "distance_meters": properties.get("distance"),
        "address": properties.get("address_line2")
        or properties.get("formatted"),
        "latitude": latitude,
        "longitude": longitude,
        "api_cuisine": api_cuisine,
        "name_tags": name_tags,
        "recommendation_tags": recommendation_tags,
        "vegetarian": _diet_value(properties, "vegetarian"),
        "vegan": _diet_value(properties, "vegan"),
        "website": properties.get("website"),
        "opening_hours": properties.get("opening_hours"),
    }


def get_nearby_restaurants_response(
    latitude, longitude, radius_meters=5_000, limit=20
):
    """Return the raw Geoapify response for nearby restaurants."""
    load_dotenv()
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key:
        raise GeoapifyError(
            "GEOAPIFY_API_KEY is missing. Add it to the project's .env file."
        )

    params = {
        "categories": "catering.restaurant",
        "filter": f"circle:{longitude},{latitude},{radius_meters}",
        "bias": f"proximity:{longitude},{latitude}",
        "limit": limit,
        "apiKey": api_key,
    }

    try:
        response = requests.get(PLACES_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        # Request exception strings can contain the full URL, including the API key.
        raise GeoapifyError(
            "Geoapify request failed. Check your connection, API key, and quota."
        ) from error

    return response.json()


def find_nearby_restaurants(latitude, longitude, radius_meters=5_000, limit=20):
    """Return nearby restaurant summaries from Geoapify."""
    response_data = get_nearby_restaurants_response(
        latitude, longitude, radius_meters, limit
    )

    restaurants = []
    for feature in response_data.get("features", []):
        restaurants.append(normalize_restaurant(feature))

    return restaurants
