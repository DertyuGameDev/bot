# import asyncio
# from datetime import datetime
# import json
# import logging
# import urllib

import requests
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters import Command
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
# from aiohttp import web
# from config import BOT_TOKEN

# -*- coding: utf-8 -*-
import asyncio
import json
import logging
import urllib
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove
from data.user import UserCard
from config import BOT_TOKEN
from data import db_session
from aiohttp import web

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
# API_URL = 'https://imminent-jet-suggestion.glitch.me'
# API_URL = "https://cultured-ring-dog.glitch.me"
API_URL = "http://127.0.0.1:5000"
routes = web.RouteTableDef()
start_button_for_offline_user = [
    [
        KeyboardButton(text="/start")
    ],
    [
        KeyboardButton(text="Помощь")
    ],
    [
        KeyboardButton(text="Редактировать профиль")
    ],
    [
        KeyboardButton(text="Выйти из тени")
    ]
]
start_button_for_online_user = [
    [
        KeyboardButton(text="/start")
    ],
    [
        KeyboardButton(text="Помощь")
    ],
    [
        KeyboardButton(text="Редактировать профиль")
    ],
    [
        KeyboardButton(text="Уйти в тень")
    ]
]
edit_user_buttons = [
    [
        KeyboardButton(text="/age")

    ],
    [
        KeyboardButton(text="/name")
    ],
    [
        KeyboardButton(text="/picture")
    ],
    [
        KeyboardButton(text="/description")
    ],
    [
        KeyboardButton(text="/end_edit_profile")
    ]
]
kb_online = ReplyKeyboardMarkup(keyboard=start_button_for_online_user, resize_keyboard=True, one_time_keyboard=False)
kb_offline = ReplyKeyboardMarkup(keyboard=start_button_for_offline_user, resize_keyboard=True, one_time_keyboard=False)
user_kb = ReplyKeyboardMarkup(keyboard=edit_user_buttons, resize_keyboard=True, one_time_keyboard=False)


@dp.message(Command('start'))
async def start(message: types.Message, state):
    resp = requests.post(f"{API_URL}/check_user", json={"user_id": message.from_user.id})
    data = resp.json()
    if not data["exists"]:
        await ask_birthdate(message, state)
    else:
        await prepare_link(message)


@dp.message(Command("help"))
async def bot_help(message: types.Message):
    data = []
    await message.answer("Это помощь")


@dp.message(Command("edit_profile"))
async def edit_user_info(message: types.Message):
    await message.answer("Вы перешли в меню редактирования своего профиля", reply_markup=ReplyKeyboardRemove())
    await message.answer("Теперь вы можете выбрать команду для редактирования", reply_markup=user_kb)


@dp.message(Command("age"))
async def edit_age(message: types.Message, state):
    await message.answer("Введите новые данные для обновления возраста")
    await state.set_state(WaitNewAge.waiting_message)


class WaitNewAge(StatesGroup):
    waiting_message = State()


@dp.message(WaitNewAge.waiting_message)
async def update_age(message: types.Message, state):
    try:
        age = int(message.text.rstrip())
        if not (6 <= age <= 100):
            raise ValueError
        res = requests.put(f"{API_URL}/edit_user/{message.from_user.id}", json={"old": age}).json()
        await state.clear()
        await message.answer("Вы успешно изменили возраст!")

    except ValueError:
        await message.answer("Возраст выходит за рамки или не является чилом. Введите еще раз.")


@dp.message(Command("name"))
async def edit_name(message: types.Message, state):
    await message.answer("Введите обновленное имя")
    await state.set_state(WaitNewName.waiting_message)


class WaitNewName(StatesGroup):
    waiting_message = State()


@dp.message(WaitNewName.waiting_message)
async def update_name(message: types.Message, state):
    name = message.text.rstrip()
    res = requests.put(f"{API_URL}/edit_user/{message.from_user.id}", json={"name": name}).json()
    await state.clear()
    await message.answer("Вы успешно сменили имя!")


@dp.message(Command("end_edit_profile"))
async def end_edit_profile(message: types.Message, state):
    await state.clear()
    await message.answer("Все данные успешно обновлены!", reply_markup=kb_online)


@dp.message(Command("picture"))
async def edit_picture(message: types.Message, state):
    await message.answer("Загрузите фото, которое вы хотите установить")
    await state.set_state(WaitNewPicture.wait_picture)


class WaitNewPicture(StatesGroup):
    wait_picture = State()


@dp.message(WaitNewPicture.wait_picture)
async def update_picture(message: types.Message, state):
    try:
        file_id = message.photo[-1].file_id
        photo = await bot.get_file(file_id)
        file_path = photo.file_path

        file_name = f"static/img/{message.from_user.id}.jpg"
        file = await bot.download_file(file_path)
        res = requests.post(f"{API_URL}/create_picture",
                            files={"file": (file_name, file, "image/jpg")}
                            ).text
        await state.clear()
        await message.answer("Вы успешно обновили свою фотографию!")
    except TypeError:
        await message.answer("Вы не загрузили фотографию! Повторите попытку.")


@dp.message(Command("description"))
async def edit_description(message: types.Message, state):
    await message.answer("Опишите себя, это увидят другие пользователи.")
    await state.set_state(WaitNewDescription.wait_description)


@dp.message(Command("set_online"))
async def set_online(message: types.Message):
    res = requests.put(f"{API_URL}/edit_user/{message.from_user.id}", json={"disabled": False}).json()
    await message.answer("Описать, что произошло", reply_markup=ReplyKeyboardRemove())
    await message.answer("Теперь вас видят другие пользователи", reply_markup=kb_online)


@dp.message(Command("set_offline"))
async def set_offline(message: types.Message):
    res = requests.put(f"{API_URL}/edit_user/{message.from_user.id}", json={"disabled": True}).json()
    await message.answer("Описать, что произошло", reply_markup=ReplyKeyboardRemove())
    await message.answer("Теперь вас не видят другие пользователи", reply_markup=kb_offline)


class WaitNewDescription(StatesGroup):
    wait_description = State()


@dp.message(WaitNewDescription.wait_description)
async def update_description(message: types.Message, state):
    text = message.text
    res = requests.put(f"{API_URL}/edit_user/{message.from_user.id}", json={"capture": text}).json()
    await state.clear()
    await message.answer("Данные успешно сохранены")


async def prepare_link(message, new_user=False):
    payload = {"user_id": message.from_user.id, 'm': message.text}
    json_str = json.dumps(payload)
    encoded = urllib.parse.quote(json_str)
    url = f"{API_URL}/?data={encoded}"
    btns = [
        [
            InlineKeyboardButton(text=u'🚀 Открыть Web App', url=url)
        ]
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=btns)
    # inline_kb.add(InlineKeyboardButton(text=u'🚀 Открыть Web App', url=url))
    if new_user:
        await message.answer(
            u"Нажми кнопку ниже, чтобы открыть наше веб-приложение:",
            reply_markup=inline_kb
        )
    else:
        await message.answer(u"Привет! 👋", reply_markup=kb_online)
        await message.answer(
            u"Нажми кнопку ниже, чтобы открыть наше веб-приложение:",
            reply_markup=inline_kb
        )
    # inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    #     [InlineKeyboardButton(text='🚀 Открыть Web App', web_app=WebAppInfo(url=url))]
    # ])
    # await message.answer(
    #     "Привет! 👋\nНажми кнопку ниже, чтобы открыть наше веб-приложение:",
    #     reply_markup=inline_kb
    # )


async def message_like(json):
    user1 = await bot.get_chat(json['user1'])
    user2 = await bot.get_chat(json['user2'])
    await bot.send_message(json['user1'], f'Вы понравились @{user2.username}! Скорее знакомьтесь😊')
    await bot.send_message(json['user2'], f'Вы понравились @{user1.username}! Скорее знакомьтесь😊')


class BirthdateForm(StatesGroup):
    waiting_for_birthdate = State()


async def ask_birthdate(message: types.Message, state):
    await message.answer("Привет! Скажи сколько тебе лет.", reply_markup=kb_online)
    await state.set_state(BirthdateForm.waiting_for_birthdate)


@dp.message(BirthdateForm.waiting_for_birthdate)
async def process_birthdate(message: types.Message, state):
    try:
        age = int(message.text.rstrip())
        if 6 > age or age > 100:
            raise ValueError
        await message.answer(f"Спасибо! Погнали!")
        picture_path = await get_user_avatar(message)
        requests.post(f"{API_URL}/create_user", json=make_reg(message, age, picture_path))
        await state.clear()
        await prepare_link(message, new_user=True)
    except ValueError:
        await message.answer("Возраст выходит за рамки или не является чилом. Введите еще раз.")


def make_reg(message, age, picture_path):
    d = {
        'tg_id': message.from_user.id,
        'name': message.from_user.first_name,
        'capture': '-',
        'picture': picture_path,
        'old': age,
        'disabled': 0
    }
    return d


async def get_user_avatar(message):
    user_id = message.from_user.id
    photos = await bot.get_user_profile_photos(user_id)
    print(photos)
    if photos.total_count == 0:
        return 'static/img/default.jpg'
    file_id = photos.photos[0][-1].file_id
    file_info = await bot.get_file(file_id)

    file_path = file_info.file_path
    file_name = f"static/img/{user_id}.jpg"

    file = await bot.download_file(file_path)
    print(requests.post(
        f"{API_URL}/create_picture",
        files={"file": (file_name, file, "image/jpg")}
    ).text)
    return file_name


async def poll_server_for_events():
    while True:
        try:
            response = requests.get(f"{API_URL}/get_events")
            if response.status_code == 200:
                data = response.json()
                for event in data.get("events", []):
                    await message_like(event)
        except Exception as e:
            logging.error(f"Ошибка при опросе сервера: {e}")
        await asyncio.sleep(5)


async def start():
    await asyncio.gather(
        poll_server_for_events(),
        dp.start_polling(bot)
    )

@dp.message()
async def test(message: types.Message):
    print(message.text)
    if message.text == "Помощь":
        await bot_help(message)
    elif message.text == "Редактировать профиль":
        await edit_user_info(message)
    elif message.text == "Выйти из тени":
        await set_online(message)
    elif message.text == "Уйти в тень":
        await set_offline(message)


if __name__ == "__main__":
    asyncio.run(start())
