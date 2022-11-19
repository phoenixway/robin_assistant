#!/usr/bin/env python3

import re
from ..aicore_ng import RSParser, RSVisitor, Story, MessageInNode  # noqa: F403, F401
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
    source1 = r"""
    < <intent>greetings
    > Hey! Whats up?
    <if input>
        all right => {
            > Cool!
        }
        nothing => {
            > Oh...
        }
    </if>
    < fuck
    """
    source = r"""
    < <intent>greetings
    > Hey! Whats up?
    <if input>
        all right => {
            > great! 
            <if input>
                ok => {
                    > oki-oki
                }
                nothing => {
                    > nothing...
                }
            </if>
            < shit
            
            > fuck
        }
        nothing=>{
            < test
        }
    </if>"""
    
    res = RSParser.rs_grammar.parse(source)
    res = RSParser.rs_grammar.parse(r"""< test test""")
    res = RSParser.rs_grammar.parse(source1)
    iv = RSVisitor()
    output = iv.visit(res)
    
    #res = parse(source1.splitlines())
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
