import torch


def build_tag_vocabulary(records):
    """Return a stable, sorted list of tags found in restaurant records."""
    tags = {
        tag.strip().lower()
        for record in records
        for tag in record.get("recommendation_tags", [])
        if isinstance(tag, str) and tag.strip()
    }
    return sorted(tags)


def encode_restaurant_tags(record, vocabulary):
    """Encode restaurant tags as a multi-hot numeric feature vector."""
    restaurant_tags = {
        tag.strip().lower()
        for tag in record.get("recommendation_tags", [])
        if isinstance(tag, str) and tag.strip()
    }
    return [1.0 if tag in restaurant_tags else 0.0 for tag in vocabulary]


def build_feedback_tensors(feedback_rows, vocabulary):
    """Convert saved feedback into PyTorch feature and label tensors."""
    features = [
        encode_restaurant_tags(feedback, vocabulary)
        for feedback in feedback_rows
    ]
    labels = [[1.0 if feedback["liked"] else 0.0] for feedback in feedback_rows]

    if not feedback_rows:
        return (
            torch.empty((0, len(vocabulary)), dtype=torch.float32),
            torch.empty((0, 1), dtype=torch.float32),
        )

    return (
        torch.tensor(features, dtype=torch.float32),
        torch.tensor(labels, dtype=torch.float32),
    )
