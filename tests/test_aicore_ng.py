#!/usr/bin/env python3

from ..aicore_ng import RSParser, RSVisitor, Story, MessageInNode, IfNode  # noqa: F403, F401
from ..aicore_ng import MessageOutNode, AICore  # noqa: F403


def test_create_from1():
    source = """
        story testname { 
            < <intent>greetings
            > Hey!
            < <intent>fuck
            > fuck you!

        }
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
    source = r"""
    story testname {
        < <intent>greetings
        > Hey! Whats up?
        <if input>
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
    assert next.text == "> Hey! Whats up?", "AICore.next_in_story error"
    log.append(next.text)
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, IfNode), "next must be IfNode"
    # TODO: check variants
    # assert next.text == "> Hey! Whats up?", "AICore.next_in_story error"
    log.append('< all right')
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> Cool!", "AICore.next_in_story error"


def test_create_from3():
    source = r"""
    story test2 {
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
        </if>
    }
    """
    
    res = RSParser.create_from_text(source)
    assert st is not None, "StoryFactory.create_from_text error"
    assert isinstance(st, Story), "st must be Story"
    assert st.name == "testname", "st.name must be testname"
    assert st.contains("<intent>greetings"), "st.contains must work"
    log = ["<intent>greetings"]
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "Hey!", "AICore.next_in_story error"
