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
    grammar_block=Grammar(r"""
        expr = (statement / block / newline)*
        statement = (if_statement / oneliner)
        if_statement = ws1* if_start ws1* if_variant* ws1* if_end ws1*
        if_start = ~r'<if input>'
        if_end = ~r'</if>'
        if_variant = text ws1* then_keyword ws1* block
        then_keyword = ~r"=>"
        block = lbr ws1* statement* ws1* rbr
        rbr = ~r"\}"
        lbr = ~r"\{"
        oneliner = ws1* inout ws1+ text
        inout = ~r"[<>]"
        text = intent* raw_text
        raw_text = ~r"[-\w\s\?\!\.]+"
        ws1 = ~r"\s"
        newline = ~r"\n\r(\s)*"
        intent = ~r"<intent>"
    """)
    res = grammar_block.parse(source)
    res = grammar_block.parse(r"""{
        > test test
    }""")
    res = grammar_block.parse(r"""< test test""")
    res = grammar_block.parse(source1)
    
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

