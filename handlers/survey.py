from aiogram import Router, F
from aiogram.types import Message, location, ReplyKeyboardMarkup, KeyboardButton
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
    await state.set_state(Form.name)
    await message.answer("Отлично, введи своё имя: ",
                         reply_markup=form_btn(message.from_user.first_name))


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.age)
    await message.answer("Теперь укажи свой возраст")

@router.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(age=int(message.text))
        await state.set_state(Form.longitude)
        await message.answer(
                "Теперь send ur location",
                reply_markup=ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text="sendlocation", request_location = True)]], resize_keyboard = True, one_time_keyboard=True)
        )
    else:
        await message.answer("Попробуй еще раз!")



@router.message(Form.longitude)
async def form_longitude(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    await state.update_data(latitude=lat)
    await state.update_data(longitude=lon)


    await state.set_state(Form.target)
    await message.answer(
            "Choose your target",
            reply_markup=form_btn(["хочу позвать", "хочу чтобы позвали"])
    )


@router.message(Form.target, F.text.casefold().in_(["хочу позвать", "хочу чтобы позвали"]))
async def form_target(message: Message, state: FSMContext):
    await state.update_data(target=message.text)
    await state.set_state(Form.about)
    await message.answer("tell about urself")


@router.message(Form.about)
async def form_about(message: Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(Form.photo)
    await message.answer("Send circle")


@router.message(Form.photo, F.video_note)
async def form_photo(message: Message, state: FSMContext, db: DataBase):
    video_note_file_id = message.video_note.file_id
    await state.update_data(photo=video_note_file_id)
    data = await state.get_data()
    await state.clear()

    frm_text = []
    [
        frm_text.append(value)
        for _, value in data.items()
    ]
    # print(frm_text)
    await db.insert(frm_text)

    await message.answer_video_note(
        video_note_file_id,
        # "\n".join(list(map(str, frm_text)))
    )# Вывод словаря в одну строку

    await message.answer("\n".join(f"{key}: {str(value)}" for key, value in data.items() if key not in ["latitude", "longitude", "photo"]) + "\nUr location: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[1:-1]))

    # print(get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"]))



@router.message(Form.photo, ~F.video_note)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь кружок!")
