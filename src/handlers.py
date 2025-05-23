from telebot.states.sync import StateContext

from bot import bot
from state import MyStates
from telebot import types

from database import SearchHistory
from api import (
    search_movie,
    search_by_genre,
    search_by_rating,
    search_by_budget,
)
import datetime


@bot.message_handler(commands=["start"])
def send_welcome(message: types.Message):
    welcome_text = (
        "Добро пожаловать!\n\n"
        "Доступные команды:\n"
        "/start - Приветствие и список команд\n"
        "/help - Помощь\n"
        "/search - Поиск фильмов и сериалов\n"
        "/history - История поисковых запросов\n"
        "/cancel - Отмена текущей операции"
    )
    bot.send_message(message.chat.id, welcome_text)


@bot.message_handler(commands=["help"])
def send_help(message: types.Message):
    help_text = (
        "Список команд:\n"
        "/start - Запуск бота\n"
        "/help - Вывод справки\n"
        "/search - Поиск фильмов:\n"
        "         1. По названию\n"
        "         2. По жанру\n"
        "         3. По рейтингу\n"
        "         4. По бюджету\n"
        "/history - История поиска\n"
        "/cancel - Отмена операции"
    )
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(state="*", commands=["cancel"])
def cancel(message: types.Message, state: StateContext):
    state.delete()
    bot.send_message(
        message.chat.id,
        "Операция отменена. Нажмите /start для начала.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@bot.message_handler(commands=["search"])
def search_command(message: types.Message, state: StateContext):
    state.delete()
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("По названию"),
        types.KeyboardButton("По жанру"),
        types.KeyboardButton("По рейтингу"),
        types.KeyboardButton("По бюджету"),
    )
    bot.send_message(message.chat.id, "Выберите тип поиска:", reply_markup=keyboard)


@bot.message_handler(
    func=lambda message: message.text
    in ["По названию", "По жанру", "По рейтингу", "По бюджету"]
)
def search_type_selection(message: types.Message, state: StateContext):
    bot.send_message(
        message.chat.id,
        f"Вы выбрали: {message.text}",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    if message.text == "По названию":
        state.set(MyStates.movie)
        bot.send_message(message.chat.id, "Введите название фильма:")
    elif message.text == "По жанру":
        state.set(MyStates.genre)
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        genres_list = ["Комедия", "Ужасы", "Фантастика", "Драма", "Боевик"]
        keyboard.add(*[types.KeyboardButton(genre) for genre in genres_list])
        bot.send_message(message.chat.id, "Выберите жанр:", reply_markup=keyboard)
    elif message.text == "По рейтингу":
        state.set(MyStates.rating)
        bot.send_message(message.chat.id, "Введите рейтинг фильма:")
    elif message.text == "По бюджету":
        state.set(MyStates.budget)
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        keyboard.add("Высокий бюджет", "Низкий бюджет")
        bot.send_message(
            message.chat.id, "Выберите категорию бюджета:", reply_markup=keyboard
        )


@bot.message_handler(state=MyStates.movie)
def movie_get(message: types.Message, state: StateContext):
    state.set(MyStates.limit)
    state.add_data(movie=message.text)
    send_limit_selection(message)


@bot.message_handler(state=MyStates.genre)
def genre_get(message: types.Message, state: StateContext):
    state.set(MyStates.limit)
    state.add_data(genre=message.text)
    send_limit_selection(message)


@bot.message_handler(state=MyStates.rating)
def rating_get(message: types.Message, state: StateContext):
    state.set(MyStates.limit)
    state.add_data(rating=message.text)
    send_limit_selection(message)


@bot.message_handler(state=MyStates.budget)
def budget_get(message: types.Message, state: StateContext):
    budget_choice = message.text
    if budget_choice == "Высокий бюджет":
        state.add_data(budget=True)
    elif budget_choice == "Низкий бюджет":
        state.add_data(budget=False)
    else:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, выберите 'Высокий бюджет' или 'Низкий бюджет'.",
        )
        return

    state.set(MyStates.limit)
    send_limit_selection(message)


def send_limit_selection(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add("1", "3", "5", "10")
    bot.send_message(
        message.chat.id, "Выберите количество вариантов:", reply_markup=keyboard
    )


@bot.message_handler(state=MyStates.limit)
def finish(message: types.Message, state: StateContext):
    bot.send_message(
        message.chat.id,
        f"Вы выбрали количество: {message.text}",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    state.add_data(limit=int(message.text))
    with state.data() as data:
        limit = data.get("limit")
        if "movie" in data:
            result = search_movie(data.get("movie"), limit=limit)
        elif "genre" in data:
            result = search_by_genre(data.get("genre"), limit=limit)
        elif "rating" in data:
            result = search_by_rating(data.get("rating"), limit=limit)
        elif "budget" in data:
            result = search_by_budget(data.get("budget"), limit=limit)
        else:
            bot.send_message(message.chat.id, "Ошибка данных запроса.")
            state.delete()
            return

    if isinstance(result, str):
        bot.send_message(message.chat.id, result, parse_mode="HTML")
    else:
        for movie in result:
            budget_value = movie.get("budget", {}).get("value", "Нет данных")
            budget_currency = movie.get("budget", {}).get("currency", "")
            post = movie.get("poster", {}).get("url", "Нет данных")

            response = (
                f"Название: {movie['name']}\n"
                f"Описание: {movie['description']}\n"
                f"Рейтинг: {movie['rating']['kp']}\n"
                f"Год: {movie['year']}\n"
                f"Жанры: {', '.join(g['name'] for g in movie['genres'])}\n"
                f"Возрастной рейтинг: {movie['ageRating']}\n"
                f"Бюджет: {budget_value} {budget_currency}\n"
                f"Постер: {post}\n"
            )
            bot.send_message(message.chat.id, response, parse_mode="HTML")
            SearchHistory.create(
                date=datetime.datetime.now(),
                title=movie["name"],
                description=movie["description"],
                rating=movie["rating"]["kp"],
                year=movie["year"],
                genres=", ".join(g["name"] for g in movie["genres"]),
                age_rating=movie.get("ageRating"),
                budget=f"{budget_value} {budget_currency}",
                poster=f"{post}",
            )
    state.delete()


@bot.message_handler(commands=["history"])
def view_history(message: types.Message):
    query = SearchHistory.select().order_by(SearchHistory.date.desc())
    if not query.exists():
        bot.send_message(message.chat.id, "История поиска пуста.")
        return
    for entry in query:
        response = (
            f"Дата: {entry.date}\n"
            f"Название: {entry.title}\n"
            f"Описание: {entry.description}\n"
            f"Рейтинг: {entry.rating}\n"
            f"Год: {entry.year}\n"
            f"Жанры: {entry.genres}\n"
            f"Возрастной рейтинг: {entry.age_rating}\n"
            f"Бюджет: {entry.budget}\n"
            f"Постер: {entry.poster}\n"
        )
        bot.send_message(message.chat.id, response)
