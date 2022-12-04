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
        a = PluginOne.modules['ai_core']
        lst = [i for i in a.stories
               if i.name == "robin_asks"]
        if lst:
            first_question = lst[0].first_node.text
            if a.log[-1] != first_question:
                a.start_story("robin_asks")

    async def user_connect_handler(self, event):
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
        modules['events'].add_listener('user_connected',
                                       self.user_connect_handler)
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.do_work, 'interval', minutes=1,
                          id="do_most_important_id")
        scheduler.start()
