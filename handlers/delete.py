from aiogram import Router, F, Bot
from aiogram.types import Message, user, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from data.database import DataBase
from keyboards.builders import form_btn
from keyboards.inline import yes_no_btn, searching_start_btn
from keyboards.reply import main
from utils.clean_chat import insert_new_msgs_to_db, delete_msgs
from asyncio import sleep

router = Router()
db = DataBase("users_db.db", "users")
temp=[]

@router.message(Command("delete"))
async def deletion(message: Message, state: FSMContext, db: DataBase, bot: Bot):
    temp.append(await message.answer("Ты уверен что хочешь удалить профиль?", reply_markup=yes_no_btn(["Да", "Нет"])))

@router.callback_query(lambda c: (c.data == 'no'))
async def deleteno(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(callback.id)
    temp.append(await callback.message.answer("Тогда продолжим поиск или хочешь отредактировать анкету?", reply_markup=searching_start_btn(["Продолжить поиск"])))
    await insert_new_msgs_to_db(callback.message.chat.id, temp, await db.read_table(), db)

@router.callback_query(lambda c: (c.data == 'yes'))
async def deleteyes(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(callback.id)
    temp.append(await callback.message.answer("Удаляем анкету..."))
    await sleep(1)
    await db.delete_user(callback.from_user.id)
    temp.append(await callback.message.answer("Анкета удалена. See you again!", reply_markup=main))
    # await insert_new_msgs_to_db(callback.message.chat.id, temp, await db.read_table(), db)
    await sleep(2)
    for msg in temp:
        try:
            await msg.delete()
        except:
            print("!!!")
