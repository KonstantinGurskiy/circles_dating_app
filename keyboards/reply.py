from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/form"),
            KeyboardButton(text="/go")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True

)
