from src.model import RestaurantModel

example = {
    "vegetarian_friendly": 1,
    "spicy": 0,
    "late_night": 0,
    "distance": 2.0,
    "rating": 4.7,
}

model = RestaurantModel()
prediction = model.predict_single_row(example)
accuracy, predictions, labels = model.evaluate_model()

print(f"Prediction for example: {prediction:.3f}")
print(f"Accuracy on training examples: {accuracy:.2%}")

for index, (pred, label) in enumerate(zip(predictions, labels)):
    predicted_label = 1 if pred >= 0.5 else 0
    true_label = int(label.item())
    print(f"Example {index + 1}: predicted={predicted_label}, true={true_label}, score={pred.item():.3f}")
