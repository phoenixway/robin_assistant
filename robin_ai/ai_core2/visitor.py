#!/usr/bin/env python3

from parsimonious.nodes import NodeVisitor
from .ast_nodes import ElifVariant, IfInNode, IfNode, AstNode, InputNode, OutputNode, FnNode, ParamInputNode  # noqa: E501
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

    def visit_maybe_story_name(self, node, visited_children):
        return visited_children[0] if len(visited_children) > 0 else None

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
        return OutputNode(s) if s.startswith("> ") else InputNode(s)

    def visit_oneliner_with_params(self, node, visited_children):
        return visited_children[0]

    def visit_input_var(self, node, visited_children):
        return node.text

    def visit_random_input(self, node, visited_children):
        return ParamInputNode("< *")

    def visit_oneliner_with_vars(self, node, visited_children):
        buf = []
        for child in visited_children:
            if child == "not_important":
                continue
            striped_child = child.strip()
            if len(striped_child) > 0:
                buf.append(striped_child)
        s = " ".join(buf)
        return ParamInputNode(s)

    def visit_maybe_text(self, node, visited_children):
        return node.text

    def visit_if_in_statement(self, node, visited_children):
        # TODO: при заповненні ifnode якщо існує ifnode.next цей next має бути  і в next полі самих останніх вкладених statements if`a  # noqa: E501
        n = IfInNode()
        for child in visited_children:
            if child != "not_important":
                n.variants = []
                n.last_statements = []
                for item in child:
                    n.variants.append(item[0])
                    n.last_statements.append(item[1])
        return n

    def visit_if_in_variant_must(self, node, visited_children):
        return visited_children

    def visit_if_in_variant(self, node, visited_children):
        message = ""
        # 1st node (without trigger input node) in nodes chain of this variant
        n1 = []
        # last node in nodes chain of this variant
        last = []
        for child in visited_children:
            if isinstance(child, tuple):
                n1, last = child
            elif child != "not_important" and not isinstance(child, AstNode):
                message = child.strip()
        # trigger input node of this variant
        inp = InputNode("< " + message)
        # and other following nodes
        inp.next = n1
        return inp, last

    def visit_if_start(self, node, visited_children):
        return {
            "condition": child
            for child in visited_children
            if child != "not_important"
        }

    def visit_if_condition(self, node, visited_children):
        pass

    def visit_else_part(self, node, visited_children):
        lst = [child for child in visited_children if child != "not_important"]
        lst = lst[0]
        return {"else_part": lst}

    def visit_maybe_else_part(self, node, visited_children):
        if lst := [
            child for child in visited_children if child != "not_important"
        ]:
            return lst[0]
        else:
            return None

    def visit_if_block(self, node, visited_children):
        return visited_children

    def visit_parameter(self, node, visited_children):
        return visited_children[0]

    def visit_fn_statement(self, node, visited_children):
        fn = None
        for child in visited_children:
            if child != "not_important":
                fn = FnNode(child[4:-5])
        return fn

    def visit_code(self, node, visited_children):
        return node.text

    def visit_block(self, node, visited_children):
        n = None
        n1 = None
        for child in visited_children:
            if child != "not_important":
                for node in child:
                    if node == "not_important":
                        continue
                    if n is not None:
                        if isinstance(n, IfInNode):
                            for st in n.last_statements:
                                st.next = node
                        if isinstance(n, IfNode):
                            n.next_if_true.next = node
                            n.next_if_else.next = node
                            for v in n.elif_variants:
                                v.node.next = node
                                n.next = node
                        n.next = node
                        n.next.parent = n
                        n = node
                    else:
                        n = node
                        n1 = node
        return n1

    def visit_if_in_variant_block(self, node, visited_children):
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

    def make_nodes_chain(lst):
        i = 0
        while i < len(lst):
            if i + 1 < len(lst):
                lst[i].next = lst[i + 1]
            if i - 1 >= 0:
                lst[i].parent = lst[i - 1]
            i += 1
        return lst[0], lst[-1]

    def visit_else_substatement(self, node, visited_children):
        return next(
            (
                child['then']
                for child in visited_children
                if isinstance(child, dict) and 'then' in child
            ),
            None,
        )
    
    def visit_elif_tag(self, node, visited_children):
        l = [c for c in visited_children if c != 'not_important']
        return {'elif': l[0]} if l else None
    
    def visit_maybe_else_part(self, node, visited_children):
        return {'else': visited_children[0]} if visited_children else None
    
    def visit_elif_substatement(self, node, visited_children):
        v = ElifVariant()
        for child in visited_children:
            if isinstance(child, dict):
                if 'elif' in child:
                    v.condition = child['elif']
                if 'then' in child:
                    v.node = child['then']
        return v if v.node and v.condition else None
    
    def visit_maybe_elif_substatements(self, node, visited_children):
        if l := [child for child in visited_children if child != 'not_important']:
            return {'elifs': l}
        else:
            return None
    
    def visit_then_part(self, node, visited_children):
        return {'then': visited_children[0]}
    
    def visit_if_tag(self, node, visited_children):
        return {'condition': node.text[4:-5]}
    
    def visit_elif_tag(self, node, visited_children):
        return {'elif': node.text[6:-7]}
    
    def visit_if_statement(self, node, visited_children):
        n = IfNode()
        for child in visited_children:
            if isinstance(child, dict):
                if 'condition' in child:
                    n.condition = child['condition']
                if 'then' in child:
                    n.next_if_true = child['then']
                if 'else' in child:
                    n.next_if_else = child['else']
                if 'elifs' in child:
                    n.elif_variants = child['elifs']
        return n

    def generic_visit(self, node, visited_children):
        return "not_important"
