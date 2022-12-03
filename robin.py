#!/usr/bin/env python3
import asyncio
import sys
import shelve
import logging
import nest_asyncio
from colorlog import ColoredFormatter

from robin_events import Robin_events
from messages import Messages
from watcher import Watcher
from ai_core2.ai_core import AICore

nest_asyncio.apply()
log = None
MODULES = {}


def init_logger():
    global log
    log = logging.getLogger('pythonConfig')
    if len(sys.argv) > 1:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    LOGFORMAT = "%(log_color)s%(levelname)-6s%(reset)s %(message)-40s %(reset)s %(log_color)s%(filename)s:%(lineno)s <- %(funcName)s() %(reset)s"  # noqa: E501
    formatter = ColoredFormatter(LOGFORMAT)
    ch.setFormatter(formatter)
    log.addHandler(ch)


def init_modules():
    global MODULES
    MODULES['events'] = Robin_events()
    MODULES['watcher'] = Watcher(MODULES)
    MODULES['messages'] = Messages(MODULES)
    MODULES['db'] = shelve.open('memory')
    MODULES['ai_core'] = AICore(MODULES)


async def quit_handler(data):
    log.debug("quit_handler launched")
    m = MODULES['messages']
    m.say("Good bye, master!")
    try:
        m.stop()
        loop = asyncio.get_running_loop()
        pending = asyncio.all_tasks()
        MODULES['db'].close()
        for task in pending:
            task.cancel()
        loop.stop()
        exit(0)
    except:
        pass
    # m.t.join()    # wait for the thread to finish what it's doing
    # m.t.close()   
    # m.t.stop()
    


async def start_handler(data):
    MODULES['messages'].say("Connected.")
    asyncio.create_task(MODULES['ai_core'].message_received_handler(None))
    log.debug("Start_handler called")


async def startup_finisher():
    finished = False
    while not finished:
        await asyncio.sleep(5)
        finished = MODULES['messages'].is_started and MODULES['events'].is_started and MODULES['ai_core'].is_started  # noqa: E501
    MODULES['events'].emit('startup', None)


async def async_modules():
    loop = asyncio.get_event_loop()
    loop.create_task(MODULES['messages'].serve())
    loop.create_task(startup_finisher())
    loop.create_task(MODULES['watcher'].watch())
    # asyncio.gather(MODULES['messages'].serve(), MODULES['watcher'].watch(), startup_finisher())  # noqa: E501
    loop.run_forever()
    log.debug("async modules finished")


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
except asyncio.exceptions.CancelledError:
    pass
finally:
    try:
        asyncio.run(quit_handler(None))
    except asyncio.exceptions.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        log.info('Bye')
