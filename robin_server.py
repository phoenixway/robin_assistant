#!/usr/bin/env python3
import asyncio
import shelve
import logging

from robin_events import Robin_events
from messages import Messages
from watcher import Watcher
from ai_core import AICore


log = logging.getLogger('pythonConfig')
MODULES = dict()

watcher = Watcher(MODULES)
messages = Messages(MODULES)
db = shelve.open('spam')
#del db['dayplanned']
aicore = AICore(MODULES)

MODULES['watcher'] = watcher
MODULES['messanges'] = messages
MODULES['db'] = db
MODULES['ai_core'] = aicore
MODULES['events'] = Robin_events()


def startup(e):
    log.debug("It's startup event!")

def quit():
    log.debug("It's quit event!")
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        t = loop.create_task(MODULES['messages'].say('Good bye'))
        # t.add_done_callback(lambda t: print(f'{t} done!')) 
    else:
        asyncio.run(MODULES['messages'].say('Good bye'))
    loop.stop()
    exit(0)

MODULES['events'].on_startup += startup 
MODULES['events'].on_quit += quit

async def fire_startup():
    MODULES['events'].on_startup('')

async def main():
    results = await asyncio.gather(messages.ws_serve(), watcher.watch(), fire_startup(), messages.telegram_serve())
    log.debug(results)

log.info('Welcome!')

try:
    asyncio.run(main())
except KeyboardInterrupt:
    log.info('Bye')
except RuntimeError:
    log.info('Bye')