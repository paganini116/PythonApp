import os

from openai import OpenAI


DEFAULT_MODEL = "gpt-5.2"


def get_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment.")
    return api_key


def build_prompt(
    person1_food: str,
    person2_food: str,
    city: str,
    budget: int,
) -> str:
    return (
        "Suggest exactly 3 date spot ideas in the provided city.\n"
        "Use the two food preferences and total budget to balance the choices.\n"
        "For each suggestion, include:\n"
        "1. Venue name or venue concept\n"
        "2. A one-sentence reason it fits both people\n"
        "3. A short budget note\n"
        "Keep the response concise, practical, and easy to scan.\n\n"
        f"Person 1 food preference: {person1_food}\n"
        f"Person 2 food preference: {person2_food}\n"
        f"City: {city}\n"
        f"Total budget: ${budget}"
    )


def suggest_date_spots(
    person1_food: str,
    person2_food: str,
    city: str,
    budget: int,
    model: str | None = None,
) -> str:
    get_api_key()
    client = OpenAI()
    response = client.chat.completions.create(
        model=model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        messages=[
            {
                "role": "system",
                "content": (
                    "You recommend concise, practical date spots based on food "
                    "preferences, city, and budget."
                ),
            },
            {
                "role": "user",
                "content": build_prompt(person1_food, person2_food, city, budget),
            },
        ],
    )
    return response.choices[0].message.content.strip()
