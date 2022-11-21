#!/usr/bin/env python3

from ..ai_core2.rs_parser import RSParser   # noqa: F403, F401
from ..ai_core2.ast_nodes import IfNode, MessageOutNode, MessageInNode  # noqa: E501
from ..ai_core2.story import Story
from ..ai_core2.aicore_ng import AICore


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
    story testname1 {
        < <intent>greetings1
        > Hey! Whats up?
        <if input>
            all right => {
                > Cool!
                < what cool?
                > everything1
            }
            nothing => {
                > Oh...
            }
        </if>
        < fuck1
    }

    """
    sts = RSParser.create_from_text(source)
    st = sts[0]
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
    log.append(next.text)
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageInNode), "next must be MessageInNode"
    assert next.text == "< what cool?", "AICore.next_in_story error"
    log.append(next.text)
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> everything", "AICore.next_in_story error"
    log.append(next.text)
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageInNode), "next must be MessageInNode"
    assert next.text == "< fuck", "AICore.next_in_story error"


def test_aicore1():
    aicore = AICore(None)
    st = aicore.stories[1]
    log = ["< <intent>cursing", "> fuck", "< <intent>cursing", "Dont curse", "< <intent>cursing"]  # noqa: E501
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> fuck", "AICore.next_in_story error"


# def test_create_from3():
#     source = r"""
#     story test2 {
#         < <intent>greetings
#         > Hey! Whats up?
#         <if input>
#             all right => {
#                 > great!
#                 <if input>
#                     ok => {
#                         > oki-oki
#                     }
#                     nothing => {
#                         > nothing...
#                     }
#                 </if>
#                 < shit
#                 > fuck
#             }
#             nothing=>{
#                 < test
#             }
#         </if>
#     }
#     """
