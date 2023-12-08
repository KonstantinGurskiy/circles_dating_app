from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/form"),
            KeyboardButton(text="Статистика")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True

)
