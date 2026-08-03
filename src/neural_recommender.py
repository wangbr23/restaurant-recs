import torch

from src.neural_features import (
    build_feedback_tensors,
    build_restaurant_tensor,
    build_tag_vocabulary,
)
from src.neural_model import NeuralRestaurantModel


def train_recommender(feedback_rows):
    """Build and train a neural recommender from saved feedback."""
    if not feedback_rows:
        raise ValueError("Feedback is required to train the recommender.")

    vocabulary = build_tag_vocabulary(feedback_rows)
    if not vocabulary:
        raise ValueError("Feedback must contain at least one recommendation tag.")

    features, labels = build_feedback_tensors(feedback_rows, vocabulary)
    torch.manual_seed(42)
    recommender = NeuralRestaurantModel(len(vocabulary))
    final_loss = recommender.train_model(features, labels)

    return recommender, vocabulary, final_loss


def rank_restaurants_with_recommender(
    recommender,
    vocabulary,
    restaurants,
):
    """Predict Like probabilities and rank candidate restaurants."""
    if not restaurants:
        return []

    candidate_features = build_restaurant_tensor(restaurants, vocabulary)
    probabilities = recommender.predict_probabilities(candidate_features)
    return recommender.rank_restaurants_by_probability(
        restaurants,
        probabilities,
    )
