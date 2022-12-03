#!/usr/bin/env python3
import logging
# import asyncio
# import aioschedule as schedule
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from yapsy.IPlugin import IPlugin
log = logging.getLogger('pythonConfig')


class PluginOne(IPlugin):
    modules = None

    async def do_work(self):
        log.debug("Doing work")
        PluginOne.modules['ai_core'].start_story('robin_asks')

    async def activate(self, modules):
        PluginOne.modules = modules
        log.debug("Activating plugin for doing most important task..")
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.do_work, 'interval', minutes=1,
                          id="do_most_important_id")
        scheduler.start()
