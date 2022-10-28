#!/usr/bin/env python3
import asyncio
import shelve
from icecream import ic
import logging
from ws_server import Ws_server
from watcher import Watcher
from ai_core import AICore

log = logging.getLogger('pythonConfig')
MODULES = dict()

watcher = Watcher(MODULES)
ws_server = Ws_server(MODULES)
db = shelve.open('spam')
#del db['dayplanned']
aicore = AICore()

MODULES['watcher'] = watcher
MODULES['ws_server'] = ws_server
MODULES['db'] = db
MODULES['ai_core'] = aicore

async def main():
    results = await asyncio.gather(ws_server.ws_handle(), watcher.watch())
    ic(results)

log.info('Welcome!')

try:
    asyncio.run(main())
except KeyboardInterrupt:
    ic('Bye')