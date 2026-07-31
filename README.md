# Restaurant Recommendation App

This project is a hands-on way to learn PyTorch and a few supporting machine learning tools by building a small restaurant recommendation app.

## What the app does

- Builds a small synthetic dataset of restaurants and preference profiles.
- Trains a simple neural network with PyTorch.
- Uses your preferences to score restaurants and suggest the best matches.

## Learning goals

1. Understand how a machine learning project is structured.
2. See how data is turned into features for a model.
3. Learn the difference between training, validation, and prediction.
4. Practice building an app that makes decisions from your own preferences.

## Project structure

- `src/recommender.py`: data generation, feature engineering, model training, and recommendations.
- `app.py`: command-line interface for entering your preferences and getting suggestions.
- `requirements.txt`: Python libraries used by the app.

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py --vegetarian --spicy --max-distance 4.0 --min-rating 4.2
```

## What to learn next

- Why we encode categorical values like cuisine and ambiance.
- Why we split data into training and test sets.
- How loss functions and optimizers work in PyTorch.
- How to replace the synthetic data with a real dataset later.
