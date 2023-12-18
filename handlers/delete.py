from aiogram import Router, F
from aiogram.types import Message, user, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from data.database import DataBase
from keyboards.builders import form_btn
from keyboards.inline import yes_no_btn, searching_start_btn
from keyboards.reply import main

from time import sleep

router = Router()
db = DataBase("users_db.db", "users")

@router.callback_query(lambda c: (c.data == 'delete'))
async def delete1(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Ты уверен что хочешь удалить профиль?", reply_markup=yes_no_btn(["Да", "Нет"]))

@router.callback_query(lambda c: (c.data == 'no'))
async def deleteno(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Тогда продолжим поиск или хочешь отредактировать анкету?", reply_markup=searching_start_btn(["Изменить", "Удалить", "Искать"]))

@router.callback_query(lambda c: (c.data == 'yes'))
async def deleteyes(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Удаляем анкету...")
    sleep(1)
    await db.delete_user(callback.from_user.id)
    await callback.message.answer("Анкета удалена. See you again!", reply_markup=main)
