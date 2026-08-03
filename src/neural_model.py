import torch
from torch import nn


class NeuralRestaurantModel:
    def __init__(self, number_of_features):
        self.model = self.build_model(number_of_features)

    def build_model(self, number_of_features):
        """Create a small neural network that predicts Like probability."""
        return nn.Sequential(
            nn.Linear(number_of_features, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid(),
        )

    def train_model(self, features, labels):
        """Train the model on restaurant features and Like labels."""
        loss_function = nn.BCELoss()
        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=0.05,
        )

        for _ in range(300):
            optimizer.zero_grad()
            predictions = self.model(features)
            loss = loss_function(predictions, labels)
            loss.backward()
            optimizer.step()

        return loss.item()

    def predict_probabilities(self, features):
        """Return the model's predicted Like probability for each restaurant."""
        self.model.eval()
        with torch.no_grad():
            probabilities = self.model(features)
        return probabilities.flatten().tolist()

    def rank_restaurants_by_probability(self, restaurants, probabilities):
        """Attach Like probabilities and rank candidates from highest to lowest."""
        if len(restaurants) != len(probabilities):
            raise ValueError(
                "Each restaurant must have one predicted probability."
            )

        ranked_restaurants = []
        for restaurant, probability in zip(restaurants, probabilities):
            ranked_restaurant = dict(restaurant)
            ranked_restaurant["predicted_probability"] = probability
            ranked_restaurants.append(ranked_restaurant)

        ranked_restaurants.sort(
            key=lambda restaurant: (
                -restaurant["predicted_probability"],
                restaurant.get("distance_meters") is None,
                restaurant.get("distance_meters") or 0,
            )
        )
        return ranked_restaurants
