# Step 2: tiny training table for a simple learning model
# Each row is one example:
# - features about the restaurant and the preference context
# - a label: 1 means liked, 0 means not liked

TRAINING_ROWS = [
    {
        "vegetarian_friendly": 1,
        "spicy": 0,
        "late_night": 0,
        "distance": 2.0,
        "rating": 4.7,
        "liked": 1,
    },
    {
        "vegetarian_friendly": 0,
        "spicy": 1,
        "late_night": 0,
        "distance": 2.0,
        "rating": 4.7,
        "liked": 1,
    },
    {
        "vegetarian_friendly": 1,
        "spicy": 0,
        "late_night": 0,
        "distance": 5.0,
        "rating": 3.8,
        "liked": 0,
    },
    {
        "vegetarian_friendly": 0,
        "spicy": 1,
        "late_night": 1,
        "distance": 1.5,
        "rating": 4.8,
        "liked": 1,
    },
    {
        "vegetarian_friendly": 0,
        "spicy": 0,
        "late_night": 0,
        "distance": 4.5,
        "rating": 3.9,
        "liked": 0,
    },
]
