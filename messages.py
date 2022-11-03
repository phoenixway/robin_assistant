#!/usr/bin/env python3
import asyncio
from datetime import datetime
import websockets
from colorlog import ColoredFormatter
import asyncio
from datetime import datetime
import websockets
import logging
from colorlog import ColoredFormatter
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # for reply keyboard (sends message)

from time import sleep

no_error = True
# bot = Bot(token=token)
# dp = Dispatcher(bot)
# answers = []  # store the answers they have given
# executor.start_polling(dp)

# lang1 = KeyboardButton('English 👍')  
# lang2 = KeyboardButton('українська 💪')
# lang3 = KeyboardButton('Other language 🤝')
# lang_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(lang1).add(lang2).add(lang3)

# # sends welcome message after start
# @dp.message_handler(commands=['start'])
# async def welcome(message: types.Message):
#     await message.answer('Hello! Please select your language.\nПривіт! Виберіть мову.', reply_markup = lang_kb)
    
# # sends help message
# @dp.message_handler(commands=['help'])
# async def help(message: types.Message):
#     await message.answer('We are a team of LGBT organizations from across Europe. We help you get into safety, provide support and answer any questions you may have. Press /start to get started. \nМи — команда ЛГБТ-організацій з усієї Європи. Ми допомагаємо вам увійти в безпеку, надаємо підтримку та відповідаємо на будь-які ваші запитання. Натисніть /start, щоб почати.')

LOGFORMAT = '%(log_color)s %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s'
LOG_LEVEL = logging.DEBUG
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)


class Messages:
    def __init__(self, modules):
        self.websocket = None
        self.MODULES = modules

    async def say(self, message):
        global no_error
        if no_error and self.websocket:
            try:
                await self.websocket.send(message)
                log.debug(f"Server sent: {message}")
            except websockets.exceptions.ConnectionClosedOK:
                log.error('ConnectionClosedOK')
                no_error = False

    async def handle(self, websocket):
        global no_error
        self.websocket = websocket
        while True:
            input_text = await websocket.recv()
            log.debug(f"Received: {input_text}")
            answer = self.MODULES['ai_core'].parse(input_text)
            await websocket.send(answer)
            log.debug(f"Server sent: {answer}")

    async def ws_handle(self):
        while True:
            try:
                await websockets.serve(self.handle, "localhost", 8765)
                await asyncio.Future()
            except websockets.exceptions.ConnectionClosedOK:
                log.error('ConnectionClosedOK')
        
          # run forever