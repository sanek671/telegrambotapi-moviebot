from telebot import states


class MyStates(states.StatesGroup):
    movie = states.State()
    genre = states.State()
    rating = states.State()
    budget = states.State()
    limit = states.State()
