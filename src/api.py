import json
import requests
from config import API_KEY

BASE_URL = "https://api.kinopoisk.dev/v1.4"


def search_movie(movie, limit=3):
    """
    Поиск фильма по названию.
    """
    url = f"{BASE_URL}/movie/search"
    params = {"query": movie, "token": API_KEY, "limit": limit}

    try:
        response = requests.get(url, params=params)

        response.raise_for_status()
        data = json.loads(response.text)
        return data["docs"]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return []


def search_by_genre(genre, limit=3):
    """
    Функция для поиска фильмов по жанру.
    """
    url = f"{BASE_URL}/movie/search"
    params = {
        "limit": limit,
        "token": API_KEY,
        "query": genre,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = json.loads(response.text)
        return data.get("docs", [])
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        return []


def search_by_rating(rating, limit=3):
    """
    Функция для поиска фильмов по рейтингу.
    """
    url = f"{BASE_URL}/movie"
    params = {
        "limit": limit,
        "token": API_KEY,
        "rating.kp": rating.strip(),
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("docs", [])
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        return []


def search_by_budget(is_high_budget, limit=3):
    """
    Получение фильмов по бюджету.
    """
    url = f"{BASE_URL}/movie"
    budget = 100000000 if is_high_budget else 10000000
    params = {
        "budget.value": budget,
        "token": API_KEY,
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("docs", [])
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе данных: {e}")
        return []
