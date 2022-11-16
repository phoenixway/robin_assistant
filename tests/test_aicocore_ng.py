#!/usr/bin/env python3

from aicore_ng import *
import copy
from pprint import pprint

def test_create_from1():
    source = """
    story testname {
        <intent>greetings
        Hey!
    }
    """
    st = StoryFactory.create_from_text(source)
    assert st != None, "StoryFactory.create_from_text error"
    assert instanceof(st, Story), "st must be Story"
    assert st.name == "testname", "st.name must be testname"
    assert st.contains("<intent>greetings"), "st.contains must work"
    log = ["<intent>greetings"]
    assert AICore.log_contains(log, "<intent>greetings"), "AICore.is_log_contains error"

