#!/usr/bin/env python3

from aicore_ng import *


def test_create_from1():
    source = """
    story testname {
        <intent>greetings
        Hey!
    }
    """
    st = RSParser.create_from_text(source)
    assert st != None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.name == "testname", "st.name must be testname"
    assert st.contains("<intent>greetings"), "st.contains must work"
    log = ["<intent>greetings"]
    assert AICore.next_in_story(log, st), "AICore.next_in_story error"

