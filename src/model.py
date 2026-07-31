import torch
from torch import nn

from src.training_data import TRAINING_ROWS

# Features we will use as input to the model
FEATURES = ["vegetarian_friendly", "spicy", "late_night", "distance", "rating"]


def build_training_tensors():
    # Convert the training rows into tensors that PyTorch can use
    x = []
    y = []

    for row in TRAINING_ROWS:
        features = [row[feature] for feature in FEATURES]
        x.append(features)
        y.append([row["liked"]])

    x_tensor = torch.tensor(x, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    return x_tensor, y_tensor


def build_model():
    # A tiny neural network:
    # input -> hidden layer -> output
    model = nn.Sequential(
        nn.Linear(len(FEATURES), 8),
        nn.ReLU(),
        nn.Linear(8, 1),
        nn.Sigmoid(),
    )
    return model


def train_model():
    x, y = build_training_tensors()
    model = build_model()

    loss_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.05)

    for _ in range(300):
        optimizer.zero_grad()
        predictions = model(x)
        loss = loss_fn(predictions, y)
        loss.backward()
        optimizer.step()

    return model


def predict_single_row(model, row):
    # row is a dictionary with the same feature names
    features = [row[feature] for feature in FEATURES]
    x = torch.tensor([features], dtype=torch.float32)
    with torch.no_grad():
        prediction = model(x).item()
    return prediction
