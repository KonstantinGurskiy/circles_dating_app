from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


from keyboards.builders import form_btn

from data.database import DataBase
from utils.states import Form
from utils.city import check

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
        await state.set_state(Form.city)
        await message.answer("Теперь укажи свой город")
    else:
        await message.answer("Попробуй еще раз!")

@router.message(Form.city)
async def form_city(message: Message, state: FSMContext):
    city_exists = await check(message.text)
    if city_exists:
        await state.update_data(city=message.text)
        await state.set_state(Form.sex)
        await message.answer(
                "Choose your gender",
                reply_markup=form_btn(["boy", "girl"])
        )
    else:
        await message.answer("No that city. Choose another")


@router.message(Form.sex, F.text.casefold().in_(["boy", "girl"]))
async def form_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await state.set_state(Form.look_for)
    await message.answer(
        "Who are u lookin 4?",
        reply_markup=form_btn(["boys", "girls", "both"])
    )

@router.message(Form.sex)
async def incorrect_form_sex(message: Message, state: FSMContext):
    await message.answer("Choose from list")


@router.message(Form.look_for, F.text.casefold().in_(["boys", "girls", "both"]))
async def form_look_for(message: Message, state: FSMContext):
    await state.update_data(look_for=message.text)
    await state.set_state(Form.about)
    await message.answer("tell about urself")

@router.message(Form.look_for)
async def incorrect_form_look_for(message: Message, state: FSMContext):
    await message.answer("choose your variant")

@router.message(Form.about)
async def form_about(message: Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(Form.photo)
    await message.answer("Send photo")


@router.message(Form.photo, F.photo)
async def form_photo(message: Message, state: FSMContext, db: DataBase):
    photo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    await state.clear()


    frm_text = []
    [
        frm_text.append(value)
        for _, value in data.items()
    ]
    await db.insert(frm_text)

    await message.answer_photo(
        photo_file_id,
        "\n".join(frm_text)
    )


@router.message(Form.photo, ~F.photo)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь фото!")
