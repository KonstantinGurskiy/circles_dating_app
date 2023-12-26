from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.reply import main
from data.database import DataBase

from utils.statistics import how_much

from asyncio import sleep

router = Router()

@router.message(CommandStart())
async def start(message: Message, db: DataBase):
    await message.answer("Сейчас ботом пользуются: " + await how_much(db))
    await sleep(1)
    await message.answer("""

        Добро пожаловать в наш бот "КРУГИ ДЛЯ ЗНАКОМСТВ"!

Устали от долгих переписок и одиночества в баре? Наш бот поможет найти вам новых друзей с помощью видео-знакомств.

В нашем боте вы сможете находить интересные события и приглашать других людей участвовать в них. Все это происходит через видео-кружочки.

Забудьте о скучных анкетах и фотографиях. Ваше видео покажет вашу натуру лучше.

Начать знакомиться просто - нажмите "Создать", заполните профиль и укажите геолокацию. Загрузите видео и установите предпочтения для встречи.

Ваша заявка будет видна другим пользователям в течение 60 минут. А ваше местоположение - только тем, кого вы пригласите на встречу.

По вопросам сотрудничества обращайтесь сюда: @wigo_llc
""", reply_markup=main)
