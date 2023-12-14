from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.reply import main
from data.database import DataBase

router = Router()

@router.message(CommandStart())
async def start(message: Message, db: DataBase):
    print(db.name)
    await message.answer("Привет! Я бот знакомств Meeting Circles. Выбери действие:\nform -- ты еще не с нами или хочешь создать анкету заново\ngo -- начать поиск", reply_markup=main)
