#!/usr/bin/env python3

import asyncio
import datetime

class Watcher:
    def __init__(self, modules):
        self.MODULES = modules
    async def watch(self):
        while True:
            await asyncio.sleep(60*60)
            log.debug("im watch")
            messages = self.MODULES['messages']
            dt = datetime.today().strftime('%Y-%m-%d')
            db = self.MODULES['db']
            if not db.get('dayplanned') or db.get('dayplanned') != dt:
                m = "You did not plan your day!"
                await messages.say(m)