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
        ai.add_to_own_will("day_preparation")
        # ai.add_to_own_will("day_time_usage")

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
        s = """
    story day_time_usage {
        <fn>
            if len(ai.history):
                del ai.history[-1] 
            if db['day_plan'] == API.today_str():
                pass
            else:
                if API.is_time_between(time(6,0), time(13,0)):
                    if db['day_time_usage_morning '] != API.today_str():
                        ai.force_say("Day has began! Remember about responsibility for using it right before yourself. Do necessary preparation and fight today battle with all ur strenth!")
                        db['day_time_usage_morning '] = API.today_str()
                elif API.is_time_between(time(13,1), time(16,0)):
                    if db['day_time_usage_daytime '] != API.today_str():
                        db['day_time_usage_daytime '] = API.today_str()
                        ai.force_say("It seems like u wasting ur time, boss. Is it really ok for u to lose one more day of ur life? Think about ur pride of warrior. Pull urself together!")
                elif API.is_time_between(time(16,5), time(20,0)):
                    if db['day_time_usage_evening '] != API.today_str():
                        db['day_time_usage_evening '] = API.today_str()
                        ai.force_say("How would u rate the current day? Are u satisfyed with it?")
        </fn>
    }
    
    story realisation_control{
        > How ur realisation of the current day-plan? Are u doing most important task for now?
        <if in>
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
                            </if in>
                    }
                    not thinking about consenquences => {
                        > Please, think about consenquences. U will not live the best version of today if u do not set, write and plan most important goals for today!
                    }
                </if in>
            }
            <intent>yes => {
               > Carry on!
            }
        </if in>
    }
    story plan_control{
        <if>db['day_plan'] != API.today_str()</if> {
            > Do you have a plan allowing ur day goals to become reality? 
            <if in> 
                <intent>yes => {
                    <fn>
                        db['day_plan'] = API.today_str()
                    </fn>
                    > Great! 
                }
                <intent>no => {
                   > Goals without plan have big chances to stay only intentions. Plan is a way to guarantee goals implementation. Will you do it within a sane peace of time?
                   <if in>
                        <intent>yes => {
                            > Great, boss! Don't forget ur promise! Please, set time when u'll start and finish.
                        }
                        <intent>no => {
                            > What prevents u?
                        }
                   </if in>
            }
            </if in>
        }
        <else> {
            <fn>
                ai.force_story("realisation_control")
            </fn>
        }
    }
        """
        ai.add_story_by_source(s)
        s = """
            story day_preparation {
                <if>db['day_priorities'] != API.today_str() </if> {
                    > Do u have written today priorities?
                    <if in>
                        working on it => {
                            > Do ur best!
                        }
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
                                    > It's all right, mostly. Achieve 3 top priorities of today, only then you may begin to worry about another goals.
                                    <fn>
                                        ai.force_story("plan_control")
                                    </fn>
                                }
                            </if in>
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
                                    soon => {
                                        > When?
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
                                        </if in>
                                    }
                                </if in>
                        }
                    </if in>
                }
                <else>
                    <fn>
                        ai.force_story('plan_control')
                    </fn>
            }
        """
        ai.add_story_by_source(s)
        ai.add_to_own_will("day_preparation")
        # ai.add_to_own_will("day_time_usage")
        # FIXME: new event - userconnected
        scheduler = AsyncIOScheduler()
        scheduler.add_job(self.do_regular_work, 'interval', minutes=2"""  """,
                          id="do_most_important_id")
        scheduler.start()
