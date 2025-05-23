import telebot
from telebot import custom_filters
from telebot.storage import StateMemoryStorage

from config import BOT_TOKEN, API_KEY

API = API_KEY
bot = telebot.TeleBot(
    BOT_TOKEN,
    state_storage=StateMemoryStorage(),
    use_class_middlewares=True,
)

bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
bot.add_custom_filter(custom_filters.TextMatchFilter())

from telebot.states.sync.middleware import StateMiddleware

bot.setup_middleware(StateMiddleware(bot))
