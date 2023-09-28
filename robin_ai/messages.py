#!/usr/bin/env python3
import websockets
import nest_asyncio
import logging
import asyncio
import signal
import sys

try:
    from .actions_queue import Action
    from .actions_queue import ActionType
except ImportError:
    from actions_queue import Action
    from actions_queue import ActionType

nest_asyncio.apply()
background_tasks = set()
log = logging.getLogger('pythonConfig')


class Messages:

    def __init__(self, action_queue, event_manager, debug_server=False):
        self.debug_server = debug_server
        self.action_queue = action_queue
        self.events = event_manager
        self.websocket = None
        self.websockets = []
        self.telegram_works = False
        self.telegram_client_id = 612272249
        self.t = None
        self.is_started = False
        self.prev_message = ""
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

    async def say_async(self, message):
        await self.ws_say(message)

    def say(self, message):
        if not self.websockets or self.prev_message == message:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            t = loop.create_task(self.say_async(message))
            background_tasks.add(t)
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
                self.action_queue.add_action(Action(ActionType.RespondToUserMessage, input_text))
                error = False
                log.debug(f"Ws server received: {input_text}")
                if not self.debug_server:
                    self.events.emit('message_received', input_text)
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

    async def serve(self):
        t = asyncio.create_task(self.ws_serve())
        background_tasks.add(t)
