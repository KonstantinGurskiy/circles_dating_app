from aiogram import Router, F, Bot
from aiogram.types import Message, location, ReplyKeyboardMarkup, KeyboardButton, user, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods.send_video_note import SendVideoNote
from aiogram.methods.delete_message import DeleteMessage

from datetime import datetime
from time import sleep

from keyboards.builders import form_btn, form_loc_req

from data.database import DataBase
from utils.states import Form
from utils.city import check
from utils.coord2loco import get_place
from keyboards.inline import name_btn, target_btn, look_for_btn, gender_btn, searching_start_btn
router = Router()


@router.callback_query(lambda c: (c.data == 'create') | (c.data == 'edit'))
async def my_form(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(callback.id)
    temp = await callback.message.answer("Создаю анкету...")
    sleep(1)
    # await bot.delete_message()
    await state.update_data(user_id = str(callback.from_user.id))
    await state.update_data(liked = None)
    await state.update_data(likes = None)
    await state.update_data(already_saw = None)
    await state.update_data(already_seen_by = None)
    await state.update_data(active = True)
    await state.update_data(time = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    await state.set_state(Form.name)
    await callback.message.answer("Как тебя зовут?",
                        reply_markup=name_btn([callback.from_user.first_name, "Новое имя"]))


@router.callback_query(lambda c: c.data == 'name')
async def form_name(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(callback.id)
    await state.update_data(name=callback.from_user.first_name)
    await state.set_state(Form.longitude)
    await callback.message.answer(
            "Где ты находишься?",
            reply_markup=form_loc_req(["отправить геопозицию"])
    )

@router.callback_query(lambda c: c.data == 'other')
async def form_name(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(callback.id)
    await callback.message.answer("Введи имя, которое бы ты хотел использовать")
    @router.message(Form.name, F.text)
    async def form_longitude(message: Message, state: FSMContext):
        await state.update_data(name=message.text)
        await state.set_state(Form.longitude)

        await message.answer(
                "Где ты находишься?",
                reply_markup=form_loc_req(["отправить геопозицию"])
    )
    @router.message(Form.longitude, ~F.location)
    async def form_photo(message: Message, state: FSMContext):
        await message.answer("Отправь геопозицию!")



@router.message(Form.longitude, F.location)
async def form_longitude(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(latitude=lat)
    await state.update_data(longitude=lon)

    msg = await message.answer("Записываю...", reply_markup=ReplyKeyboardRemove())
    await msg.delete()


    await state.set_state(Form.target)
    await message.answer(
            "Зачем ты здесь?\nПригласить кого-нибудь или присоединиться к кому-нибудь?",
            reply_markup=target_btn(["создать событие", "присоединиться к событию"])
    )


@router.message(Form.longitude, ~F.location)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь геопозицию!")


@router.callback_query(lambda c: (c.data == 'создатель события') | (c.data == 'гость события'))
async def form_target(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(callback.id)
    await state.update_data(target=callback.data)
    if(callback.data == "гость события"):
        await state.set_state(Form.gender)
        await callback.message.answer("Ты парень или девушка?", reply_markup=gender_btn(["парень", "девушка"]))
    else:
        await state.set_state(Form.look_for)
        await state.update_data(gender = None)
        await callback.message.answer("Кого бы ты хотел видеть на событии?", reply_markup=look_for_btn(["парней", "девушек", "всех!"]))

#
# @router.message(Form.target, ~F.text.casefold().in_(["создать событие", "присоединиться к событию"]))
# async def form_photo(message: Message, state: FSMContext):
#     await callback.message.answer("Выбери вариант!")


@router.callback_query(lambda c: (c.data == 'парень') | (c.data == 'девушка'))
async def form_target(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(callback.id)
    await state.update_data(gender=callback.data)
    await state.update_data(look_for = None)
    await state.set_state(Form.circle)
    await callback.message.answer("Расскажи о себе кружком")

# @router.callback_query(lambda c: ~((c.data == 'boy') | (c.data == 'girl')))
# async def form_target(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer("Выбери вариант!")

@router.callback_query(lambda c: (c.data == 'парней') | (c.data == 'девушек') | (c.data == 'всех!'))
async def form_target(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.answer_callback_query(callback.id)
    await state.update_data(look_for=callback.data)
    await state.set_state(Form.circle)
    await callback.message.answer("Расскажи о себе кружком")


@router.message(Form.circle, F.video_note)
async def form_photo(message: Message, state: FSMContext, db: DataBase):
    video_note_file_id = message.video_note.file_id
    await state.update_data(circle=video_note_file_id)
    await state.update_data(username = message.from_user.username)
    data = await state.get_data()
    await state.clear()

    frm_text = []
    [
        frm_text.append(value)
        for _, value in data.items()
    ]
    print(frm_text)
    await db.insert(frm_text)


    if(data["gender"]==None):
        await message.answer("Твое событие:")

        await message.answer_video_note(
            video_note_file_id,
        )
        await message.answer("Имя: " + data["name"] + "\nТы -- " + data["target"] + "\nПриглашаю: " + data["look_for"] + "\nТы находишься: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[-4:-1]))
        await message.answer("Событие будет активно в течение часа\nМы пришлем уведомление, когда его нужно будет обновить")
        await message.answer("Все верно? Начинаем поиск?\n", reply_markup=searching_start_btn(["Изменить", "Удалить", "Искать"]))
    else:
        await message.answer("Твой профиль:")

        await message.answer_video_note(
            video_note_file_id,
        )
        await message.answer("Имя: " + data["name"] + "\nТы -- " + data["target"] + "\nТы -- " + data["gender"] +"\nТы находишься: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[-4:-1]))
        await message.answer("Профиль будет активен в течение часа\nМы пришлем уведомление, когда его нужно будет обновить")
        await message.answer("Все верно? Начинаем поиск?\n", reply_markup=searching_start_btn(["Изменить", "Удалить", "Искать"]))

    if(data["username"]==None):
        await message.answer("У тебя нет юзернейма в телеграме\nДобавь его\nИначе -- тебе не смогут написать")




@router.message(Form.circle, ~F.video_note)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь кружок!")
