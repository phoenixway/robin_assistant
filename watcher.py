#!/usr/bin/env python3

import asyncio
import logging
import datetime as dt
import aioschedule as schedule
import time

log = logging.getLogger('pythonConfig')


class Watcher:
    def __init__(self, modules):
        self.MODULES = modules
        # schedule.cyclic(dt.timedelta(minutes=7), self.helper)

    async def helper(self):
        log.debug("Helping run.")
        self.MODULES['ai_core'].start_story("robin_asks")

    async def watch(self):
        log.debug("I'm Watcher and I'm watching!")
        # ai_core = self.MODULES['ai_core']
        # while True:
        #     await asyncio.sleep(4)
        schedule.every(10).minutes.do(self.helper)
        loop = asyncio.get_event_loop()
        while True:
            loop.run_until_complete(schedule.run_pending())
            await asyncio.sleep(4)
        # ai_core.start_story('robin_asks')
        # while True:
        #     await asyncio.sleep(60*35)
            
            # messages = self.MODULES['messages']
            # dt = datetime.today().strftime('%Y-%m-%d')
            # db = self.MODULES['db']
            # if not db.get('dayplanned') or db.get('dayplanned') != dt:
            #     m = "You did not plan your day!"
            #     await messages.say_async(m)