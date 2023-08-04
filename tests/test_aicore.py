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
from robin_ai.ai_core2.ast_nodes import OutputNode  # noqa: E501
from robin_ai.ai_core2.ast_nodes import FnNode
from robin_ai.ai_core2.story import Story
from robin_ai.robin_db import RobinDb
from robin_ai.robin_events import Robin_events
from robin_ai.handle_config import init_config
from robin_ai.ai_core2.ai_core import AI
from robin_ai.messages import Messages
from robin_ai.ai_core2.input_templates import TemplatesHandler


def check_next(log, s, goal, result_class=OutputNode):
    ''' Check if goal is next element in story with a given log
    Parameters:
        s : str Story script
    '''
    config = init_config()
    MODULES = {'config': config}
    ac = AI(MODULES)
    next = ac.get_next(log, s)
    assert next is not None, f"next is None, must be Node:{goal}"
    assert isinstance(next, result_class), f"next must be {result_class.__name__}"
    res = ac.run_fn(next) if result_class.__name__ == "FnNode" else next.value
    assert TemplatesHandler.substitute(res, ac.runtime_vars) == goal, f"AICore.next_in_story: must be {goal}"


def test_next_in_story1():
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


def test_next_in_story2():
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
        </if>
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
        </if>
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
            <if li == "Really?">
                > Nope.
            <elif li == "Really?"> 
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
            <if li == "Really?">
                > Nope.
            <elif li == "Oh no.."> {
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
            <if True>
                > Nope.
            <elif "li" == "Really?"> 
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
    check_next(lst, st, "> Nope.")
    lst.extend(("> Nope.", "< Yaha"))
    check_next(lst, st, "> Yahaha")


def test_grammar():
    raw_gr = r"""
        if_variant_must = if_variant+
        if_variant = maybe_ws parameter maybe_ws then_keyword maybe_ws
        then_keyword = ~r"=>"
        oneliner = inout ws_must text
        inout = ~r"[<>]"
        text = (intent_text / simple_text)
        intent_text = maybe_intent_keyword raw_text
        simple_text = raw_text
        parameter = (intent_parameter / simple_parameter)
        simple_parameter = raw_text
        intent_parameter = maybe_intent_keyword
        raw_text = ~r"[-\w\s\?\!\.]+"
        ws = ~r"\s"
        intent_keyword = ~r"<intent>"
        maybe_ws = ws*
        ws_must = ws+
        maybe_intent_keyword = intent_keyword+
        maybe_statements = statement*
        statement = (oneliner)
        """

    raw_stories = r"""
        <intent> => """
    gr = Grammar(raw_gr)
    stories = gr.parse(raw_stories)
    assert stories is not None, "stories is None"


def test_rs_parser():
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
        </if>
        < fuck
    }"""
    try:
        stories = RSParser.create_from_text(raw_stories)
    except:
        assert False, "Exception raised"
    assert stories is not None, "stories is None"


def test_func():
    raw_story = r"""
        story testname {
            < func
            > <fn>
                s = "Hello, world!"
                print(s)
                ret = s
              </fn>
        }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains("< func"), "st.contains must work"
    lst = ["< func"]
    check_next(lst, st, "Hello, world!", FnNode)


def test_func1():
    raw_story = r"""
        story testname1 {
            < func
            > <fn>
                if True:
                    ret = "if works!"
                else:
                    ret = "else works!"
              </fn>
        }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains("< func"), "st.contains must work"
    lst = ["< func"]
    check_next(lst, st, "if works!", FnNode)


@pytest.mark.asyncio
async def test_own_will():
    modules = {}
    modules['db'] = RobinDb('memory', modules)
    db = modules['db']
    events = Robin_events()
    modules['events'] = events
    ai = AI(modules)
    db['var2change'] = "initional state"
    messages = Messages(modules)
    modules['messages'] = messages
    messages.websockets.append([])

    raw_story = r"""
        story test_own_will {
            > <fn>
                db['var2change'] = "modified state"
              </fn>
        }
    """
    ai.add_story_by_source(raw_story)
    ai.set_silence_time(seconds=3)
    ai.add_to_own_will("test_own_will")
    ai.init_silence()
    await sleep(6)
    assert db['var2change'] == "modified state", "var2change must be changed"


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
        > <fn>
            ret = 'yes we can'
          </fn>
    }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains(
        r"< query goals %s"), "st.contains must work"
    lst = [r'< query goals "test query" ']
    check_next(lst, st, "yes we can", FnNode)
    lst = [r"< query goals one_word"]
    check_next(lst, st, "yes we can", FnNode)


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

'''
def test_parametrized_input3():
    raw_story = r"""
    story{
        < I went there <date: yesterday|recently>, bought <goods1: %s> and <goods2: %s>
        > ur data are: $date $goods1 $goods2
    }
    """
    st = RSParser.create_from_text(raw_story)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains(
        r"< report <let when>yesterday|%d|(%i days ago)</let>"), "st.contains must work"
    lst = [r"< report <let when>yesterday|%d|(%i days ago)</let>"]
    check_next(lst, st, "> it's parametrized input!")'''