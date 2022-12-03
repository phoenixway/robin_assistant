#!/usr/bin/env python3
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from yapsy.IPlugin import IPlugin
log = logging.getLogger('pythonConfig')


class PluginOne(IPlugin):
    modules = None

    async def do_work(self):
        log.debug("Doing work")
        PluginOne.modules['ai_core'].start_story('robin_asks')

    def startup_handler(self):
        db = PluginOne.modules['db']
        today = datetime.today() \
            .strftime('%Y-%m-%d')
        if ('last_login_date' in db.keys()) and db['last_login_date'] == today:
            PluginOne.modules['messages'].say('Welcome back')
        else:
            PluginOne.modules['messages'].say('Good to see you')
            db['last_login_date'] = today

    async def activate(self, modules):
        PluginOne.modules = modules
        log.debug("Activating plugin for doing most important task..")
        # FIXME: new event - userconnected
        modules['events'].addListener('startup', self.startup_handler)
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.do_work, 'interval', minutes=1,
                          id="do_most_important_id")
        scheduler.start()
