#!/usr/bin/env python3

import re
import logging
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
from parsimonious.exceptions import ParseError, VisitationError


class VarNode:
    def __init_(self, value):
        self.value = value


class NumberVarNode(VarNode):
    pass


class StringVarNode(VarNode):
    pass


class RandomVarNode(VarNode):
    pass


class InputVisitor(NodeVisitor):
    def visit_message(self, node, visited_children):
        children = [child for child in visited_children if child is not None]
        # for child in children:
        #     logging.debug(child)
        #     pass
        return children[0]

    def visit_statements_or_raw_text(self, node, visited_children):
        children = [child for child in visited_children if child is not None]
        return children

    def visit_statement_or_raw_text(self, node, visited_children):
        return visited_children[0]

    def visit_statement(self, node, visited_children):
        return visited_children[0]

    def visit_number_param(self, node, visited_children):
        return NumberVarNode()
    
    def visit_string_param(self, node, visited_children):
        return StringVarNode()
    
    def visit_random_random(self, node, visited_children):
        return RandomVarNode()

    def visit_raw_text(self, node, visited_children):
        return node.text.strip()

    def generic_visit(self, node, visited_children):
        return None


raw_input_grammar = """
    message = in_symbol ws_must statements_or_raw_text
    in_symbol = ~r"<"
    statements_or_raw_text = statement_or_raw_text*
    statement_or_raw_text = (statement / ws_must / raw_text)
    statement = (number_param / string_param / random_param)
    number_param = ~r"%d"
    string_param = ~r"%s"
    random_param = ~r"\*"
    raw_text = ~r"[-\w\s\?\!\.\,\d\'\`]+"
    ws = ~r"\s"
    ws_must = ws+
"""
input_grammar = Grammar(raw_input_grammar)
inputVisitor = InputVisitor()


class RuntimeVariables:
    def __init__(self):
        self.unnamed_vars = []
        self.named_vars = dict()


class TemplatesHandler():
    def validate_template(template):
        try:
            parsed = input_grammar.parse(template)
            ast = inputVisitor.visit(parsed)
        except (ParseError, VisitationError) as error:
            logging.debug(error)
            return False, None
        return True, ast

    def check(node, text, position):
        if isinstance(node, str):
            end_position = position + len(node)
            if node == text[position:end_position]:
                return True, node, position + len(node)
        if isinstance(node, NumberVarNode):
            regex = re.compile(r"^(\d+).*")
            m = regex.match(text[position:])
            if not m:
                return False, None, -1
            else:
                number = int(m.group(1))
                node.value = number
                return True, node, position + len(str(number))
        if isinstance(node, StringVarNode):
            m = re.match(r"^((\"(.*)\")|(\b\w+\b))", text[position:])
            if not m:
                return False, None, -1
            else:
                # if m.group(3):
                #     s = m.group(3)
                # else:
                s = m.group(0)
                node.value = s
                return True, node, position + len(str(s))
            
        return False, None, -1

    def validate(template_node, text):
        """Validate user input text againts template.

        Args:
            template_node (ParamInputNode): template
            text (str): user text input

        Returns:
            is_valid, parameters: Bool, list
        """
        position = 0
        vars = RuntimeVariables()
        if text[:2] != "< ":
            return False, None
        text = text[2:]
        for node in template_node.ast:
            if position > len(text):
                return False, None
            is_in_text, node, end_position = TemplatesHandler.check(
                node,
                text,
                position)
            if (not is_in_text) or (end_position > len(text)):
                return False, None
            else:
                if isinstance(node, NumberVarNode) or isinstance(node, StringVarNode):
                    vars.unnamed_vars.append(node)
                position = end_position + 1
        return True, vars

    def substitute(text, vars):
        for var in vars.unnamed_vars:
            i = vars.unnamed_vars.index(var)
            text = text.replace("$" + str(i), str(var.value))
        return text
