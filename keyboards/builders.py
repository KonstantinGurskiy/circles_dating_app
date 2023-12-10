from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def form_btn(text: str | list) -> ReplyKeyboardBuilder:
    if isinstance(text, str):
        text = [text]

    builder = ReplyKeyboardBuilder()
    [builder.button(text=txt) for txt in text]
    return builder.as_markup(
        resize_keyboard = True,
        one_time_keyboard = True,
        )

def form_loc_req(text):
    return ReplyKeyboardMarkup([KeyboardButton(text, request_contact = True)], resize_keyboard = True)
