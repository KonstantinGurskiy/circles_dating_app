from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def name_btn(txt: str | list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=txt[0], callback_data = 'name')
            ],
            [
                InlineKeyboardButton(text=txt[1], callback_data = 'other')
            ]
        ],

    )
def target_btn(txt: str | list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=txt[0], callback_data = 'создатель события')
            ],
            [
                InlineKeyboardButton(text=txt[1], callback_data = 'гость события')
            ]
        ],

    )


def gender_btn(txt: str | list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=txt[0], callback_data = 'парень')
            ],
            [
                InlineKeyboardButton(text=txt[1], callback_data = 'девушка')
            ]
        ],

    )

def look_for_btn(txt: str | list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=txt[0], callback_data = 'парней')
            ],
            [
                InlineKeyboardButton(text=txt[1], callback_data = 'девушек')
            ],
            [
                InlineKeyboardButton(text=txt[2], callback_data = 'всех!')
            ]
        ],

    )


def searching_start_btn(txt: str | list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=txt[0], callback_data = 'edit')
            ],
            [
                InlineKeyboardButton(text=txt[1], callback_data = 'delete')
            ],
            [
                InlineKeyboardButton(text=txt[2], callback_data = 'search')
            ]
        ],

    )



def like_btn(txt: str | list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=txt[0], callback_data = 'like')
            ],
            [
                InlineKeyboardButton(text=txt[1], callback_data = 'dislike')
            ]
        ],

    )

def yes_no_btn(txt: str | list):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=txt[0], callback_data = 'yes')
            ],
            [
                InlineKeyboardButton(text=txt[1], callback_data = 'no')
            ]
        ],

    )
