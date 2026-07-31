import unittest

from src.geoapify import infer_name_tags, normalize_restaurant


class NameTagTests(unittest.TestCase):
    def test_sushi_name_adds_sushi_and_japanese_tags(self):
        self.assertEqual(
            infer_name_tags("Aoki Sushi & Grill"),
            ["sushi", "japanese"],
        )

    def test_keyword_must_be_a_complete_word(self):
        self.assertEqual(infer_name_tags("Taco"), ["taco", "mexican"])
        self.assertEqual(infer_name_tags("Tacoma Cafe"), [])


class NormalizeRestaurantTests(unittest.TestCase):
    def test_combines_api_cuisine_and_name_tags(self):
        feature = {
            "properties": {
                "place_id": "place-1",
                "name": "Aoki Sushi & Grill",
                "address_line2": "621 Broadway East, Seattle, WA 98102",
                "categories": [
                    "catering.restaurant",
                    "catering.restaurant.japanese",
                ],
                "catering": {"cuisine": "japanese"},
                "distance": 91,
                "website": "https://example.com",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-122.3211244, 47.6249184],
            },
        }

        restaurant = normalize_restaurant(feature)

        self.assertEqual(restaurant["api_cuisine"], ["japanese"])
        self.assertEqual(restaurant["name_tags"], ["sushi", "japanese"])
        self.assertEqual(
            restaurant["recommendation_tags"],
            ["japanese", "sushi"],
        )
        self.assertIsNone(restaurant["vegetarian"])
        self.assertIsNone(restaurant["vegan"])
        self.assertEqual(restaurant["latitude"], 47.6249184)
        self.assertEqual(restaurant["longitude"], -122.3211244)

    def test_preserves_unknown_diet_as_none(self):
        restaurant = normalize_restaurant(
            {
                "properties": {"name": "Unknown Cafe"},
                "geometry": {"coordinates": []},
            }
        )

        self.assertIsNone(restaurant["vegetarian"])
        self.assertIsNone(restaurant["vegan"])

    def test_reads_confirmed_vegetarian_value(self):
        restaurant = normalize_restaurant(
            {
                "properties": {
                    "name": "Cafe Lolo",
                    "categories": ["catering.restaurant", "vegetarian"],
                    "catering": {"diet": {"vegetarian": True}},
                }
            }
        )

        self.assertTrue(restaurant["vegetarian"])


if __name__ == "__main__":
    unittest.main()
