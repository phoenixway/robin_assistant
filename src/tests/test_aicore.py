#!/usr/bin/env python3
from asyncio import sleep
from parsimonious.grammar import Grammar
import pytest
# import pytest_asyncio.plugin

from ..ai_core2.rs_parser import RSParser   # noqa: F403, F401
from ..ai_core2.ast_nodes import MessageOutNode  # noqa: E501
from ..ai_core2.ast_nodes import FnNode
from ..ai_core2.story import Story
from ..robin_db import RobinDb
from ..robin_events import Robin_events
from ..ai_core2.ai_core import AICore
from ..messages import Messages


def check_next(log, st, goal, result_class=MessageOutNode):
    ac = AICore(None)
    next = ac.next_in_story(log, st)
    assert next is not None, f"next is None, must be Node:{goal}"
    assert isinstance(next, result_class), f"next must be {result_class.name}"
    assert next.text == goal, f"AICore.next_in_story: must be {goal}"


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
    log.append("> Hey! Whats up?")
    log.append('< all right')
    check_next(log, st, "> Cool!")
    log.append("> Cool!")
    log.append(r"< what cool?")
    check_next(log, st, "> everything")
    log.append("> everything")
    log.append("< fuck")
    check_next(log, st, "> dont curse")


def test_if_statement():
    source = """
        story {
            < <intent>greetings
            <if True>
                    > Good to see u again, boss.
                    < Really?
                    > Nope.
            <else>
                > Oh no..
                < What?
                > Forget.
            </if>
            < fuck you
            > u welcome

        }
    """
    st = RSParser.create_from_text(source)
    st = st[0]
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.contains("< <intent>greetings"), "st.contains must work"
    lst = ["< <intent>greetings"]
    check_next(lst, st, "> Good to see u again, boss.")
    lst.append("> Good to see u again, boss.")
    lst.append("< Really?")
    check_next(lst, st, "> Nope.")
    lst.append("> Nope.")
    lst.append("< fuck you")
    check_next(lst, st, "> u welcome")


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
            <fn>
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
    ac = AICore(None)
    ac.stories.append(st)
    next = ac.next_in_story(lst, st)
    assert next is not None, f"next is None, must be Node:{FnNode}"
    assert isinstance(next, FnNode), f"next must be {FnNode.name}"
    answer = ac.respond("func")
    assert answer == "Hello, world!", "answer is not hello word"


def test_func1():
    raw_story = r"""
        story testname1 {
            < func
            <fn>
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
    ac = AICore(None)
    ac.stories.append(st)
    next = ac.next_in_story(lst, st)
    assert next is not None, f"next is None, must be Node:{FnNode}"
    assert isinstance(next, FnNode), f"next must be {FnNode.name}"
    answer = ac.respond("func")
    assert answer == "if works!", "answer is not hello word"


@pytest.mark.asyncio
async def test_own_will():
    modules = {}
    modules['db'] = RobinDb('memory')
    db = modules['db']
    events = Robin_events()
    modules['events'] = events
    ai = AICore(modules)
    db['var2change'] = "initional state"
    messages = Messages(modules)
    modules['messages'] = messages
    messages.websockets.append([])

    raw_story = r"""
        story test_own_will {
            <fn>
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
