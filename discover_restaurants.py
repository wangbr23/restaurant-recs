import json

from src.geoapify import GeoapifyError, find_nearby_restaurants


# Fixed Capitol Hill, Seattle location for the first API integration test.
LATITUDE = 47.6253
LONGITUDE = -122.3222


def main():
    try:
        restaurants = find_nearby_restaurants(
            LATITUDE,
            LONGITUDE,
            limit=3,
        )
    except GeoapifyError as error:
        raise SystemExit(error) from error

    print(json.dumps(restaurants, indent=2))


if __name__ == "__main__":
    main()
