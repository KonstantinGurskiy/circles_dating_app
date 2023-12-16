from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/create"),
            # KeyboardButton(text="/go")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True

)
