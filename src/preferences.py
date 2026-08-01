def build_preference_profile(feedback_rows):
    """Turn like/dislike feedback into an accumulated score per tag."""
    profile = {}

    for feedback in feedback_rows:
        liked = feedback.get("liked")
        if not isinstance(liked, bool):
            continue

        score_change = 1 if liked else -1
        unique_tags = {
            tag.strip().lower()
            for tag in feedback.get("recommendation_tags", [])
            if isinstance(tag, str) and tag.strip()
        }

        for tag in unique_tags:
            profile[tag] = profile.get(tag, 0) + score_change

    return profile


def score_restaurant_for_profile(restaurant, profile):
    """Return a restaurant's score from its tags and a preference profile."""
    unique_tags = {
        tag.strip().lower()
        for tag in restaurant.get("recommendation_tags", [])
        if isinstance(tag, str) and tag.strip()
    }

    return sum(profile.get(tag, 0) for tag in unique_tags)


def rank_restaurants_for_profile(restaurants, profile):
    """Return scored restaurants ordered by preference, then distance."""
    scored_restaurants = []

    for restaurant in restaurants:
        scored_restaurant = dict(restaurant)
        scored_restaurant["preference_score"] = score_restaurant_for_profile(
            restaurant,
            profile,
        )
        scored_restaurants.append(scored_restaurant)

    scored_restaurants.sort(
        key=lambda restaurant: (
            -restaurant["preference_score"],
            restaurant.get("distance_meters") is None,
            restaurant.get("distance_meters") or 0,
        )
    )
    return scored_restaurants
