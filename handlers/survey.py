from aiogram import Router, F
from aiogram.types import Message, location, ReplyKeyboardMarkup, KeyboardButton, user
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods.send_video_note import SendVideoNote


from keyboards.builders import form_btn, form_loc_req

from data.database import DataBase
from utils.states import Form
from utils.city import check
from utils.coord2loco import get_place

router = Router()

@router.message(Command("form"))
async def my_form(message: Message, state: FSMContext):
    await state.update_data(user_id = str(message.from_user.id))
    await state.update_data(liked = " ")
    await state.update_data(likes = " ")
    await state.update_data(already_seen = " ")
    await state.set_state(Form.name)
    await message.answer("Как тебя зовут?",
                         reply_markup=form_btn(message.from_user.first_name))


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
#     await state.set_state(Form.age)
#     await message.answer("Enter ur age")
#
# @router.message(Form.age)
# async def form_age(message: Message, state: FSMContext):
#     if message.text.isdigit():
#         await state.update_data(age=int(message.text))
    await state.set_state(Form.longitude)
    await message.answer(
            "Где ты находишься?",
            reply_markup=form_loc_req(["отправить геопозицию"])
    )
    # else:
    #     await message.answer("Try again!")



@router.message(Form.longitude, F.location)
async def form_longitude(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(latitude=lat)
    await state.update_data(longitude=lon)


    await state.set_state(Form.target)
    await message.answer(
            "Зачем ты здесь?\nПригласить кого-нибудь или присоединиться к кому-нибудь?",
            reply_markup=form_btn(["хочу пригласить", "хочу присоединиться"])
    )

@router.message(Form.longitude, ~F.location)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь геопозицию!")



@router.message(Form.target, F.text.casefold().in_(["хочу пригласить", "хочу присоединиться"]))
async def form_target(message: Message, state: FSMContext):
    await state.update_data(target=message.text)
#     await state.set_state(Form.about)
#     await message.answer("tell about urself")
#раскомментируй если нужен about
#
# @router.message(Form.about)
# async def form_about(message: Message, state: FSMContext):
#     await state.update_data(about=message.text)
    await state.set_state(Form.circle)
    await message.answer("Расскажи о себе кружком")

@router.message(Form.target, ~F.text.casefold().in_(["хочу пригласить", "хочу присоединиться"]))
async def form_photo(message: Message, state: FSMContext):
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

    await db.insert(frm_text)

    await message.answer("Твой профиль:")

    await message.answer_video_note(
        video_note_file_id,
    )

    await message.answer("Имя: " + data["name"] + "\nЦель: " + data["target"] + "\nТы находишься: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[-4:-1]), reply_markup=form_btn(["/form", "/go"]))


@router.message(Form.circle, ~F.video_note)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь кружок!")

