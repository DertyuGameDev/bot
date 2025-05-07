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
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.user import UserCard
from config import BOT_TOKEN
from data import db_session
from aiohttp import web

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
API_URL = 'https://imminent-jet-suggestion.glitch.me'
routes = web.RouteTableDef()


@dp.message(Command('start'))
async def start(message: types.Message, state):
    resp = requests.post(f"{API_URL}/check_user", json={"user_id": message.from_user.id})
    data = resp.json()
    if not data["exists"]:
        await ask_birthdate(message, state)
    else:
        await prepare_link(message)


async def prepare_link(message):
    payload = {"user_id": message.from_user.id, 'm': message.text}
    json_str = json.dumps(payload)
    encoded = urllib.parse.quote(json_str)
    url = f"{API_URL}/?data={encoded}"
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton(text=u'🚀 Открыть Web App', url=url))

    await message.answer(
        u"Привет! 👋\nНажми кнопку ниже, чтобы открыть наше веб-приложение:",
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
    await message.answer("Привет! Скажи сколько тебе лет.")
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
        await prepare_link(message)
    except ValueError:
        await message.answer("Возраст выходит за рамки или не является чилом. Введите еще раз.")


def make_reg(message, age, picture_path):
    d = {
        'tg_id': message.from_user.id,
        'name': message.from_user.first_name,
        'capture': '-',
        'picture': picture_path,
        'old': age,
        'disabled': False
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


async def main():
    await dp.start_polling(bot)


@routes.post("/json")
async def handle_json(request):
    try:
        data = await request.json()
        logging.info(f"Got JSON: {data}")
        await message_like(data)
        return web.json_response({"status": "ok"})
    except Exception as e:
        logging.exception("Error handling JSON:")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


async def start():
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 3000)
    await site.start()
    print("Server started on http://0.0.0.0:3000")
    loop = asyncio.get_event_loop()
    await loop.create_task(dp.start_polling(bot))


if __name__ == "__main__":
    asyncio.run(start())
