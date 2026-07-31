import argparse

from src.recommender import RESTAURANTS, build_preferences, recommend_restaurants


def main():
    parser = argparse.ArgumentParser(description="Recommend restaurants with simple rule-based scoring")
    parser.add_argument("--vegetarian", action="store_true", help="Prefer vegetarian-friendly restaurants")
    parser.add_argument("--spicy", action="store_true", help="Prefer spicy food")
    parser.add_argument("--late-night", action="store_true", help="Prefer late-night options")
    parser.add_argument("--max-distance", type=float, default=4.0, help="Maximum acceptable distance")
    parser.add_argument("--min-rating", type=float, default=4.0, help="Minimum acceptable rating")
    parser.add_argument("--top-n", type=int, default=5, help="Number of restaurants to display")
    args = parser.parse_args()

    preferences = build_preferences(args)
    recommendations = recommend_restaurants(RESTAURANTS, preferences, top_n=args.top_n)

    print("Your top restaurant picks:")
    for name, score, reasons in recommendations:
        print(f"- {name}: score {score}")
        if reasons:
            print(f"  reasons: {', '.join(reasons)}")
        else:
            print("  reasons: no matching preferences")


if __name__ == "__main__":
    main()
