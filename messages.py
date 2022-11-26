#!/usr/bin/env python3
import asyncio
import nest_asyncio
import websockets
import logging
from tgclient import *

nest_asyncio.apply()
background_tasks = set()
TELEGRAM_BOT_TOKEN = r"5700563667:AAG0Q-EK3f7hGo4EcwISGC87gIJ40morNTs"
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN)
log = logging.getLogger('pythonConfig')


class Messages:

    def __init__(self, modules):
        self.websocket = None
        self.MODULES = modules
        self.telegram_client_id = 612272249
        self.t = None
        self.is_started = False

    async def say_async(self, message):
        await self.ws_say(message)
        try:
            self.telegram_say(message)
        except:
            log.error('An exception telegram bot when sending message.')       

    def say(self, message):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            t = loop.create_task(self.say_async(message))
            background_tasks.add(t)
            # t.add_done_callback(background_tasks.remove(t))
            loop.run_until_complete(t)
        else:
            asyncio.set_event_loop(asyncio.new_event_loop())
            asyncio.run(self.say_async(message))
        self.MODULES['events'].emit('message_send', message)

    def stop(self):
        self.t.stop()

    async def ws_say(self, message):
        if self.websocket:
            try:
                await self.websocket.send(message)
                log.debug(f"Ws server sent: {message}")
            except websockets.exceptions.ConnectionClosedOK:
                log.error("Ws server can't send a message because client closed the connection.")
            except websockets.exceptions.ConnectionClosedError:
                log.error("Ws server can't send a message because of incorrectly closed connection.")

    def get_answer(self, message):
        log.debug(f"get answer for: {message}")
        return self.MODULES['ai_core'].respond(message)

    def telegram_say(self, message):
        try:
            telegram_bot.sendMessage(chat_id=self.telegram_client_id, text=message)
            log.debug(f"Telegrambot sent: {message}")
        except:
            print("telegram_say error")

    async def ws_process(self, websocket):
        self.websocket = websocket
        self.is_started = True
        error = False
        while True:
            try:
                input_text = await websocket.recv()
                error = False
                log.debug(f"Ws server received: {input_text}")
                self.telegram_say(f"Ws server received: {input_text}")
                self.MODULES['events'].emit('message_received', input_text)
                answer = self.get_answer(input_text)
                await self.say_async(answer)
            except websockets.exceptions.ConnectionClosedOK:
                if not error:
                    log.info('Ws connection is closed by client.')
                    error = True
            except websockets.exceptions.ConnectionClosedError:
                if not error:
                    log.info("Ws connection error.")
                    error = True
            except KeyboardInterrupt:
                log.info("Keyboard interrupts.")

    async def ws_serve(self):
        while True:
            try:
                log.debug("Ws server started.")
                await websockets.serve(self.ws_process, "localhost", 8765)
                await asyncio.Future()
            except:
                log.error("Ws server exception")
            # except websockets.exceptions.ConnectionClosedOK:
            #     log.error('ConnectionClosedOK')

    def run_telegram_bot(self):
        log.debug('Telegram bot started.')
        @telegram_bot.message("text")
        def text(message):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            t = loop.create_task(self.ws_say(f"TelegramBot received: {message['text']}"))
            background_tasks.add(t)
            # t.add_done_callback(background_tasks.remove(t))
            loop.run_until_complete(t)
            loop.close()
            log.debug(f"TelegramBot received: {message['text']}")
            answer = self.get_answer(message['text'])
            self.telegram_client_id = message['chat']['id']
            log.debug(f"{self.telegram_client_id}")
            asyncio.run(self.say(answer))

        telegram_bot.run()

    async def telegram_serve(self):
        import threading
        self.t = threading.Thread(target=self.run_telegram_bot)
        self.t.daemon = True
        self.t.start()

    async def serve(self):
        t = asyncio.create_task(self.ws_serve())
        background_tasks.add(t)
        # t.add_done_callback(background_tasks.remove(t))
        t1 = asyncio.create_task(self.telegram_serve())
        background_tasks.add(t1)

