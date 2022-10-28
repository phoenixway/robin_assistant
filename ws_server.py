#!/usr/bin/env python3
import asyncio
from datetime import datetime
from icecream import ic
import websockets
from termcolor import colored
from colorlog import ColoredFormatter
import asyncio
from datetime import datetime
from icecream import ic
import websockets
import logging
from termcolor import colored
from colorlog import ColoredFormatter

no_error = True

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


class Ws_server:
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
        while no_error:
            try:
                input_text = await websocket.recv()
                log.debug(f"Received: {input_text}")
                answer = self.MODULES['ai_core'].parse(input_text)
                await websocket.send(answer)
                log.debug(f"Server sent: {answer}")
            except websockets.exceptions.ConnectionClosedOK:
                log.error('ConnectionClosedOK')
                no_error = False

    async def ws_handle(self):
        await websockets.serve(self.handle, "localhost", 8765)
        await asyncio.Future()  # run forever