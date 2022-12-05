#!/usr/bin/env python3
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from yapsy.IPlugin import IPlugin
log = logging.getLogger('pythonConfig')


class PArtOfLiving(IPlugin):
    modules = None

    async def do_work(self):
        log.debug("Doing work")
        ai = PArtOfLiving.modules['ai_core']
        lst = [i for i in ai.stories
               if i.name == "do_most_important"]
        if lst:
            first_question = lst[0].first_node.text
            if len(ai.log) == 0 or (len(ai.log) > 0 and ai.log[-1] !=
                                    first_question):
                ai.add_own_will_story("do_most_important")
                ai.force_own_will_story()

    async def user_connect_handler(self, event):
        db = PArtOfLiving.modules['db']
        today = datetime.today() \
            .strftime('%Y-%m-%d')
        if ('last_login_date' in db.keys()) and db['last_login_date'] == today:
            PArtOfLiving.modules['messages'].say('Welcome back')
        else:
            PArtOfLiving.modules['messages'].say('Good to see you')
            db['last_login_date'] = today

    async def activate(self, modules):
        log.debug("Activating plugin for doing most important task..")
        PArtOfLiving.modules = modules
        ai = modules['ai_core']
        modules['events'].add_listener('user_connected',
                                       self.user_connect_handler)
        # TODO: дві історії, одна щодо планування дня
        ai.add_story_by_source("""
            story do_most_important {
                > Are u doing the currently most important task now?
                <if in>
                    <intent>yes => {
                        > Great, as expected!
                    }
                    <intent>no => {
                        > Why dont u do that right now?
                        <if in>
                            <intent>yes => {
                                > Do ur best!
                            }
                            stick to not so important => {
                                > Just stop what u doing and think about consenquests, responsibility, etc
                            }
                            low energy => {
                                > Stop doing non-important, get more energy. Master, u can!
                            }
                            dont want => {
                                > What about Levi's method?
                                < dont want
                                > Are u realize the consequences? Do you accept them? Responsibility for them?
                                <if in>
                                    <intent>yes => {
                                        > Then let's them be. 
                                    }
                                    <intent>no => {
                                        > Think of them!
                                    }
                                </if>
                            }
                            <intent>no => {
                                > Think about what prevents u from that? Do u realize consenquests of skipping? Do u accept own responsibility for not doing most important task?
                                <if in>
                                    <intent>yes => {
                                        > Why dont at least stop doing not important things right now?
                                    }
                                    <intent>no => {
                                        > Think about it. Pull yourself together!
                                        <if in>
                                            <intent>yes => {
                                                > Please, be the best version of yourself!
                                            }
                                            <intent>no => {
                                                > U will get all consenquests.
                                            }
                                        </if>
                                    }
                                </if>
                            }
                        </if>
                    }
                </if>
            }
        """)
        # FIXME: new event - userconnected
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.do_work, 'interval', minutes=1,
                          id="do_most_important_id")
        scheduler.start()
