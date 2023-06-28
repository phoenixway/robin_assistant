#!/usr/bin/env python3
import re
from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError, VisitationError


class NumberVarNode:
    pass


class InputVisitor():
    def generic_visit(self, node, visited_children):
        return "not_important"


class TemplatesHandler():
    def __init_(self):
        # в варіантах має бути можливе використання параметрів, інших варіантів
        # змінні з умовним форматуванням
        self.raw_input_grammar = """
            message = statement_or_raw_text*
            statement_or_raw_text = (statement / raw_text)
            statement = number_param
            raw_text = ~r"[-\w\s\?\!\.\,\d\'\`]+"
            ws = ~r"\s"
            number_param = ~r"%\d+"
        """
        self.input_grammar = Grammar(self.raw_input_grammar)
        self.visitor = InputVisitor()

    def validate_templete(self, templete):
        try:
            parsed = self.input_grammar.parse(templete)
            _ = self.visitor.visit(parsed)
        except (ParseError, VisitationError) as error:
            print(error)
            return False
        return True

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
                number = int(m.group(0))
                return True, number, position + len(str(number))
        return False, None, -1

    def validate(self, template_node, text):
        """Validate user input text againts template.

        Args:
            template_node (ParamInputNode): template
            text (str): user text input

        Returns:
            is_valid, parameters: Bool, list
        """
        position = 0
        params = []
        for node in template_node.ast:
            if position > len(text):
                return False, None
            is_in_text, node_params, end_position = TemplatesHandler.check(
                node,
                text,
                position)
            if (not is_in_text) or (end_position > len(text)):
                return False, None
            else:
                params.extend(node_params)
                position = end_position + 1
        return True, params

