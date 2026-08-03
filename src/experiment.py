import random


def calculate_fetch_limit(feedback_rows, pool_size=50):
    """Return how many places to request to allow for reviewed results."""
    reviewed_place_ids = {
        feedback.get("place_id")
        for feedback in feedback_rows
        if feedback.get("place_id")
    }
    return pool_size + len(reviewed_place_ids)


def remove_reviewed_restaurants(restaurants, feedback_rows):
    """Return restaurants whose Place IDs do not appear in saved feedback."""
    reviewed_place_ids = {
        feedback.get("place_id")
        for feedback in feedback_rows
        if feedback.get("place_id")
    }
    return [
        restaurant
        for restaurant in restaurants
        if restaurant.get("place_id") not in reviewed_place_ids
    ]


def split_restaurant_pool(restaurants, rating_count=20):
    """Split 50 restaurants into repeatable rating and candidate groups."""
    if len(restaurants) < 50:
        raise ValueError("At least 50 restaurants are required.")
    if not 1 <= rating_count < 50:
        raise ValueError("rating_count must be between 1 and 49.")

    experiment_pool = list(restaurants[:50])
    random.Random(42).shuffle(experiment_pool)

    return (
        experiment_pool[:rating_count],
        experiment_pool[rating_count:],
    )
