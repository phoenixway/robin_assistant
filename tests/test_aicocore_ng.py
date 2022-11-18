#!/usr/bin/env python3

import re
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
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


class IniVisitor(NodeVisitor):
    def visit_exprs(self, node, visited_children):
        output = []
        for child in visited_children:
            if len(child) > 0:
                output.append(child)
        return output

    def visit_expr(self, node, visited_children):
        return visited_children[0]

    def visit_statement(self, node, visited_children):
        return visited_children[0]

    def visit_oneliner(self, node, visited_children):
        output = []
        for child in visited_children:
            if child == "ws*":
                continue
            if len(child) > 0:
                output.append(child)
        return output

    def visit_if_statement(self, node, visited_children):
        return "if_statement"

    def visit_ws(self, node, visited_children):
        return "ws"

    def visit_maybe_ws(self, node, visited_children):
        return "ws*"

    def visit_ws_must(self, node, visited_children):
        return "ws*"
    
    def visit_inout(self, node, visited_children):
        return node.text

    def visit_intent(self, node, visited_children):
        return "intent"

    def visit_maybe_intent(self, node, visited_children):
        return "intent*"

    def visit_maybe_statements(self, node, visited_children):
        return "maybe_statements"

    def visit_if_variant_must(self, node, visited_children):
        return "if_variant_must"

    def visit_raw_text(self, node, visited_children):
        return "raw_text"

    def visit_text(self, node, visited_children):
        return node.text

    def visit_block(self, node, visited_children):
        """ Returns the overall output. """
        return "statement"

    def visit_newline(self, node, visited_children):
        """ Returns the overall output. """
        return "statement"

    def visit_if_start(self, node, visited_children):
        """ Returns the overall output. """
        return "statement"

    def visit_if_end(self, node, visited_children):
        """ Returns the overall output. """
        return "statement"

    def visit_then_keyword(self, node, visited_children):
        """ Returns the overall output. """
        return "statement"

    def visit_lbr(self, node, visited_children):
        """ Returns the overall output. """
        return "statement"

    def visit_rbr(self, node, visited_children):
        """ Returns the overall output. """
        return "statement"

    def visit_if_variant(self, node, visited_children):
        """ Returns the overall output. """
        return "statement"

    # def generic_visit(self, node, visited_children):
    #     return ""


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
        exprs = (expr)*
        expr = statement / newline
        statement = (if_statement / oneliner)
        if_statement = maybe_ws if_start maybe_ws if_variant_must maybe_ws if_end maybe_ws
        if_start = ~r'<if input>'
        if_end = ~r'</if>'
        if_variant = text maybe_ws then_keyword maybe_ws block
        then_keyword = ~r"=>"
        block = lbr maybe_ws maybe_statements maybe_ws rbr
        rbr = ~r"\}"
        lbr = ~r"\{"
        oneliner = maybe_ws inout ws_must text
        inout = ~r"[<>]"
        text = maybe_intent raw_text
        raw_text = ~r"[-\w\s\?\!\.]+"
        ws = ~r"\s"
        newline = ~r"\n\r(\s)*"
        intent = ~r"<intent>"
        maybe_ws = ws*
        ws_must = ws+
        maybe_intent = intent*
        maybe_statements = statement*
        if_variant_must = if_variant+
    """)
    res = grammar_block.parse(source)
    res = grammar_block.parse(r"""< test test""")
    res = grammar_block.parse(source1)
    iv = IniVisitor()
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

