#!/usr/bin/env python3
import asyncio
import shelve
from datetime import datetime
from icecream import ic
import websockets
import logging
from termcolor import colored
from colorlog import ColoredFormatter
from ws_server import Ws_server
from watcher import Watcher

log = logging.getLogger('pythonConfig')
MODULES = dict()

watcher = Watcher(MODULES)
ws_server = Ws_server()
db = shelve.open('spam')
#del db['dayplanned']

MODULES['watcher'] = watcher
MODULES['ws_server'] = ws_server
MODULES['db'] = db

async def main():
    results = await asyncio.gather(ws_server.ws_handle(), watcher.watch())
    ic(results)

log.info('Welcome!')

try:
    asyncio.run(main())
except KeyboardInterrupt:
    ic('Bye')