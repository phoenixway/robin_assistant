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
        # lst = [i for i in ai.stories
        #        if i.name == "day_preparation"]
        # if lst:
        #     first_question = lst[0].first_node.value
        #     if len(ai.history) == 0 or (len(ai.history) > 0 and ai.history[-1] != first_question):
        ai.add_to_own_will("day_preparation")
                # ai.force_own_will_story()

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
        # TODO: чи план з таймінгом, дедлайнами. якщо реалізація не ок відповідь
        s = """
    story plan_control {
        <if db['day_plan'] != API.today_str() > {
            > Do you have a plan allowing ur day goals to become reality? 
            <if in> 
                <intent>yes => {
                    <fn>
                        db['day_plan'] = API.today_str()
                    </fn>
                    > Great! What about realisation?
                }
                <intent>no => {
                   > Goals without plan have big chances to stay only intentions. Plan is a way to guarantee goals implementation. Will you do it within a sane peace of time?
            }
            </if>
        }
        <else>
            > Great that u planned a day!
    }
    story day_preparation {
        <if db['day_priorities'] != API.today_str() > {
            > Do u have today priorities? 
            <if in> 
                <intent>yes => {
                    <fn>
                        db['day_priorities'] = API.today_str()
                    </fn>
                    > Great! Having day beams is an absolutely mandatory element of a high level day. What about goal list?
                    <if in>
                        <intent>yes => {
                            > Wonderful!
                            <fn>
                                ai.force_story("plan_control")
                            </fn>
                        }
                        <intent>no => {
                            <fn>
                                ai.force_say("It's all right, mostly. Achieve 3 top priorities of today, only then you may begin to worry about another goals.")
                                ai.force_story("plan_control")
                            </fn>
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
                        </if>
                }
            </if>
        }
        <else>
            <fn>
                ai.force_story('plan_control')
            </fn>
    }
        """
        ai.add_story_by_source(s)
        ai.add_to_own_will("day_preparation")
        # ai.add_to_own_will("is_day_planned")
        # ai.add_to_own_will()
        # FIXME: new event - userconnected
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.do_regular_work, 'interval', minutes=8,
                          id="do_most_important_id")
        scheduler.start()
