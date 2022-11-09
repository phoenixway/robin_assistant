#!/usr/bin/env python3
import asyncio, shelve, logging, nest_asyncio
from colorlog import ColoredFormatter

from robin_events import Robin_events
from messages import Messages
from watcher import Watcher
from ai_core import AICore

nest_asyncio.apply()
log = None
MODULES = dict()

def init_logger():
    global log
    log = logging.getLogger('pythonConfig')
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    LOGFORMAT = "%(log_color)s%(levelname)-6s%(reset)s %(message)-40s %(reset)s %(log_color)s%(filename)s:%(lineno)s <- %(funcName)s() %(reset)s"
    formatter = ColoredFormatter(LOGFORMAT)
    ch.setFormatter(formatter)
    log.addHandler(ch)

def init_modules():
    global MODULES
    MODULES['events'] = Robin_events()
    MODULES['watcher'] = Watcher(MODULES)
    MODULES['messages'] = Messages(MODULES)
    MODULES['db'] = shelve.open('spam')
    MODULES['ai_core'] = AICore(MODULES)

async def quit_handler(data):
    log.debug("quit_handler launched")
    m = MODULES['messages']
    m.say("Good bye, master!")
    loop = asyncio.get_running_loop()
    pending = asyncio.all_tasks()
    for task in pending:
        task.cancel()
    loop.stop()
    # m.t.stop()
    exit(0)

async def start_handler(data):
    MODULES['messages'].say("Connected.")
    asyncio.create_task(MODULES['ai_core'].message_received_handler(None))
    log.debug("Start_handler called")

async def startup_finisher():
    finished = False
    while not finished:
        await asyncio.sleep(5)
        finished = MODULES['messages'].is_started and MODULES['events'].is_started and MODULES['ai_core'].is_started
    MODULES['events'].emit('startup', None)

async def async_modules():
    results = await asyncio.gather(MODULES['messages'].serve(), MODULES['watcher'].watch(), startup_finisher())
    log.debug(results)

init_logger()
log.info('Welcome!')
init_modules()
MODULES['events'].add_listener('startup', start_handler)
MODULES['events'].add_listener('quit', quit_handler)

try:
    asyncio.run(async_modules())
except KeyboardInterrupt:
    pass
except RuntimeError:
    pass
finally:
    try:
        asyncio.run(quit_handler(None))
    except:
        pass
    finally:
        log.info('Bye')
