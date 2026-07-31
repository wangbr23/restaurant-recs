from src.model import predict_single_row, train_model

model = train_model()

example = {
    "vegetarian_friendly": 1,
    "spicy": 0,
    "late_night": 0,
    "distance": 2.0,
    "rating": 4.7,
}

prediction = predict_single_row(model, example)
print(f"Prediction: {prediction:.3f}")
