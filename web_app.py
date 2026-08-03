import os

from flask import Flask, jsonify, render_template, request

from src.feedback import list_feedback, save_feedback
from src.geoapify import GeoapifyError, find_nearby_restaurants
from src.neural_recommender import (
    rank_restaurants_with_recommender,
    train_recommender,
)


app = Flask(__name__)
app.config["DATABASE_PATH"] = os.path.join(app.instance_path, "feedback.db")

CAPITOL_HILL_LATITUDE = 47.6253
CAPITOL_HILL_LONGITUDE = -122.3222


@app.get("/")
def index():
    try:
        restaurants = find_nearby_restaurants(
            CAPITOL_HILL_LATITUDE,
            CAPITOL_HILL_LONGITUDE,
            limit=10,
        )
    except GeoapifyError as error:
        return render_template("index.html", restaurants=[], error=str(error)), 502

    os.makedirs(os.path.dirname(app.config["DATABASE_PATH"]), exist_ok=True)
    feedback_rows = list_feedback(app.config["DATABASE_PATH"])
    try:
        recommender, vocabulary, _ = train_recommender(feedback_rows)
        restaurants = rank_restaurants_with_recommender(
            recommender,
            vocabulary,
            restaurants,
        )
    except ValueError:
        restaurants = sorted(
            restaurants,
            key=lambda restaurant: (
                restaurant.get("distance_meters") is None,
                restaurant.get("distance_meters") or 0,
            ),
        )

    return render_template("index.html", restaurants=restaurants, error=None)


@app.post("/api/feedback")
def create_feedback():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Request body must be JSON."), 400

    place_id = data.get("place_id")
    restaurant_name = data.get("restaurant_name")
    liked = data.get("liked")
    recommendation_tags = data.get("recommendation_tags", [])

    if not isinstance(place_id, str) or not place_id.strip():
        return jsonify(error="place_id is required."), 400
    if not isinstance(restaurant_name, str) or not restaurant_name.strip():
        return jsonify(error="restaurant_name is required."), 400
    if not isinstance(liked, bool):
        return jsonify(error="liked must be true or false."), 400
    if not isinstance(recommendation_tags, list) or not all(
        isinstance(tag, str) for tag in recommendation_tags
    ):
        return jsonify(error="recommendation_tags must be a list of strings."), 400

    os.makedirs(os.path.dirname(app.config["DATABASE_PATH"]), exist_ok=True)
    feedback_id = save_feedback(
        app.config["DATABASE_PATH"],
        place_id.strip(),
        restaurant_name.strip(),
        liked,
        recommendation_tags,
    )

    return jsonify(id=feedback_id, saved=True), 201


if __name__ == "__main__":
    app.run(debug=True)
