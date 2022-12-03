#!/usr/bin/env python3
import logging
import asyncio
import aioschedule as schedule
from yapsy.IPlugin import IPlugin
log = logging.getLogger('pythonConfig')


class PluginOne(IPlugin):
    def do_work(self, modules):
        log.debug("Doing work")

    async def activate(self, modules):
        log.debug("Activating plugin for doing most important task..")
        schedule.every(1).minutes.do(self.do_work, modules)
        loop = asyncio.get_event_loop()
        while True:
            loop.run_until_complete(schedule.run_pending())
            await asyncio.sleep(10)
