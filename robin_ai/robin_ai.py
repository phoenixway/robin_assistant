#!/usr/bin/env python3

import asyncio
import sys
import logging
import nest_asyncio
from colorlog import ColoredFormatter
from os import _exit

try:
    from .robin_db import RobinDb
    from .robin_events import Robin_events
    from .messages import Messages
    from .plugin_manager import Plugins
    from .ai_core2.ai_core import AI
    from .handle_config import init_config
    from .actions_queue import ActionsQueue
except ImportError:
    from robin_db import RobinDb
    from robin_events import Robin_events
    from messages import Messages
    from plugin_manager import Plugins
    from ai_core2.ai_core import AI
    from handle_config import init_config
    from actions_queue import ActionsQueue


nest_asyncio.apply()
log = None
MODULES = {}


def close_server():
    sys.exit(0)


def init_logger():
    global log
    log = logging.getLogger('pythonConfig')
    if (hasattr(sys, 'gettrace') and sys.gettrace() is not None) or (len(sys.argv) > 1):
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    LOGFORMAT = "%(log_color)s%(levelname)-6s%(reset)s %(message)-40s %(reset)s %(log_color)s%(filename)s:%(lineno)s <- %(funcName)s() %(reset)s"  # noqa: E501
    formatter = ColoredFormatter(LOGFORMAT)
    ch.setFormatter(formatter)
    log.addHandler(ch)


def init_modules():
    global MODULES
    MODULES['config'] = init_config()
    MODULES['config']['debug_server_mode'] = False
    MODULES['config']['debug'] = True if (hasattr(sys, 'gettrace') and sys.gettrace() is not None) or (len(sys.argv) > 1) else False
    debug_server_mode = MODULES['config']['debug_server_mode']
    actions_queue = ActionsQueue()
    MODULES['actions_queue'] = actions_queue
    events = None
    if not debug_server_mode:
        events = MODULES['events'] = Robin_events()
        MODULES['plugins'] = Plugins(MODULES)
    MODULES['messages'] = Messages(actions_queue, events)
    actions_queue.send_message_callback = MODULES['messages'].say
    
    if not debug_server_mode:
        MODULES['db'] = RobinDb('memory', MODULES)
        MODULES['ai'] = AI(MODULES)
        actions_queue.respond_to_user_message_callback = MODULES['ai'].respond
        actions_queue.force_own_will_callback = MODULES['ai'].force_own_will_story

    actions_queue.close_server_callback = close_server

async def quit_handler(data):
    log.debug("quit_handler launched")
    m = MODULES['messages']
    m.say("Good bye, master!")
    # try:
    m.stop()
    loop = asyncio.get_running_loop()
    pending = asyncio.all_tasks()
    if 'db' in MODULES and MODULES['db']:
        MODULES['db'].close()
    for task in pending:
        task.cancel()
    loop.stop()
    try:
        sys.exit(0)
    except SystemExit:
        log.info('Bye')
        _exit(0)
    # except:
    #     pass
    # m.t.join()    # wait for the thread to finish what it's doing
    # m.t.close()
    # m.t.stop()


async def start_handler(data):
    log.debug("Start_handler called")
    # MODULES['messages'].say("Connected.")
    asyncio.create_task(MODULES['ai'].message_received_handler(None))


async def startup_finisher():
    if not MODULES['config']['debug_server_mode']:
        finished = False
        while not finished:
            await asyncio.sleep(5)
            finished = MODULES['messages'].is_started and MODULES['events'].is_started and MODULES['ai'].is_started  # noqa: E501
        MODULES['events'].emit('startup', None)


async def async_modules():
    loop = asyncio.get_event_loop()
    loop.create_task(MODULES['actions_queue'].listen_queue())
    loop.create_task(MODULES['messages'].serve())
    loop.create_task(startup_finisher())
    if not MODULES['config']['debug_server_mode']:
        loop.create_task(MODULES['plugins'].activate())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        log.debug("async modules finished")


def main():
    init_logger()
    log.info('Welcome!')
    init_modules()
    if not MODULES['config']['debug_server_mode']:
        MODULES['events'].add_listener('startup', start_handler)
        MODULES['events'].add_listener('quit', quit_handler)

    try:
        asyncio.run(async_modules())
    except (KeyboardInterrupt, RuntimeError):
        pass
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        asyncio.run(quit_handler(None))


if __name__ == "__main__":
    main()
