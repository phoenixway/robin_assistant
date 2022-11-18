#!/usr/bin/env python3

from ..aicore_ng import RSParser, Story, MessageInNode  # noqa: F403, F401
from ..aicore_ng import MessageOutNode, AICore  # noqa: F403


def test_create_from1():
    source = """
    story testname
        < <intent>greetings
        > Hey!
    story_ends
    """
    st = RSParser.create_from_text(source)
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.name == "testname", "st.name must be testname"
    assert st.contains("< <intent>greetings"), "st.contains must work"
    log = ["< <intent>greetings"]
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> Hey!", "AICore.next_in_story error"


def test_create_from2():
    source = """
    story testname
        < <intent>greetings
        > Hey! Whats up?
        fork <
            all right => {
                > Cool!1
            }
            nothing => {
                > Oh...
            }
        fi
    story_ends
    """
    st = RSParser.create_from_text(source)
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.name == "testname", "st.name must be testname"
    assert st.contains("<intent>greetings"), "st.contains must work"
    log = ["<intent>greetings"]
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "Hey!", "AICore.next_in_story error"

