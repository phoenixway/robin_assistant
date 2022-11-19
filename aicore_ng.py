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
    def visit_story(self, node, visited_children):
        story_name = ""
        for child in visited_children:
            if isinstance(child, dict):
                story_name = child['story_name']

        s = Story(story_name)
        return s

    def visit_story_start_keyword(self, node, visited_children):
        return "not_important"

    def visit_story_ends_keyword(self, node, visited_children):
        return "not_important"

    def visit_story_name(self, node, visited_children):
        return {'story_name': node.text}

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
            if child == "not_important":
                continue
            if len(child) > 0:
                output.append(child.strip())
        return output

    def visit_if_statement(self, node, visited_children):
        for child in visited_children:
            if hasattr(child, "expr_name") == "if_variant":
                pass
        pass
        return "if_statement"

    def visit_if_variant(self, node, visited_children):
        param = ""
        block = []
        for child in visited_children:
            if isinstance(child, list):
                block = child
            elif child != "not_important":
                param = child.strip()
        return {param: block}

    def visit_parameter(self, node, visited_children):
        pass
        return visited_children[0]

    def visit_block(self, node, visited_children):
        block = []
        for child in visited_children:
            if child != "not_important":
                block.append(child)
        return block

    def visit_ws(self, node, visited_children):
        return "not_important"

    def visit_maybe_ws(self, node, visited_children):
        return "not_important"

    def visit_ws_must(self, node, visited_children):
        return "not_important"
    
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
        pass
        return visited_children

    def visit_maybe_intent_keyword(self, node, visited_children):
        return "intent"


    def visit_if_variant_must(self, node, visited_children):
        return "if_variant_must"

    def visit_raw_text(self, node, visited_children):
        return node.text

    def visit_text(self, node, visited_children):
        return node.text

    def visit_newline(self, node, visited_children):
        return "newline"

    def visit_if_start(self, node, visited_children):
        return "if_start"

    def visit_if_end(self, node, visited_children):
        return "if_end"

    def visit_then_keyword(self, node, visited_children):
        return "not_important"

    def visit_lbr(self, node, visited_children):
        return "not_important"

    def visit_rbr(self, node, visited_children):
        return "not_important"

    # def generic_visit(self, node, visited_children):
    #     return ""


class RSParser:
    rs_grammar = Grammar(r"""
        story = maybe_ws story_start_keyword maybe_ws story_name maybe_ws lbr maybe_ws exprs maybe_ws rbr maybe_ws 
        exprs = (expr)*
        story_start_keyword = ~r"story"
        story_ends_keyword = ~r"story_ends"
        story_name = ~r"\w+"
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
        res = RSParser.rs_grammar.parse(text)
        v = RSVisitor()
        ret = v.visit(res)
        return ret

    def create_from_text1(text):
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