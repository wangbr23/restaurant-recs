const dataElement = document.querySelector("#restaurant-data");

if (dataElement) {
  const restaurants = JSON.parse(dataElement.textContent);
  const card = document.querySelector("[data-restaurant-card]");
  const completion = document.querySelector("[data-completion]");
  const nameElement = card.querySelector("[data-name]");
  const cuisinesElement = card.querySelector("[data-cuisines]");
  const distanceElement = card.querySelector("[data-distance]");
  const addressElement = card.querySelector("[data-address]");
  const vegetarianElement = card.querySelector("[data-vegetarian]");
  const progressElement = card.querySelector("[data-progress]");
  const statusElement = card.querySelector("[data-feedback-status]");
  const choiceButtons = card.querySelectorAll("[data-choice]");
  let currentIndex = 0;

  function titleCase(value) {
    return value
      .replaceAll("_", " ")
      .replace(/\b\w/g, (character) => character.toUpperCase());
  }

  function renderCuisines(cuisines) {
    cuisinesElement.replaceChildren();
    cuisinesElement.classList.toggle("muted", cuisines.length === 0);

    if (cuisines.length === 0) {
      cuisinesElement.textContent = "Cuisine details unavailable";
      return;
    }

    cuisines.forEach((cuisine) => {
      const tag = document.createElement("span");
      tag.textContent = titleCase(cuisine);
      cuisinesElement.append(tag);
    });
  }

  function renderRestaurant(restaurant) {
    nameElement.textContent = restaurant.name;
    renderCuisines(restaurant.api_cuisine);

    distanceElement.textContent =
      restaurant.distance_meters == null
        ? "Distance unavailable"
        : `${Math.round(restaurant.distance_meters * 3.28084)} ft away`;

    addressElement.textContent = restaurant.address
      ? restaurant.address.split(",")[0]
      : "Address unavailable";

    vegetarianElement.hidden = restaurant.vegetarian !== true;
    progressElement.textContent = `Restaurant ${currentIndex + 1} of ${restaurants.length}`;
    statusElement.textContent = "Your choice will be saved locally.";
  }

  function showNextRestaurant() {
    currentIndex += 1;

    if (currentIndex >= restaurants.length) {
      card.hidden = true;
      completion.hidden = false;
      return;
    }

    renderRestaurant(restaurants[currentIndex]);
  }

  async function saveChoice(liked) {
    const restaurant = restaurants[currentIndex];
    choiceButtons.forEach((button) => {
      button.disabled = true;
    });
    statusElement.textContent = "Saving your choice…";

    try {
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          place_id: restaurant.place_id,
          restaurant_name: restaurant.name,
          liked,
          recommendation_tags: restaurant.recommendation_tags,
        }),
      });

      if (!response.ok) {
        throw new Error("Feedback was not saved.");
      }

      showNextRestaurant();
    } catch (error) {
      statusElement.textContent = "Could not save your choice. Please try again.";
    } finally {
      choiceButtons.forEach((button) => {
        button.disabled = false;
      });
    }
  }

  choiceButtons.forEach((button) => {
    button.addEventListener("click", () => {
      saveChoice(button.dataset.choice === "like");
    });
  });
}
