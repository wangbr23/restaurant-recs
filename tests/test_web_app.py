import os
import tempfile
import unittest
from unittest.mock import patch

from src.feedback import list_feedback, save_feedback
from web_app import app


class RestaurantPageTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.temporary_directory = tempfile.TemporaryDirectory()
        app.config["DATABASE_PATH"] = os.path.join(
            self.temporary_directory.name,
            "feedback.db",
        )
        self.client = app.test_client()

    def tearDown(self):
        self.temporary_directory.cleanup()

    @patch("web_app.find_nearby_restaurants")
    def test_page_displays_restaurant_card(self, find_restaurants):
        find_restaurants.return_value = [
            {
                "name": "Aoki Sushi & Grill",
                "place_id": "place-1",
                "api_cuisine": ["japanese"],
                "recommendation_tags": ["japanese", "sushi"],
                "distance_meters": 91,
                "address": "621 Broadway East, Seattle, WA 98102",
                "vegetarian": None,
            }
        ]

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Aoki Sushi &amp; Grill", response.data)
        self.assertIn(b"Japanese", response.data)
        self.assertIn(b"299 ft away", response.data)
        self.assertIn(b"621 Broadway East", response.data)
        self.assertIn(b"Not interested", response.data)
        self.assertIn(b"Like", response.data)
        self.assertIn(b"Restaurant 1 of 1", response.data)
        self.assertIn(b"restaurant-data", response.data)
        self.assertIn(b"Your choice will be saved locally", response.data)
        find_restaurants.assert_called_once_with(
            47.6253,
            -122.3222,
            limit=10,
        )

    def test_feedback_endpoint_saves_choice(self):
        response = self.client.post(
            "/api/feedback",
            json={
                "place_id": "place-1",
                "restaurant_name": "Aoki Sushi & Grill",
                "liked": True,
                "recommendation_tags": ["japanese", "sushi"],
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["saved"], True)
        self.assertEqual(
            list_feedback(app.config["DATABASE_PATH"])[0],
            {
                "id": 1,
                "place_id": "place-1",
                "restaurant_name": "Aoki Sushi & Grill",
                "liked": True,
                "recommendation_tags": ["japanese", "sushi"],
                "created_at": list_feedback(app.config["DATABASE_PATH"])[0][
                    "created_at"
                ],
            },
        )

    def test_feedback_endpoint_rejects_invalid_choice(self):
        response = self.client.post(
            "/api/feedback",
            json={"place_id": "place-1", "liked": "yes"},
        )

        self.assertEqual(response.status_code, 400)

    @patch("web_app.find_nearby_restaurants")
    def test_saved_preferences_change_restaurant_order(self, find_restaurants):
        find_restaurants.return_value = [
            {
                "name": "Nearby Pizza",
                "place_id": "pizza-1",
                "api_cuisine": ["italian"],
                "recommendation_tags": ["italian", "pizza"],
                "distance_meters": 50,
                "address": "1 Pine Street, Seattle, WA",
                "vegetarian": None,
            },
            {
                "name": "Aoki Sushi",
                "place_id": "sushi-1",
                "api_cuisine": ["japanese"],
                "recommendation_tags": ["japanese", "sushi"],
                "distance_meters": 500,
                "address": "2 Broadway East, Seattle, WA",
                "vegetarian": None,
            },
        ]
        save_feedback(
            app.config["DATABASE_PATH"],
            "previous-sushi",
            "Previous Sushi Restaurant",
            True,
            ["japanese", "sushi"],
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertLess(
            response.data.index(b"Aoki Sushi"),
            response.data.index(b"Nearby Pizza"),
        )


if __name__ == "__main__":
    unittest.main()
