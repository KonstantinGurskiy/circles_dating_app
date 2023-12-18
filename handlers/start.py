from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.reply import main
from data.database import DataBase

router = Router()

@router.message(CommandStart())
async def start(message: Message, db: DataBase):
    print(db.name)
    await message.answer("Привет! Меня зовут бот \n\"КРУГИ ДЛЯ ЗНАКОМСТВ\".\nЗдесь ты можешь найти интересное событие или сам создать его и позвать других пользователей. \nДля начала давай создадим тебе профиль. \nНажми Создать", reply_markup=main)
