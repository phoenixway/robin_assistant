#!/usr/bin/env python3

from parsimonious.nodes import NodeVisitor
from .ast_nodes import IfNode, AstNode, MessageInNode, MessageOutNode, FnNode  # noqa: E501
from .story import Story


class RSVisitor(NodeVisitor):
    def visit_stories(self, node, visited_children):
        return visited_children

    def visit_story(self, node, visited_children):
        story_name = ""
        fst_node = []
        for child in visited_children:
            if isinstance(child, dict):
                story_name = child['story_name']
            elif isinstance(child, AstNode):
                fst_node = child
        s = Story(story_name)
        s.first_node = fst_node
        return s

    def visit_story_name(self, node, visited_children):
        return {'story_name': node.text}

    def visit_statement(self, node, visited_children):
        return visited_children[0]

    def visit_oneliner(self, node, visited_children):
        buf = []
        for child in visited_children:
            if child == "not_important":
                continue
            if len(child) > 0:
                buf.append(child.strip())
        s = " ".join(buf)
        n = MessageOutNode(s) if s[:2] == "> " else MessageInNode(s)
        return n

    def visit_if_statement(self, node, visited_children):
        # TODO: при заповненні ifnode якщо існує ifnode.next цей next має бути  і в next полі самих останніх вкладених statements if`a  # noqa: E501
        n = IfNode()
        for child in visited_children:
            if child != "not_important":
                for d in child:
                    param = tuple(d.keys())[0]
                    n1, n2 = d[param]
                    n.variants[param] = n1
                    n.last_statements[param] = n2
        return n

    def visit_if_variant_must(self, node, visited_children):
        return visited_children

    def visit_if_variant(self, node, visited_children):
        param = ""
        n1 = []
        n2 = []
        for child in visited_children:
            if isinstance(child, tuple):
                n1, n2 = child
            elif child != "not_important" and not isinstance(child, AstNode):
                param = child.strip()
        return {param: (n1, n2)}

    def visit_parameter(self, node, visited_children):
        pass
        return visited_children[0]

    def visit_fn_statement(self, node, visited_children):
        fn = None
        for child in visited_children:
            if child != "not_important":
                fn = FnNode(child)
        return fn

    def visit_code(self, node, visited_children):
        return node.text

    def visit_block(self, node, visited_children):
        n = None
        n1 = None
        for child in visited_children:
            if child != "not_important":
                for node in child:
                    if n is not None:
                        if isinstance(n, IfNode):
                            for keys in n.last_statements:
                                n.last_statements[keys].next = node
                        n.next = node
                        n.next.parent = n
                        n = node
                    else:
                        n = node
                        n1 = node
        return n1

    def visit_if_variant_block(self, node, visited_children):
        n = None
        n1 = None
        for child in visited_children:
            if child != "not_important":
                for node in child:
                    if n is not None:
                        n.next = node
                        n.next.parent = n
                        n = node
                    else:
                        n = node
                        n1 = node
        return n1, n

    def visit_inout(self, node, visited_children):
        return node.text

    def visit_intent_parameter(self, node, visited_children):
        pass
        return f"{node.text.strip()}"

    def visit_maybe_statements(self, node, visited_children):
        return visited_children

    def visit_raw_text(self, node, visited_children):
        return node.text

    def visit_text(self, node, visited_children):
        return node.text

    def generic_visit(self, node, visited_children):
        return "not_important"
