# Learning Guide: Restaurant Recommendation App

This project is intentionally simple so you can focus on the core ideas behind machine learning.

## 1. What problem are we solving?

We want a model that can look at a restaurant and a set of preferences, then predict whether you would likely like that restaurant.

In machine learning terms:

- Input: restaurant features + preference features
- Output: a label of 1 (liked) or 0 (not liked)

## 2. What makes up the data?

The app builds a synthetic dataset from a few restaurant examples. Each row contains:

- categorical features such as cuisine, price level, and ambiance
- numeric features such as distance and rating
- boolean features such as vegetarian_friendly and spicy
- preference flags such as prefers_vegetarian and prefers_spicy

The label is `liked`, which tells the model whether the restaurant matches the preference profile.

## 3. Why do we encode categorical data?

Neural networks work with numbers, not words. That is why we convert values like:

- `cuisine = japanese`
- `price_level = moderate`
- `ambiance = quiet`

into numeric columns using one-hot encoding.

This is a key concept to understand because most real-world ML datasets also need preprocessing.

## 4. What does the model do?

The model is a small neural network built with PyTorch.

It has:

- an input layer that receives all of the feature values
- hidden layers that learn useful patterns
- an output layer that produces a probability between 0 and 1

If the output is close to 1, the model thinks the restaurant is a good match.

## 5. What happens during training?

Training happens in small steps.

For each batch of examples:

1. The model makes a prediction.
2. We compare the prediction to the true label with a loss function.
3. We compute gradients with backpropagation.
4. We update the model weights with an optimizer.

The core idea is simple:

- make a mistake
- measure the size of the mistake
- adjust the model to make fewer mistakes next time

## 6. How do we evaluate the model?

We split the data into training and test sets.

- The training data teaches the model.
- The test data checks whether the model can generalize to new examples.

This is important because a model that memorizes the training set may perform poorly on new data.

## 7. How does the app make recommendations?

Once the model is trained, the app scores each restaurant against your preferences.

It then ranks the restaurants and shows the highest-scoring matches.

## 8. What to learn next

Once this feels comfortable, the next step is to learn:

- how validation sets work
- how overfitting happens
- how to use real restaurant datasets
- how to build a more realistic recommender with embeddings and user history
