#!/usr/bin/env python3
import pytest
import logging
import os
import sys

from asyncio import sleep
from parsimonious.grammar import Grammar
# import pytest_asyncio.plugin

sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../robin_ai'))
logging.basicConfig(level=logging.DEBUG)
logging.debug(os.getcwd())

from robin_ai.ai_core2.rs_parser import RSParser   # noqa: F403, F401
from robin_ai.ai_core2.ast_nodes import InputNode, OutputNode  # noqa: E501
from robin_ai.ai_core2.fn_node import FnNode
from robin_ai.ai_core2.story import Story
from robin_ai.robin_db import RobinDb
from robin_ai.robin_events import Robin_events
from robin_ai.handle_config import init_config
from robin_ai.actions_queue import ActionsQueue
from robin_ai.ai_core2.ai_core import AI
from robin_ai.messages import Messages
from robin_ai.ai_core2.input_templates import TemplatesHandler

def get_aicore() -> AI:
    config = init_config()
    MODULES = {'config': config}
    ac = AI(MODULES)
    aq = ActionsQueue()
    MODULES['actions_queue'] = aq
    aq.respond_to_user_message_callback = ac.respond
    return ac

def check_next(log, s, goal, result_class=OutputNode):
    ''' Check if goal is next element in story with a given log
    Parameters:
        s : str Story script
    '''
    ac = get_aicore()
    ac.history = log
    nxt = ac.next_in_story(s)
    assert nxt is not None, f"next is None, must be Node:{goal}"
    assert isinstance(nxt, result_class), f"next must be {result_class.__name__}"
    res = ac.execute_fn(nxt) if result_class.__name__ == "FnNode" else nxt.value
    assert TemplatesHandler.substitute(res, ac.runtime_vars) == goal, f"AICore.next_in_story: must be {goal}"


def test_1liners():
    source = r"""
        story testname {
            < <intent>greetings
            > Hey!
            < <intent>fuck
            > fuck you!

        }
    """
    st = RSParser.create_from_text(source)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.name == "testname", "st.name must be testname"
    assert st.contains("< <intent>greetings"), "st.contains must work"
    log = ["< <intent>greetings"]
    check_next(log, st, "> Hey!")


def test_1liners2():
    source = r"""
    story testname {
        < <intent>greetings
        > Hey! Whats up?
        <if in>
            all right => {
                > Cool!
                < what cool?
                > everything
            }
            nothing => {
                > Oh...
            }
        </if in>
        < fuck
    }
    story testname1 {
        < <intent>greetings
        > Hey! Whats up?
        <if in>
            all right => {
                > Cool!
                < what cool?
                > everything
            }
            nothing => {
                > Oh...
            }
        </if in>
        < fuck
        > dont curse
    }

    """
    sts = RSParser.create_from_text(source)
    st = sts[1]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.name == "testname1", "st.name must be testname"
    assert st.contains("< <intent>greetings"), "st.contains must work"
    log = ["< <intent>greetings"]
    check_next(log, st, "> Hey! Whats up?")
    log.extend(("> Hey! Whats up?", '< all right'))
    check_next(log, st, "> Cool!")
    log.extend(("> Cool!", r"< what cool?"))
    check_next(log, st, "> everything")
    log.extend(("> everything", "< fuck"))
    check_next(log, st, "> dont curse")

    

def test_inline_fn():
    source = r"""
    story testname {
        < input1
        > <f code1 = 'random python inline code'] output1 <f code2 = 'that will be executed before and after Robin response'>
        < input 2
        > output 2
    }
    """
    sts = RSParser.create_from_text(source)
    st = sts[1]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.name == "testname", "st.name must be testname"
    assert st.contains("< input1"), "st.contains must work"
    log = ["< input1"]
    check_next(log, st, "> output1")
    log.extend(("> output1", '< input2'))
    check_next(log, st, "> output 2")


def test_grammar_if():
    source = """
        story test1{
            < <intent>greetings
            > Good to see u again, boss.
            < *
            <if>li == "Really?"</if>
                > Nope.
                <elif>li == "Really?"</elif>
                {
                    > What?
                    < Whatever
                    > As u command.
                }
            <else>
                <fn>
                    x = 1 + 1
                    ret = "No comments."
                </fn>
            < Yaha
            > Yahaha
        }
    """
    res = RSParser.rs_grammar.parse(source)
    assert res is not None, "bad parsing"


def test_if_statement():
    source2 = """
        story test1{
            < <intent>greetings
            > Good to see u again, boss.
            < *
            <if>li == "Really?"</if>
                > Nope.
            <elif> li == "Oh no.."</elif> {
                > What?
                < Whatever
                > As u command.
                }
            <else> <fn>
                    x = 1 + 1
                    ret = "No comments."
                </fn>
            < Yaha
            > Yahaha
        }
    """
    source = """
        story test1{
            < <intent>greetings
            > Good to see u again, boss.
            < *
            <if>True</if>
                > Nope.
                <elif>"li" == "Really?"</elif> {
                    > What?
                    < Whatever
                    > As u command.
                }
            <else>
                > Npoe
            < Yaha
            > Yahaha
        }
    """
    # TODO: змінні в метод який перевіряє умови
    # TODO: як вивід fn в лозі спілкування відображати так щоб наступний потрібний оператор детектився? аналогічно рішення if оператора  на момент знаходження наступної відповіді в діалозі
    # можна кожен прохід по такого типу узлам story фіксувати в лозі 
    # вузли story мають дві функції. дати наступний вузул відносно поточного. друга - ідентифікувати частини кожної конкретної story які мали місце в актуальному лозі спілкування
    """
        тобто щоб визначити наступний вузол потрбно зафіксувати достатньо достовірно в лозі спілкування усі попередні. це важливий момент
        інший важливий момент - достовірно розпізнати за записом в лозі елементи діалогу
        має бути map_in_log(node) == node.id
        чи node.trace_in_log == node.trace_to_be_pasted_in_log
        обидва параметри відносно складно продумати для if оператора. 
        це знову повертає до проблеми=необхідності мати можливість працювати з кількома діями (вивід, функії, зокрема if) Робіна підряд.
        зате отримана гнучкість буде вражаючою        
        має бути можливим перевірити точно map_in_log(node) == node.trace_to_be_pasted_in_log
        великого об'єму код можна замінити хеш-кодами
    """
    st = RSParser.create_from_text(source)
    assert st is not None, "StoryFactory.create_from_text error, st is None"
    assert len(st) > 0, "StoryFactory.create_from_text error. len == 0"
    st = st[0]
    assert isinstance(st, Story), "st must be Story"
    assert st.contains("< <intent>greetings"), "st.contains must work"
    lst = ["< <intent>greetings"]
    check_next(lst, st, "> Good to see u again, boss.")
    lst.extend(("> Good to see u again, boss.", "< Really?"))
    check_next(lst, st, "> Nope.")
    lst.extend(("> Nope.", "< Yaha"))
    check_next(lst, st, "> Yahaha")

def test_if_else_statement():
    source = """
        story test1{
            < <intent>greetings
            > Good to see u again, boss.
            < *
            <if>False</if>
                > Nope.
                <elif>"li" == "Really?"</elif>
                {
                > What?
                < Whatever
                > As u command.
                }
            <else>
                > Npoe
            < Yaha
            > Yahaha
        }
    """
    # TODO: змінні в метод який перевіряє умови
    # TODO: як вивід fn в лозі спілкування відображати так щоб наступний потрібний оператор детектився? аналогічно рішення if оператора  на момент знаходження наступної відповіді в діалозі
    # можна кожен прохід по такого типу узлам story фіксувати в лозі 
    # вузли story мають дві функції. дати наступний вузул відносно поточного. друга - ідентифікувати частини кожної конкретної story які мали місце в актуальному лозі спілкування
    """
        тобто щоб визначити наступний вузол потрбно зафіксувати достатньо достовірно в лозі спілкування усі попередні. це важливий момент
        інший важливий момент - достовірно розпізнати за записом в лозі елементи діалогу
        має бути map_in_log(node) == node.id
        чи node.trace_in_log == node.trace_to_be_pasted_in_log
        обидва параметри відносно складно продумати для if оператора. 
        це знову повертає до проблеми=необхідності мати можливість працювати з кількома діями (вивід, функії, зокрема if) Робіна підряд.
        зате отримана гнучкість буде вражаючою        
        має бути можливим перевірити точно map_in_log(node) == node.trace_to_be_pasted_in_log
        великого об'єму код можна замінити хеш-кодами
    """
    st = RSParser.create_from_text(source)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains("< <intent>greetings"), "st.contains must work"
    lst = ["< <intent>greetings"]
    check_next(lst, st, "> Good to see u again, boss.")
    lst.extend(("> Good to see u again, boss.", "< Really?"))
    check_next(lst, st, "> Npoe")
    lst.extend(("> Npoe", "< Yaha"))
    check_next(lst, st, "> Yahaha")



def test_if_in():
    raw_stories = r"""
       story testname {
        < <intent>greetings
        > Hey! Whats up?
        <if in>
            all right => {
                > Cool!
                < what cool?
                > everything
            }
            <intent>greetings => {
                > Oh...
            }
        </if in>
        < fuck
    }"""
    try:
        stories = RSParser.create_from_text(raw_stories)
    except:
        assert False, "Exception raised"
    assert stories is not None, "stories is None"


def test_func():
    # TODO: change db record in fn and check if that was made
    # TODO: test if after user input next after fn execution output will be as given one
    raw_story = r"""
        story testname {
            < func
            <fn>
                s = "Hello, world!"
                print(s)
                ret = s
            </fn>
            < Great!
            > Do most important! Don't waste time!
        }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains("< func"), "st.contains must work"
    ac = get_aicore()
    lst = ["< func"]
    ac.history = lst
    fn_node = ac.next_in_story(st)
    assert fn_node is not None, "next is None, must be FnNode"
    assert isinstance(fn_node, FnNode), f"next must be {FnNode.__name__}"
    lst.extend([fn_node.map_to_history(), '< Great!'])
    check_next(lst, st, "> Do most important! Don't waste time!",OutputNode )

def test_func2():
    # TODO: change db record in fn and check if that was made
    # TODO: test if after user input next after fn execution output will be as given one
    raw_story = r"""
        story plan_control{
            <if>db['day_plan'] != API.today_str()</if> {
                > Do you have a plan allowing ur day goals to become reality? 
                <if in> 
                    <intent>no => {
                        > Goals without plan have big chances to stay only intentions. Plan is a way to guarantee goals implementation. Will you do it within a sane peace of time?
                    }
                </if in>
            }
        }
    """
    st = RSParser.create_from_text(raw_story)
    assert st is not None, "StoryFactory.create_from_text error, story is None"
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains("< func"), "st.contains must work"
    ac = get_aicore()
    lst = ["< func"]
    ac.history = lst
    fn_node = ac.next_in_story(st)
    assert fn_node is not None, "next is None, must be FnNode"
    assert isinstance(fn_node, FnNode), f"next must be {FnNode.__name__}"
    lst.extend([fn_node.map_to_history(), '< Great!'])
    check_next(lst, st, "> Do most important! Don't waste time!",OutputNode )

def test_func3():
    # TODO: change db record in fn and check if that was made
    # TODO: test if after user input next after fn execution output will be as given one
    raw_story = r"""
        story day_preparation {
            <if>db['day_priorities'] != API.today_str() </if> {
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
    st = RSParser.create_from_text(raw_story)
    assert st is not None, "StoryFactory.create_from_text error, story is None"
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains("< func"), "st.contains must work"
    ac = get_aicore()
    lst = ["< func"]
    ac.history = lst
    fn_node = ac.next_in_story(st)
    assert fn_node is not None, "next is None, must be FnNode"
    assert isinstance(fn_node, FnNode), f"next must be {FnNode.__name__}"
    lst.extend([fn_node.map_to_history(), '< Great!'])
    check_next(lst, st, "> Do most important! Don't waste time!",OutputNode )


# @pytest.mark.asyncio
# async def test_own_will():
#     modules = {}
#     modules['db'] = RobinDb('memory', modules)
#     db = modules['db']
#     events = Robin_events()
#     modules['events'] = events
#     ai = AI(modules)
#     db['var2change'] = "initional state"
#     messages = Messages(modules)
#     modules['messages'] = messages
#     messages.websockets.append([])

#     raw_story = r"""
#         story test_own_will {
#             > <fn>
#                 db['var2change'] = "modified state"
#               </fn>
#         }
#     """
#     ai.add_story_by_source(raw_story)
#     ai.set_silence_time(seconds=3)
#     ai.add_to_own_will("test_own_will")
#     ai.init_silence()
#     await sleep(6)
#     assert db['var2change'] == "modified state", "var2change must be changed"


def test_parametrized_input():
    raw_story = r"""
    story {
        < alarm in %d minutes
        > Alarming!
    }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains(
        r"< alarm in %d minutes"), "st.contains must work"
    lst = [r"< alarm in 5 minutes"]
    check_next(lst, st, "> Alarming!")


def test_parametrized_input1():
    raw_story = r"""
    story {
        < alarm in %d minutes
        > Alarming! $0 minutes passed!
    }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains(
        r"< alarm in %d minutes"), "st.contains must work"
    lst = [r"< alarm in 5 minutes"]
    check_next(lst, st, "> Alarming! 5 minutes passed!")


def test_parametrized_input2():
    raw_story = r"""
    story {
        < query goals %s 
        > yes we can
    }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains(
        r"< query goals %s"), "st.contains must work"
    lst = [r'< query goals "test query" ']
    check_next(lst, st, "> yes we can")


def test_parametrized_input3():
    raw_story = r"""
    story {
        < *
        > superbla
    }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains(
        r"< *"), "st.contains must work"
    lst = [r'< random input text']
    check_next(lst, st, "> superbla")


def test_variable_output():
    raw_story = r"""
    # story{
    #     < I went there <date: yesterday|recently>, bought <goods1: %s> and <goods2: %s>
    #     > ur data are: $date $goods1 $goods2
    # }
    # 
    raw_story{
        < I went there
        > This text<or>That text with random variation1|variation2|"variation3 with spaces"<or>the ultracool third text
    }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains(
        r"< report <let when>yesterday|%d|(%i days ago)</let>"), "st.contains must work"
    lst = [r"< report <let when>yesterday|%d|(%i days ago)</let>"]
    check_next(lst, st, "> it's parametrized input!")
