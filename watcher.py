#!/usr/bin/env python3

import asyncio
import datetime
import logging

log = logging.getLogger('pythonConfig')

class Watcher:
    def __init__(self, modules):
        self.MODULES = modules
    async def watch(self):
        log.debug("I'm Watcher and I'm watching!")
        # ai_core = self.MODULES['ai_core']
        while True:
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