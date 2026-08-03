# Restaurant Recommender

A learning project that builds a personal restaurant recommender from real nearby restaurant data and Like/Not interested feedback.

The application retrieves restaurants around Capitol Hill, Seattle from Geoapify, derives cuisine tags, stores feedback in SQLite, trains a small PyTorch neural network, and orders the current restaurant cards by predicted Like probability.

This is intentionally a small educational system. The model is useful for learning the complete recommendation pipeline, but the current dataset is too small to treat its predictions as reliable.

## What currently works

- Retrieves nearby restaurants from the Geoapify Places API.
- Normalizes inconsistent API responses into one restaurant structure.
- Combines confirmed cuisine data with explainable tags inferred from restaurant names.
- Shows restaurant cards in a minimal Flask interface.
- Saves Like and Not interested choices to a local SQLite database.
- Converts restaurant tags into PyTorch feature tensors.
- Trains a small neural network from saved feedback.
- Predicts a Like probability for each restaurant.
- Sorts restaurants by predicted probability, with distance as a tie-breaker.
- Retrains the model whenever the restaurant page is refreshed.
- Falls back to distance ordering when there is not enough tagged feedback to train.

## Application flow

```text
Browser requests /
        |
        v
Flask requests nearby restaurants from Geoapify
        |
        v
Geoapify responses are normalized and tagged
        |
        +-----------------------------+
        |                             |
        v                             v
Read feedback from SQLite      Current restaurants
        |                             |
        v                             |
Build tag vocabulary                 |
        |                             |
        v                             |
Build training tensors               |
        |                             |
        v                             |
Create and train neural network       |
        |                             |
        +-------------+---------------+
                      |
                      v
          Encode current restaurants
                      |
                      v
          Predict Like probabilities
                      |
                      v
       Rank by probability, then distance
                      |
                      v
              Render restaurant cards
                      |
                      v
             User chooses Like/Dislike
                      |
                      v
          POST /api/feedback -> SQLite
```

Feedback collected during a card session is saved immediately. It affects the model after the next page refresh, when Flask trains a new model from the complete feedback table.

## Architecture

The project is a single Python application with a small HTML/CSS/JavaScript frontend.

```text
restaurant-recs/
├── web_app.py                  Flask routes and application orchestration
├── discover_restaurants.py    Command-line Geoapify inspection tool
├── show_feedback.py           Command-line SQLite feedback viewer
├── requirements.txt           Python dependencies
├── .env.example               Environment variable template
├── templates/
│   └── index.html             Server-rendered restaurant card
├── static/
│   ├── app.js                 Card navigation and feedback requests
│   └── styles.css             Minimal interface styling
├── src/
│   ├── geoapify.py            API client, normalization, and name tags
│   ├── feedback.py            SQLite persistence
│   ├── neural_features.py     Vocabulary and tensor construction
│   ├── neural_model.py        PyTorch model, training, prediction, ranking
│   ├── neural_recommender.py  Training and ranking orchestration
│   ├── preferences.py         Earlier rule-based recommendation baseline
│   ├── experiment.py          Unseen-pool and 20/30 split utilities
│   └── constants/
│       └── tags.py            Explainable restaurant-name keyword rules
├── tests/                     Unit and Flask endpoint tests
└── instance/
    └── feedback.db            Local generated database; ignored by Git
```

### Backend

Flask serves the page and owns all access to the Geoapify key and SQLite database. The browser never receives the API key.

Routes:

| Route | Method | Purpose |
|---|---|---|
| `/` | `GET` | Fetch, train, rank, and render restaurant cards |
| `/api/feedback` | `POST` | Validate and save one Like/Not interested choice |

### Frontend

The frontend uses server-rendered HTML and a small amount of plain JavaScript. No Node or frontend build system is required.

The browser receives the ranked restaurant records, displays one card at a time, and sends feedback before advancing. Buttons are temporarily disabled while a choice is being saved. Feedback is not used to reorder the remaining cards until the page is refreshed.

### External restaurant data

`src/geoapify.py` calls the Geoapify Places API with a restaurant category, a coordinate, and a radius. The current web application uses fixed coordinates in Capitol Hill, Seattle and requests 10 restaurants within a 5 km radius.

Each response is normalized to a structure similar to:

```python
{
    "place_id": "...",
    "name": "Aoki Sushi & Grill",
    "distance_meters": 91,
    "address": "621 Broadway East, Seattle, WA 98102",
    "latitude": 47.6249184,
    "longitude": -122.3211244,
    "api_cuisine": ["japanese"],
    "name_tags": ["sushi", "japanese"],
    "recommendation_tags": ["japanese", "sushi"],
    "vegetarian": None,
    "vegan": None,
    "website": "https://example.com",
    "opening_hours": None,
}
```

`api_cuisine` contains Geoapify/OpenStreetMap cuisine data. `name_tags` contains explainable keyword matches from the restaurant name. `recommendation_tags` combines the two without duplicates.

Missing dietary data remains `None`; missing information is not treated as `False`.

## Feedback storage

Feedback is stored in `instance/feedback.db` using Python's built-in SQLite support.

The current table contains:

| Column | Meaning |
|---|---|
| `id` | Local auto-incrementing event ID |
| `place_id` | Geoapify place identifier |
| `restaurant_name` | Name shown when the choice was made |
| `liked` | `1` for Like, `0` for Not interested |
| `recommendation_tags` | JSON list of tags used as model features |
| `created_at` | UTC timestamp |

The database is local, generated at runtime, and excluded from Git.

Inspect saved feedback with:

```bash
.venv/bin/python show_feedback.py
```

## Neural-network pipeline

### 1. Build a vocabulary

`build_tag_vocabulary()` creates a sorted list of tags found in rated restaurants:

```python
["american", "burger", "italian", "japanese", "sushi", "thai"]
```

Only tags from labeled feedback are included. A candidate-only tag is ignored until a restaurant with that tag receives feedback. This prevents untrained input weights from affecting predictions.

The vocabulary order defines the meaning of every model input position and must remain identical during training and prediction.

### 2. Encode restaurants

`encode_restaurant_tags()` converts tags into a multi-hot vector. With this vocabulary:

```python
["italian", "japanese", "sushi", "thai"]
```

a Japanese sushi restaurant becomes:

```python
[0.0, 1.0, 1.0, 0.0]
```

`build_feedback_tensors()` creates labeled training tensors. `build_restaurant_tensor()` creates unlabeled candidate tensors using the same vocabulary.

### 3. Build the model

`NeuralRestaurantModel` creates this network:

```text
N tag inputs
      |
      v
8-neuron linear layer
      |
      v
ReLU activation
      |
      v
1-neuron linear layer
      |
      v
Sigmoid -> Like probability from 0 to 1
```

`N` is the number of tags in the current training vocabulary.

### 4. Train

The model uses:

- Binary cross-entropy loss (`BCELoss`)
- Adam optimizer
- Learning rate `0.05`
- 300 training iterations
- Fixed PyTorch seed `42`

The label is:

```text
Like             = 1.0
Not interested   = 0.0
```

`train_recommender()` coordinates vocabulary creation, tensor creation, model construction, and training.

### 5. Predict and rank

`rank_restaurants_with_recommender()` encodes current restaurants, predicts one Like probability per restaurant, and ranks them from highest to lowest probability. Distance breaks probability ties, with unknown distances placed last.

The probability is currently included in the data rendered to the browser but is not displayed on the card.

## Rule-based baseline

`src/preferences.py` contains the earlier explainable baseline:

```text
Like a tag             -> +1
Not interested in tag -> -1
```

The Flask page no longer uses this baseline for ranking, but it remains useful for comparing a simple deterministic approach with the neural network.

## Experiment utilities

`src/experiment.py` contains utilities for a planned evaluation flow:

- Calculate how many places to request after accounting for reviewed places.
- Remove restaurants already present in feedback.
- Reproducibly split 50 restaurants into 20 rating examples and 30 held-back candidates.

These utilities are implemented but are not currently connected to Flask. The current page continues to fetch and rank 10 restaurants.

## Setup

Requirements:

- Python 3.8 or newer
- A Geoapify API key

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the local environment file:

```bash
cp .env.example .env
```

Then add the key to `.env`:

```env
GEOAPIFY_API_KEY=your_key_here
```

Do not commit `.env`. For deployment, configure `GEOAPIFY_API_KEY` as a server-side environment variable in the hosting platform.

## Running the application

Start Flask:

```bash
.venv/bin/flask --app web_app run
```

Open:

```text
http://127.0.0.1:5000
```

The first visit with an empty database uses distance ordering. After tagged feedback exists, refreshing trains the neural model and applies its ranking.

To inspect raw normalized Geoapify records for the fixed Capitol Hill location:

```bash
.venv/bin/python discover_restaurants.py
```

## Running tests

Run the complete test suite:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The tests cover:

- Name-based tag inference
- Geoapify record normalization
- Vocabulary and multi-hot encoding
- Training tensor construction
- Rule-based baseline behavior
- Feedback validation and SQLite persistence
- Flask page rendering
- Neural ranking integration

## Current limitations

- The dataset is very small, so the neural network can overfit and produce unjustifiably extreme probabilities.
- Training loss on previously seen records does not measure performance on unseen restaurants.
- Restaurants are represented only by recommendation tags. Distance is used as a ranking tie-breaker but is not a neural-network input.
- Restaurants with identical tags are indistinguishable to the model.
- Restaurants without known training tags become all-zero feature vectors.
- Duplicate feedback rows influence training multiple times.
- The model retrains from scratch on every page refresh and is not saved.
- The page uses fixed Capitol Hill coordinates rather than browser location.
- The current page may show restaurants that were previously reviewed.
- The 20/30 held-out evaluation experiment is not connected yet.
- Predicted probabilities are not calibrated and should not be interpreted as trustworthy percentages with this amount of data.

## Suggested next steps

1. Display the model's predicted probability on each card for inspection.
2. Add a held-out recommendation round and calculate Precision@5.
3. Compare neural ranking against the rule-based baseline.
4. Add distance, dietary status, and other reliable fields as model features.
5. Prevent repeated ratings or define how duplicate feedback should be weighted.
6. Save the trained model and its vocabulary instead of retraining on every request.
7. Replace fixed coordinates with user-approved location input.

## Data and attribution

Restaurant data comes from Geoapify and OpenStreetMap. The interface includes OpenStreetMap attribution. Review Geoapify's current pricing, attribution, caching, and usage terms before deploying publicly.

The API key is loaded server-side from `GEOAPIFY_API_KEY`; it is not embedded in frontend JavaScript.
