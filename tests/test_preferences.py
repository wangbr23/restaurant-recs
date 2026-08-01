import unittest

from src.preferences import (
    build_preference_profile,
    rank_restaurants_for_profile,
    score_restaurant_for_profile,
)


class PreferenceProfileTests(unittest.TestCase):
    def test_builds_profile_from_likes_and_dislikes(self):
        feedback = [
            {
                "liked": True,
                "recommendation_tags": ["japanese", "sushi"],
            },
            {
                "liked": False,
                "recommendation_tags": ["italian", "pizza"],
            },
        ]

        self.assertEqual(
            build_preference_profile(feedback),
            {
                "japanese": 1,
                "sushi": 1,
                "italian": -1,
                "pizza": -1,
            },
        )

    def test_accumulates_repeated_tag_choices(self):
        feedback = [
            {"liked": True, "recommendation_tags": ["japanese"]},
            {"liked": True, "recommendation_tags": ["japanese", "sushi"]},
            {"liked": False, "recommendation_tags": ["japanese"]},
        ]

        self.assertEqual(
            build_preference_profile(feedback),
            {"japanese": 1, "sushi": 1},
        )

    def test_counts_duplicate_tag_only_once_per_restaurant(self):
        feedback = [
            {
                "liked": True,
                "recommendation_tags": ["sushi", "Sushi", " sushi "],
            }
        ]

        self.assertEqual(build_preference_profile(feedback), {"sushi": 1})

    def test_empty_feedback_creates_empty_profile(self):
        self.assertEqual(build_preference_profile([]), {})


class RestaurantPreferenceScoreTests(unittest.TestCase):
    def test_sums_matching_positive_tag_scores(self):
        restaurant = {"recommendation_tags": ["japanese", "sushi"]}
        profile = {"japanese": 2, "sushi": 1, "italian": -1}

        self.assertEqual(
            score_restaurant_for_profile(restaurant, profile),
            3,
        )

    def test_includes_negative_tag_scores(self):
        restaurant = {"recommendation_tags": ["italian", "pizza"]}
        profile = {"italian": -1, "pizza": -2}

        self.assertEqual(
            score_restaurant_for_profile(restaurant, profile),
            -3,
        )

    def test_unseen_or_missing_tags_score_zero(self):
        profile = {"japanese": 2}

        self.assertEqual(
            score_restaurant_for_profile(
                {"recommendation_tags": ["mexican"]},
                profile,
            ),
            0,
        )
        self.assertEqual(score_restaurant_for_profile({}, profile), 0)

    def test_duplicate_tags_are_scored_once(self):
        restaurant = {
            "recommendation_tags": ["sushi", "Sushi", " sushi "]
        }
        profile = {"sushi": 2}

        self.assertEqual(
            score_restaurant_for_profile(restaurant, profile),
            2,
        )


class RestaurantRankingTests(unittest.TestCase):
    def test_orders_by_preference_score_before_distance(self):
        restaurants = [
            {
                "name": "Nearby Pizza",
                "recommendation_tags": ["pizza", "italian"],
                "distance_meters": 50,
            },
            {
                "name": "Aoki Sushi",
                "recommendation_tags": ["japanese", "sushi"],
                "distance_meters": 500,
            },
        ]
        profile = {"japanese": 2, "sushi": 1, "pizza": -1}

        ranked = rank_restaurants_for_profile(restaurants, profile)

        self.assertEqual(
            [restaurant["name"] for restaurant in ranked],
            ["Aoki Sushi", "Nearby Pizza"],
        )
        self.assertEqual(
            [restaurant["preference_score"] for restaurant in ranked],
            [3, -1],
        )

    def test_uses_distance_to_break_equal_scores(self):
        restaurants = [
            {
                "name": "Farther Sushi",
                "recommendation_tags": ["sushi"],
                "distance_meters": 500,
            },
            {
                "name": "Nearby Sushi",
                "recommendation_tags": ["sushi"],
                "distance_meters": 100,
            },
            {
                "name": "Unknown Distance Sushi",
                "recommendation_tags": ["sushi"],
                "distance_meters": None,
            },
        ]

        ranked = rank_restaurants_for_profile(restaurants, {"sushi": 1})

        self.assertEqual(
            [restaurant["name"] for restaurant in ranked],
            ["Nearby Sushi", "Farther Sushi", "Unknown Distance Sushi"],
        )

    def test_does_not_modify_original_restaurant_records(self):
        restaurants = [
            {
                "name": "Aoki Sushi",
                "recommendation_tags": ["sushi"],
                "distance_meters": 100,
            }
        ]

        rank_restaurants_for_profile(restaurants, {"sushi": 1})

        self.assertNotIn("preference_score", restaurants[0])


if __name__ == "__main__":
    unittest.main()
