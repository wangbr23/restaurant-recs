from flask import Flask, render_template

from src.geoapify import GeoapifyError, find_nearby_restaurants


app = Flask(__name__)

CAPITOL_HILL_LATITUDE = 47.6253
CAPITOL_HILL_LONGITUDE = -122.3222


@app.get("/")
def index():
    try:
        restaurants = find_nearby_restaurants(
            CAPITOL_HILL_LATITUDE,
            CAPITOL_HILL_LONGITUDE,
            limit=3,
        )
    except GeoapifyError as error:
        return render_template("index.html", restaurant=None, error=str(error)), 502

    restaurant = restaurants[0] if restaurants else None
    return render_template("index.html", restaurant=restaurant, error=None)


if __name__ == "__main__":
    app.run(debug=True)
