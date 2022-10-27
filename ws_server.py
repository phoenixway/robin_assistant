#!/usr/bin/env python3
import asyncio
from datetime import datetime
from icecream import ic
import websockets
from termcolor import colored
from colorlog import ColoredFormatter
import asyncio
import shelve
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
    def __init__(self):
        self.websocket = None

    async def say(self, message):
        global no_error
        if no_error and self.websocket:
            try:
                await self.websocket.send(message)
                log.debug(f"Server sent: {message}")
            except websockets.exceptions.ConnectionClosedOK:
                log.error('ConnectionClosedOK')
                no_error = False

    async def echo(self, websocket):
        global no_error, MODULES
        self.websocket = websocket
        while no_error:
            try:
                name = await websocket.recv()
                log.debug(f"Received: {name}")
                greeting = f"Hello {name}!"
                await websocket.send(greeting)
                log.debug(f"Server sent: {greeting}")
            except websockets.exceptions.ConnectionClosedOK:
                log.error('ConnectionClosedOK')
                no_error = False

    async def ws_handle(self):
        await websockets.serve(self.echo, "localhost", 8765)
        await asyncio.Future()  # run forever