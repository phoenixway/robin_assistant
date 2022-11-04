#!/usr/bin/env python3
import asyncio
import shelve
import logging
import time
from colorlog import ColoredFormatter
from robin_events import Robin_events

from messages import Messages
from watcher import Watcher
from ai_core import AICore
import logging
# coloredlogs.install()

log = logging.getLogger('pythonConfig')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
LOGFORMAT = "%(log_color)s%(levelname)-6s%(reset)s %(message)-40s %(reset)s %(log_color)s%(filename)s:%(lineno)s <- %(funcName)s() %(reset)s"
formatter = ColoredFormatter(LOGFORMAT)
ch.setFormatter(formatter)
log.addHandler(ch)

MODULES = dict()

watcher = Watcher(MODULES)
messages = Messages(MODULES)
db = shelve.open('spam')
aicore = AICore(MODULES)

MODULES['watcher'] = watcher
MODULES['messages'] = messages
MODULES['db'] = db
MODULES['ai_core'] = aicore
MODULES['events'] = Robin_events()



def startup_handler(e):
    log.debug("It's startup event!")

def quit_handler():
    log.debug("quit_handler launched")
    m = MODULES['messages']
    m.say("Good bye, master!")
    loop = asyncio.get_running_loop()
    loop.stop()
    # m.t.stop()
    exit(0)

MODULES['events'].on_startup += startup_handler 
MODULES['events'].on_quit += quit_handler

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