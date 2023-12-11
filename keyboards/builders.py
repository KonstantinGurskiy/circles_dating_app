from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def form_btn(text: str | list) -> ReplyKeyboardMarkup:
    if isinstance(text, str):
        text = [text]
    return ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text=txt) for txt in text]], resize_keyboard = True, one_time_keyboard = True)

def form_loc_req(text: str | list) -> ReplyKeyboardMarkup:
    if isinstance(text, str):
        text = [text]
    return ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text=txt, request_location = True) for txt in text]], resize_keyboard = True, one_time_keyboard = True)

