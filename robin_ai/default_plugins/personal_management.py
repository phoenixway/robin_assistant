#!/usr/bin/env python3
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from yapsy.IPlugin import IPlugin
log = logging.getLogger('pythonConfig')


class PArtOfLiving(IPlugin):
    modules = None

    async def do_regular_work(self):
        log.debug("Doing regular work")
        ai = PArtOfLiving.modules['ai']
        lst = [i for i in ai.stories
               if i.name == "do_most_important"]
        if lst:
            first_question = lst[0].first_node.value
            if len(ai.history) == 0 or (len(ai.history) > 0 and ai.history[-1] != first_question):
                ai.add_to_own_will("do_most_important")
                ai.add_to_own_will("is_day_planned")
                ai.force_own_will_story()

    async def user_connect_handler(self, event):
        db = PArtOfLiving.modules['db']
        today = datetime.now().strftime('%Y-%m-%d')
        if db['last_login_date'] == today:
            PArtOfLiving.modules['messages'].say('Welcome back')
        else:
            PArtOfLiving.modules['messages'].say('Greatings. I wish you a good day! Do your best and let the Force be with you!')
            db['last_login_date'] = today

    async def activate(self, modules):
        log.debug("Activating plugin for doing most important task..")
        PArtOfLiving.modules = modules
        ai = modules['ai']
        modules['events'].add_listener('user_connected',
                                       self.user_connect_handler)
        # TODO: дві історії, одна щодо планування дня
        ai.add_story_by_source("""
            story day_preparation {
                > Do you have 3 top priorities for today?
                <if in>
                    <intent>yes => {
                        > Great! Having day beams is an absolutely mandatory element of a high level day. What about goal list?
                        <if in> 
                            <intent>yes => {
                                > Have you plan allowing make ur day goals reality?
                                <if in>
                                    <intent>yes => {
                                    }
                                </if>
                            }
                            <intent>no => {
                                > It's all right, mostly. Achieve 3 top priorities of today, only then you may begin to worry about another goals. Do you have a plan allowing ur day goals to become reality? 
                                <if in>
                                    <intent>yes => {
                                        > What about realisation?
                                    }
                                    <intent>no => {
                                        > Goals without plan have big chances to stay only intentions. Plan is a way to guarantee goals implementation. Will you do it within a sane peace of time?
                                    }
                                </if>
                            }
                        </if>
                    }
                    <intent>no => {
                        > Why don't to do it right now?
                        <if in>
                            <intent>yes => {
                                > Cool!
                            }
                            busy => {
                                > Please, choose exact time. Then provide a way to guarantee execution of that. Maybe, set timer with reminder.
                            }
                            <intent>no_motivation => {
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
                                > It's important! What prevents u?
                                <if in>
                                    not thinking about consenquences => {
                                        > Please, think about consenquences. U will not live the best version of today if u do not set, write and plan most important goals for today!
                                    }
                                </if>
                            }
                        </if>
                    }
                </if>
            }
            story do_most_important {
                > Do you have optimal goals and plan for today?
                <if in>
                    <intent>yes => {
                        > Great! It's an absolutely mandatory element of high level day.
                    }
                    <intent>no => {
                        > Do it!
                    }
                </if>
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
                            no motivation => {
                                > Think about consequences. Accept responsibility for them and for the current day. For your life! Is it the best dicision to lose them? To live worse version of your life?
                                <if in>
                                    <intent>no => {
                                        > Then force yourself to do what is right.
                                    }
                                    <intent>yes => {
                                        > Its your choice. You cant run from consequences.
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
        ai.add_to_own_will("day_preparation")
        # ai.add_to_own_will("is_day_planned")
        # ai.add_to_own_will()
        # FIXME: new event - userconnected
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.do_regular_work, 'interval', minutes=8,
                          id="do_most_important_id")
        scheduler.start()
