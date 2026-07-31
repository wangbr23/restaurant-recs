import unittest
from unittest.mock import patch

from web_app import app


class RestaurantPageTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    @patch("web_app.find_nearby_restaurants")
    def test_page_displays_restaurant_card(self, find_restaurants):
        find_restaurants.return_value = [
            {
                "name": "Aoki Sushi & Grill",
                "api_cuisine": ["japanese"],
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


if __name__ == "__main__":
    unittest.main()
