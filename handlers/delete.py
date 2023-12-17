from aiogram import Router, F
from aiogram.types import Message, user
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from data.database import DataBase
from keyboards.builders import form_btn
from time import sleep

router = Router()

@router.message(Command("delete"))
async def search_people(message: Message, state: FSMContext):
    await message.answer("Ты уверен что хочешь удалить профиль?", reply_markup=form_btn(["/да", "/нет"]))

@router.message(Command("нет"))
async def search_people(message: Message, state: FSMContext):
    await message.answer("Тогда продолжим поиск или хочешь отредактировать анкету?", reply_markup=form_btn(["/edit", "/search"]))

@router.message(Command("да"))
async def search_people(message: Message, state: FSMContext, db: DataBase):
    await message.answer("Удаляем анкету...")
    sleep(1)
    await db.delete_user(message.from_user.id)
    await message.answer("Анкета удалена. See you again!")
