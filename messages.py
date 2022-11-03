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
from tgclient import *
from time import sleep
import inspect

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

TELEGRAM_BOT_TOKEN = r"5700563667:AAG0Q-EK3f7hGo4EcwISGC87gIJ40morNTs"
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN)

class Messages:
   
    def __init__(self, modules):
        self.websocket = None
        self.MODULES = modules
        self.telegram_client_id = None
        self.msg_id = None

    async def say(self, message):
        try:
          await self.ws_say(message)
        except:
          print('An exception wsserver')
        try:
          self.telegram_say(message)
        except:
          print('An exception telegram b')       
        

    async def ws_say(self, message):
        if self.websocket:
            try:
                await self.websocket.send(message)
                log.debug(f"Ws server sent: {message}")
            except websockets.exceptions.ConnectionClosedOK:
                log.error('ConnectionClosedOK')

    def get_answer(self, message):
        return self.MODULES['ai_core'].parse(message)
    
    def telegram_say(self, message):
        # log.debug(f"{inspect[0][3]}: message '{message}'")
        try:
          telegram_bot.sendMessage(chat_id=self.telegram_client_id, text=message)
        except:
          print("telegram_say error")
        
    
    async def ws_process(self, websocket):
        self.websocket = websocket
        while True:
            input_text = await websocket.recv()
            log.debug(f"Ws server received: {input_text}")
            self.telegram_say(f"Ws server received: {input_text}")
            answer = self.get_answer(input_text)
            await self.say(answer)

    async def ws_serve(self):
        while True:
            try:
                log.debug("Ws server started.")
                await websockets.serve(self.ws_process, "localhost", 8765)
                await asyncio.Future()
            except websockets.exceptions.ConnectionClosedOK:
                log.error('ConnectionClosedOK')

    def run_tlbot(self):
        log.debug('Telegram bot started.')
        @telegram_bot.message("text")
        def text(message):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            t = loop.create_task(self.ws_say(f"TelegramBot received: {message['text']}"))
            loop.run_until_complete(t)
            loop.close()
            answer = self.get_answer(message['text'])
            self.telegram_client_id = message['chat']['id']
            asyncio.run(self.say(answer))
        
        telegram_bot.run()

    async def telegram_serve(self):
        import threading
        t=threading.Thread(target=self.run_tlbot)
        t.daemon = True
        t.start()
        

