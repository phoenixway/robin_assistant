#!/usr/bin/env python3

import re
from parsimonious.grammar import Grammar
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


def is_one_liner(line):
    r = re.compile(r'([\<\>])+ (\w+)')
    res = r.search(line)
    return res


def parse_if(lines, pos):
    find_end = False
    res = ""
    while pos < len(lines) and not find_end:
        if lines[pos].strip() == "<if/>":
            find_end = True
        res = res + str(lines[pos])
        pos = pos + 1
    if find_end:
        return res, pos
    else:
        raise RuntimeError


def parse(lines):
    i = 0
    result = []
    while i < len(lines):
        if is_one_liner(lines[i]):
            result.append(lines[i])
        else:
            if lines[i].strip() == "<if input>":
                if_st, i = parse_if(lines, i)
                result.append(if_st)
        i = i + 1
    return result


def test_create_from2():
    source = """
    story testname
        < <intent>greetings
        > Hey! Whats up?
        <if input>
            < all right => {
                > Cool!1
            }
            < nothing => {
                > Oh...
            }
        <if/>
    story_ends
    """
    source1 = """
        < <intent>greetings
        > Hey! Whats up?
        <if input>
            all right => {
                > Cool!1
            }
            nothing => {
                > Oh...
            }
        </if>
    """
    # expr = (statement / emptyline)*
    #     statement = (oneliner / if_statement )
    #     if_statement = if_start
    #     if_start = ~r'<if input>'
    #     if_end = ~r'\</if\>'
    #     if_variant = text ws* then_keyword ws* block
    #     text = ~r"[-\w]+"
    #     then_keyword = ~r"\=\>"
    #     block = lbr ws* text* ws* rbr
    #     ws = ~"\s*"
    #     rbr = ~r"\}"
    #     lbr = ~r"\{"
    #     oneliner = ws* inout ws+ text
    #     inout = ~r'[\<\>]+'
    #     ws = ~"\s*"
    #     emptyline = ws+
    grammar = Grammar(r"""
        expr = (statement / emptyline)*
        statement = (oneliner / if_statement )
        if_statement = ws1* if_start if_variant* if_end
        if_start = ~r'<if input>'
        if_end = ~r'\</if\>'
        if_variant = text ws* then_keyword ws* block
        text = ~r"[-\w]+"
        then_keyword = ~r"\=\>"
        block = lbr ws* text* ws* rbr
        ws = ~"\s*"
        rbr = ~r"\}"
        lbr = ~r"\{"
        oneliner = ws* inout
        inout = ~r'[/>/<]{1} (/w/s)+'
        ws = ~"\s*"
        ws1 = ~"\s"
        emptyline = ws+
    """)
    res = grammar.parse("""<if input>""")
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

