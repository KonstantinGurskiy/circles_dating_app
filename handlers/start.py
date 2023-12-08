from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards.reply import main
from data.database import DataBase

router = Router()

@router.message(CommandStart())
async def start(message: Message, db: DataBase):
    print(db.name)
    await message.answer("Привет Викусик! Выберите действие:", reply_markup=main)
