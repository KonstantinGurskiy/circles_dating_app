from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Создать", callback_data = 'create'),
            # KeyboardButton(text="/go")
        ]
    ],

)
