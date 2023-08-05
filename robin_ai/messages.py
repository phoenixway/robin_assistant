#!/usr/bin/env python3
import websockets
import nest_asyncio
import logging
import asyncio
import signal
import sys

try:
    from .actions_queue import RespondToUserMessageAction
except ImportError:
    from actions_queue import RespondToUserMessageAction
#from robin_ai.robin_ai import MODULES
# from tgclient import TelegramBot

nest_asyncio.apply()
background_tasks = set()
TELEGRAM_BOT_TOKEN = r"5700563667:AAG0Q-EK3f7hGo4EcwISGC87gIJ40morNTs"
# telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN)
log = logging.getLogger('pythonConfig')


class Messages:

    def __init__(self, action_queue, event_manager, debug_server=False):
        self.debug_server = debug_server
        self.action_queue = action_queue
        self.events = event_manager
        self.websocket = None
        self.websockets = []
        self.telegram_works = False
        # self.MODULES = modules
        self.telegram_client_id = 612272249
        self.t = None
        self.is_started = False
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            self.ws_stop = loop.create_future()
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.ws_stop = loop.create_future()
        loop.add_signal_handler(signal.SIGTERM, self.ws_stop.set_result, None)
        # self.ws_stop = asyncio.Future()

    async def say_async(self, message):
        await self.ws_say(message)
        # try:
        # if self.telegram_works:
        #     self.telegram_say(message)
        # except:
        # log.error('An exception telegram bot when sending message.')

    def say(self, message):
        if not self.websockets:
            return
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
        self.events.emit('message_send', message)

    def stop(self):
        self.ws_stop.set_result(None)
        if self.t:
            self.t.stop()

    async def ws_say(self, message):
        if self.websocket:
            try:
                await self.websocket.send(message)
                log.debug(f"Ws server sent: {message}")
            except websockets.exceptions.ConnectionClosedOK:
                log.error("Ws server can't send a message because client \
                           closed the connection.")
            except websockets.exceptions.ConnectionClosedError:
                log.error("Ws server can't send a message because of \
                           incorrectly closed connection.")

    # def get_answer(self, message):
    #     log.debug(f"get answer for: {message}")
    #     if not self.debug_server:
    #         self.action_queue.add_action(RespondToUserMessageAction(message))
    #     return ["deprecated"] #if self.debug_server else self.MODULES['ai'].respond_text(message)

    # def telegram_say(self, message):
    #     # try:
    #     # telegram_bot.sendMessage(chat_id=self.telegram_client_id
    #     # text=message)
    #     log.debug(f"Telegrambot sent: {message}")
    #     # except:
    #     # print("telegram_say error")

    async def ws_process(self, websocket):
        self.websockets.append(websocket)
        log.info("User connected via websocket protocol.")
        if not self.debug_server:
            self.events.emit('user_connected', None)
        self.websocket = websocket
        error = False
        while True:
            try:
                input_text = await websocket.recv()
                self.action_queue.add_action(RespondToUserMessageAction(input_text))
                error = False
                log.debug(f"Ws server received: {input_text}")
                # TODO: telegram optionally
                # if self.telegram_works:
                #     self.telegram_say(f"Ws server received: {input_text}")
                if not self.debug_server:
                    self.events.emit('message_received', input_text)
                # if answers := self.get_answer(input_text):
                #     for a in answers:
                #         await self.say_async(a)
            except websockets.exceptions.ConnectionClosedOK:
                if not error:
                    log.info('Ws connection is closed by client.')
                    self.websockets.remove(websocket)
                    error = True
                    break
            except websockets.exceptions.ConnectionClosedError:
                if not error:
                    log.info("Ws connection error.")
                    self.websockets.remove(websocket)
                    error = True
                    break
            except KeyboardInterrupt:
                log.info("Keyboard interrupts.")
                self.websockets.remove(websocket)
                break

    async def ws_serve(self):
        while True:
            # try:
            self.is_started = True
            log.debug("Ws server started.")
            ws = await websockets.serve(self.ws_process, "localhost", 8765)
            await ws.wait_closed()
            await self.ws_stop
            loop = asyncio.get_event_loop()
            loop.run_until_complete(ws)
            # async with websockets.serve(self.ws_process, "localhost", 8765):
            #     log.debug("that")
            #     await self.ws_stop
            # except:
            #     log.error("Ws server exception")
            # except websockets.exceptions.ConnectionClosedOK:
            #     log.error('ConnectionClosedOK')

    # def run_telegram_bot(self):
    #     log.debug('Deprecated.')

        # @telegram_bot.message("text")
        # def text(message):
        #     loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(loop)
        #     t = loop.create_task(self.ws_say(
        #         f"TelegramBot received: {message['text']}"))
        #     background_tasks.add(t)
        #     # t.add_done_callback(background_tasks.remove(t))
        #     loop.run_until_complete(t)
        #     loop.close()
        #     log.debug(f"TelegramBot received: {message['text']}")
        #     answer = self.get_answer(message['text'])
        #     self.telegram_client_id = message['chat']['id']
        #     log.debug(f"{self.telegram_client_id}")
        #     asyncio.run(self.say(answer))

        # telegram_bot.run()

    # async def telegram_serve(self):
    #     import threading
    #     self.t = threading.Thread(target=self.run_telegram_bot)
    #     self.t.daemon = True
    #     self.t.start()

    async def serve(self):
        t = asyncio.create_task(self.ws_serve())
        background_tasks.add(t)
        # t.add_done_callback(background_tasks.remove(t))
        # t1 = asyncio.create_task(self.telegram_serve())
        # background_tasks.add(t1)
