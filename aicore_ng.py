#!/usr/bin/env python3

import string
import random 
import re
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


class AstNode:
    def __init__(self):
        self.parent = None
        self.next = None
    
    def __str__(self):
        return f'{self.__class__.__name__}'

    def __repr__(self):
        return f'{self.__class__.__name__}'

    def equals(self, other):
        return str(self) == str(other)


class StringNode(AstNode):
    def __init__(self, text):
        self.text = text
        super().__init__()
    
    def __str__(self):
        return f'{self.text}'

    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.text}"'


class MessageInNode(StringNode):
    def __init__(self, text):
        super().__init__(text)

    def validate(message):
        return message[0:2] == "< "


class MessageOutNode(StringNode):
    def __init__(self, message):
        super().__init__(message)

    def validate(message):
        return message[0:2] == "> "


class NodeFactory:
    def createNode(text):
        if MessageInNode.validate(text):
            return MessageInNode(text)
        elif MessageOutNode.validate(text):
            return MessageOutNode(text)
        else:
            return StringNode(text)


class RSVisitor(NodeVisitor):
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
                output.append(child.strip())
        return output

    def visit_if_statement(self, node, visited_children):
        for child in visited_children:
            #if child.expr_type == "if_variant":
            pass
        pass
        return "if_statement"

    def visit_if_variant(self, node, visited_children):
        pass
        return "if_variant"

    def visit_parameter(self, node, visited_children):
        if visited_children[0].expr_name=="raw_text":
            return {"parameter": visited_children[0]["raw_text"]}
        return "parameter"

    def visit_ws(self, node, visited_children):
        return "ws"

    def visit_maybe_ws(self, node, visited_children):
        return ""

    def visit_ws_must(self, node, visited_children):
        return "ws*"
    
    def visit_inout(self, node, visited_children):
        return node.text

    def visit_intent(self, node, visited_children):
        return "intent"

    def visit_intent_keyword(self, node, visited_children):
        return "intent"

    def visit_intent_text(self, node, visited_children):
        return "intent"

    def visit_simple_text(self, node, visited_children):
        return "intent"


    def visit_maybe_intent(self, node, visited_children):
        pass
        return "<intent>"

    def visit_simple_parameter(self, node, visited_children):
        pass
        return "simple_parameter"
    
    def visit_intent_parameter(self, node, visited_children):
        pass
        return "intent_parameter"

    def visit_maybe_statements(self, node, visited_children):
        return "maybe_statements"

    def visit_maybe_intent_keyword(self, node, visited_children):
        return "intent"


    def visit_if_variant_must(self, node, visited_children):
        return "if_variant_must"

    def visit_raw_text(self, node, visited_children):
        return {"raw_text": node.text}

    def visit_text(self, node, visited_children):
        return node.text

    def visit_block(self, node, visited_children):
        return "block"

    def visit_newline(self, node, visited_children):
        return "newline"

    def visit_if_start(self, node, visited_children):
        return "if_start"

    def visit_if_end(self, node, visited_children):
        """ Returns the overall output. """
        return "if_end"

    def visit_then_keyword(self, node, visited_children):
        return "then_theme"

    def visit_lbr(self, node, visited_children):
        """ Returns the overall output. """
        return "lbr"

    def visit_rbr(self, node, visited_children):
        return "rbr"

    # def generic_visit(self, node, visited_children):
    #     return ""


class RSParser:
    rs_grammar = Grammar(r"""
        exprs = (expr)*
        expr = statement / newline
        statement = (if_statement / oneliner)
        if_statement = maybe_ws if_start maybe_ws if_variant_must maybe_ws if_end maybe_ws
        if_start = ~r'<if input>'
        if_end = ~r'</if>'
        if_variant = parameter maybe_ws then_keyword maybe_ws block
        then_keyword = ~r"=>"
        block = lbr maybe_ws maybe_statements maybe_ws rbr
        rbr = ~r"\}"
        lbr = ~r"\{"
        oneliner = maybe_ws inout ws_must text
        inout = ~r"[<>]"
        text = (intent_text / simple_text)
        intent_text = maybe_intent_keyword raw_text
        simple_text = raw_text
        parameter = (intent_parameter / simple_parameter)
        simple_parameter = raw_text
        intent_parameter = maybe_intent_keyword raw_text
        raw_text = ~r"[-\w\s\?\!\.]+"
        ws = ~r"\s"
        newline = ~r"\n\r(\s)*"
        intent_keyword = ~r"<intent>"
        maybe_ws = ws*
        ws_must = ws+
        maybe_intent_keyword = intent_keyword+
        maybe_statements = statement*
        if_variant_must = if_variant+
    """)

    def create_from_text(text):
        rg = re.compile(r"(story\s+(\w+)\s*((\n|.)*?)story_ends)", re.MULTILINE)  # noqa: E501
        m = rg.search(text)
        if m is None:
            return None
        else:
            story_name = m.group(2)
            story_body = m.group(3)
            body = story_body.splitlines()
            body = [item.strip() for item in body if len(item.strip()) > 0]
            i = 0
            first = None
            while i < len(body) - 1:
                if body[i + 1] is not None:
                    n = NodeFactory.createNode(body[i])
                    if i == 0:
                        first = n
                    n1 = NodeFactory.createNode(body[i + 1])
                    n.next = n1
                    n1.parent = n
                i = i + 1

            st = Story(name=story_name)
            st.first_node = first
            return st


class Story:
    def contains(self, item):
        node = self.first_node
        while node:
            if node.equals(item):
                return True
            elif node.next is not None:
                node = node.next
            else:
                break
        return False

    def __init__(self,
                 name=""):
        self._name = name
        self.first_node = None

    @property
    def name(self):
        if not self._name and not self.first_node:
            raise Exception("Not initialized story!")
        elif not self._name:
            letters = string.ascii_letters
            self._name = ''.join(random.choice(letters) for i in range(10)) 
        return self._name


class AICore:
    def next_in_story(log, story):
        if str(story.first_node) not in log:
            return None
        return story.first_node.next