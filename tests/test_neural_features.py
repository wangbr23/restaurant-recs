import unittest

import torch

from src.neural_features import (
    build_feedback_tensors,
    build_tag_vocabulary,
    encode_restaurant_tags,
)


class TagVocabularyTests(unittest.TestCase):
    def test_builds_normalized_stable_vocabulary(self):
        records = [
            {"recommendation_tags": ["Sushi", "japanese"]},
            {"recommendation_tags": [" thai ", "sushi"]},
        ]

        self.assertEqual(
            build_tag_vocabulary(records),
            ["japanese", "sushi", "thai"],
        )


class RestaurantEncodingTests(unittest.TestCase):
    def test_encodes_tags_as_multi_hot_vector(self):
        vocabulary = ["italian", "japanese", "sushi", "thai"]

        encoded = encode_restaurant_tags(
            {"recommendation_tags": ["japanese", "sushi"]},
            vocabulary,
        )

        self.assertEqual(encoded, [0.0, 1.0, 1.0, 0.0])

    def test_ignores_tags_outside_vocabulary(self):
        self.assertEqual(
            encode_restaurant_tags(
                {"recommendation_tags": ["vietnamese"]},
                ["italian", "thai"],
            ),
            [0.0, 0.0],
        )


class FeedbackTensorTests(unittest.TestCase):
    def test_builds_feature_and_label_tensors(self):
        feedback = [
            {
                "recommendation_tags": ["japanese", "sushi"],
                "liked": True,
            },
            {
                "recommendation_tags": ["italian"],
                "liked": False,
            },
        ]
        vocabulary = ["italian", "japanese", "sushi"]

        features, labels = build_feedback_tensors(feedback, vocabulary)

        self.assertTrue(
            torch.equal(
                features,
                torch.tensor(
                    [
                        [0.0, 1.0, 1.0],
                        [1.0, 0.0, 0.0],
                    ]
                ),
            )
        )
        self.assertTrue(
            torch.equal(labels, torch.tensor([[1.0], [0.0]]))
        )

    def test_empty_feedback_has_predictable_tensor_shapes(self):
        features, labels = build_feedback_tensors([], ["sushi", "thai"])

        self.assertEqual(tuple(features.shape), (0, 2))
        self.assertEqual(tuple(labels.shape), (0, 1))


if __name__ == "__main__":
    unittest.main()
