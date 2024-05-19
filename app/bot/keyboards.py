from aiogram.types import BotCommand, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from .text import commands_bot

# TODO: команды бота прописать в yaml файл
main_menu_commands = [
    BotCommand(
        command=command,
        description=description
    ) for command, description in commands_bot.items()
]


def model_buttons(models: list):
    builder = ReplyKeyboardBuilder()
    number_models = len(models)
    for name in models:
        builder.add(KeyboardButton(text=name))
    builder.adjust(1 if number_models == 1 else number_models // 2)
    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        is_persistent=True
    )


