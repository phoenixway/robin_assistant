import asyncio
import datetime


1#!/usr/bin/env python3

class Watcher:
    def __init__(self, modules):
        self.MODULES = modules
    async def watch(self):
        while True:
            await asyncio.sleep(60*60)
            log.debug("im watch")
            ws_server = self.MODULES['ws_server']
            dt = datetime.today().strftime('%Y-%m-%d')
            db = self.MODULES['db']
            if not db.get('dayplanned') or db.get('dayplanned') != dt:
                m = "You did not plan your day!"
                await ws_server.say(m)