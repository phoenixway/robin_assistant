#!/usr/bin/env python3
from parsimonious.grammar import Grammar

from ..ai_core2.rs_parser import RSParser   # noqa: F403, F401
from ..ai_core2.ast_nodes import IfInNode, MessageOutNode, MessageInNode  # noqa: E501
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
    st = st[0]
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
    assert isinstance(next, IfInNode), "next must be IfNode"
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
    assert st.name == "testname", "st.name must be testname"
    assert st.contains("< <intent>greetings"), "st.contains must work"
    log = ["< <intent>greetings"]
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> Hey!", "AICore.next_in_story error"


def test_next_in_story():
    aicore = AICore(None)
    st = aicore.stories[1]
    log = ["< <intent>cursing", "> fuck", "< <intent>cursing", "Dont curse", "< <intent>cursing"]  # noqa: E501
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> fuck", "AICore.next_in_story error"


def test_next_in_story2():
    aicore = AICore(None)
    st = aicore.stories[1]
    log = ["> Are u doing the currently most important task now?", "<intent>no"]  # noqa: E501
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> Why dont u do that right now?", "AICore.next_in_story error"
    log = ["> Are u doing the currently most important task now?", "<intent>no", "> Why dont u do that right now?", "< <intent>yes"]  # noqa: E501
    next = AICore.next_in_story(log, st)
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> Do ur best!", "AICore.next_in_story error"


def test_next_in_story1():
    aicore = AICore(None)
    aicore.log = ["< <intent>greetings", "> Hey! Whats up?", "<intent>no"]  # noqa: E501
    next = AICore.next_in_story(aicore.log, aicore.stories[0])
    assert next is not None, "next is None"
    assert isinstance(next, MessageOutNode), "next must be MessageOutNode"
    assert next.text == "> Oh...", "AICore.next_in_story error"


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
    # raw_stories = r"""
    #     <if input>
    #         all right => {
    #             > Cool!
    #             < what cool?
    #             > everything
    #         }
    #         <intent>greetings => {
    #             > Oh...
    #         }
    #     </if>
    # }"""
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
        <if input>
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
