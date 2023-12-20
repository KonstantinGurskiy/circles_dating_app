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
from keyboards.inline import name_btn, target_btn, look_for_btn, gender_btn, searching_start_btn, check_profile_btn, like_btn
from utils.search_machine import closest_person
from utils.check_timer import check_timer

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
    await state.update_data(waiting = False)
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
            "Где ты находишься?\nОтправь геопозицию\nКнопка⬇",
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
                "Где ты находишься?\nОтправь геопозицию\nКнопка⬇️",
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
async def form_photo(message: Message, state: FSMContext, db: DataBase, bot: Bot):
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
        # await message.answer("Событие будет активно в течение часа\nМы пришлем уведомление, когда его нужно будет обновить")
        await message.answer("Событие будет активно в течение часа\n")
        await message.answer("Всё верно?\n", reply_markup=check_profile_btn(["Изменить запрос", "Удалить запрос"]))
    else:
        await message.answer("Твой профиль:")

        await message.answer_video_note(
            video_note_file_id,
        )
        await message.answer("Имя: " + data["name"] + "\nТы -- " + data["target"] + "\nТы -- " + data["gender"] +"\nТы находишься: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[-4:-1]))
        # await message.answer("Профиль будет активен в течение часа\nМы пришлем уведомление, когда его нужно будет обновить")
        await message.answer("Профиль будет активен в течение часа\n")
        await message.answer("Всё верно?\n", reply_markup=check_profile_btn(["Изменить запрос", "Удалить запрос"]))

    if(data["username"]==None):
        await message.answer("У тебя нет юзернейма в телеграме\nДобавь его\nИначе -- тебе не смогут написать")











###Отправим сообщение о новом событии ждущим
    df = await db.read_table()
    if(data["gender"]==None):
        guests_list = df[(df['gender'].values!=None) & (df['waiting'].values==True) & (df['time'].apply(lambda x: check_timer(x))) & (df['active']==True)]
        if(data["look_for"]=="парней"):
            guests_list &= guests_list['gender'].isin(['парень'])
        elif(data["look_for"]=="девушек"):
            guests_list &= guests_list['gender'].isin(['девушка'])
        for item in guests_list['user_id'].values:
            await bot.send_message(item, "Новое событие! Посмотри:")
            await bot.send_video_note(item, video_note_file_id)
            await bot.send_message(item, "Имя: " + data["name"] + "\nЦель: " + data["target"] + "\nОткуда: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", contr_person["latitude"], data["longitude"])).split(',')[-4:-1]), reply_markup=like_btn(["нравится ❤️", "следующий 👎"]))







    await message.answer("Ищу кандидата...\n")
    sleep(3)

###приколхозим отправку первого кружка
    df = await db.read_table()
    print(df)
    contr_person = await closest_person(message.from_user.id, df)
    changed_row = df[df['user_id'] == message.from_user.id].iloc[0].values.flatten().tolist()[1:]
    if isinstance(contr_person, int):
        changed_row[0] = str(changed_row[0])
        changed_row[5] = str(1)
        changed_row[6] = str(changed_row[6])
        await db.insert(changed_row)
        await message.answer("Пользователи кончились", reply_markup=check_profile_btn(["Изменить запрос", "Удалить запрос"]))
    else:
        changed_opponent_row = df[df['user_id'] == int(contr_person['user_id'])].iloc[0].values.flatten().tolist()[1:]
        await message.answer_video_note(
        contr_person["circle"],
        )
        await message.answer("Имя: " + contr_person["name"] + "\nЦель: " + contr_person["target"] + "\nОткуда: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", contr_person["latitude"], contr_person["longitude"])).split(',')[-4:-1]), reply_markup=like_btn(["нравится ❤️", "следующий 👎"]))
        if changed_row[3]==None:
            changed_row[3] = str(contr_person['user_id'])
        else:
            changed_row[3] = str(changed_row[3])+ ' ' + str(contr_person['user_id'])

        changed_row[0] = str(changed_row[0])
        changed_row[5] = str(changed_row[5])
        changed_row[6] = str(changed_row[6])
        await db.insert(changed_row)



        if changed_opponent_row[4]==None:
            changed_opponent_row[4] = str(message.from_user.id)
        else:
            changed_opponent_row[4] = str(changed_opponent_row[4])+ ' ' + str(message.from_user.id)

        changed_opponent_row[0] = str(changed_opponent_row[0])
        changed_opponent_row[5] = str(changed_opponent_row[5])
        changed_opponent_row[6] = str(changed_opponent_row[6])
        await db.insert(changed_opponent_row)







@router.message(Form.circle, ~F.video_note)
async def form_photo(message: Message, state: FSMContext):
    await message.answer("Отправь кружок!")
