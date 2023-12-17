from aiogram import Router, F
from aiogram.types import Message, location, ReplyKeyboardMarkup, KeyboardButton, user
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

router = Router()

@router.message(Command("create", "edit"))
async def my_form(message: Message, state: FSMContext):
    temp = await message.answer("Создаю анкету...")
    sleep(1)
    # await bot.delete_message()
    await state.update_data(user_id = str(message.from_user.id))
    await state.update_data(liked = None)
    await state.update_data(likes = None)
    await state.update_data(already_saw = None)
    await state.update_data(already_seen_by = None)
    await state.update_data(active = False)
    await state.update_data(time = datetime.now().strftime("%H:%M:%S"))
    await state.set_state(Form.name)
    await message.answer("Как тебя зовут?",
                         reply_markup=form_btn(message.from_user.first_name))


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.longitude)
    await message.answer(
            "Где ты находишься?",
            reply_markup=form_loc_req(["отправить геопозицию"])
    )



@router.message(Form.longitude, F.location)
async def form_longitude(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(latitude=lat)
    await state.update_data(longitude=lon)


    await state.set_state(Form.target)
    await message.answer(
            "Зачем ты здесь?\nПригласить кого-нибудь или присоединиться к кому-нибудь?",
            reply_markup=form_btn(["создать событие", "присоединиться к событию"])
    )


@router.message(Form.longitude, ~F.location)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь геопозицию!")





@router.message(Form.target, F.text.casefold().in_(["создать событие", "присоединиться к событию"]))
async def form_target(message: Message, state: FSMContext):
    await state.update_data(target=message.text)
    if(message.text == "присоединиться к событию"):
        await state.set_state(Form.gender)
        await message.answer("Ты парень или девушка?", reply_markup=form_btn(["парень", "девушка"]))
    else:
        await state.set_state(Form.look_for)
        await state.update_data(gender = None)
        await message.answer("Кого бы ты хотел видеть на событии?", reply_markup=form_btn(["парней", "девушек", "всех!"]))


@router.message(Form.target, ~F.text.casefold().in_(["создать событие", "присоединиться к событию"]))
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Выбери вариант!")


@router.message(Form.gender, F.text.casefold().in_(["парень", "девушка"]))
async def form_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.update_data(look_for = None)
    await state.set_state(Form.circle)
    await message.answer("Расскажи о себе кружком")

@router.message(Form.gender, ~F.text.casefold().in_(["парень", "девушка"]))
async def form_gender(message: Message, state: FSMContext):
    await message.answer("Выбери вариант!")

@router.message(Form.look_for, F.text.casefold().in_(["парней", "девушек", "всех!"]))
async def form_gender(message: Message, state: FSMContext):
    await state.update_data(look_for=message.text)
    await state.set_state(Form.circle)
    await message.answer("Расскажи о себе кружком")

@router.message(Form.look_for, ~F.text.casefold().in_(["парней", "девушек", "всех!"]))
async def form_gender(message: Message, state: FSMContext):
    await message.answer("Выбери вариант!")


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
        await message.answer("Имя: " + data["name"] + "\nЦель: " + data["target"] + "\nПриглашаю: " + data["look_for"] + "\nТы находишься: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[-4:-1]))
        await message.answer("Событие будет активно в течение часа\nМы пришлем уведомление, когда его нужно будет обновить")
        await message.answer("Все верно? Начинаем поиск?\n", reply_markup=form_btn(["/edit", "/delete", "/search"]))
    else:
        await message.answer("Твой профиль:")

        await message.answer_video_note(
            video_note_file_id,
        )
        await message.answer("Имя: " + data["name"] + "\nЦель: " + data["target"] + "\nТы -- " + data["gender"] +"\nТы находишься: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[-4:-1]))
        await message.answer("Профиль будет активен в течение часа\nМы пришлем уведомление, когда его нужно будет обновить")
        await message.answer("Все верно? Начинаем поиск?\n", reply_markup=form_btn(["/edit", "/delete", "/search"]))

    if(data["username"]==None):
        await message.answer("У тебя нет юзернейма в телеграме\nДобавь его\nИначе -- тебе не смогут написать")

@router.message(Form.circle, ~F.video_note)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь кружок!")

