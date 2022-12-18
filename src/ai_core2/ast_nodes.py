#!/usr/bin/env python3
import re
# import sys


class AstNode:
    def __init__(self):
        self.parent = None
        self.next = None

    def __str__(self):
        return f'{self.__class__.__name__}'

    def __repr__(self):
        return f'{self.__class__.__name__}'

    def log_form(self):
        return str(self)
    
    def equals(self, item):
        raise Exception("Not implemented yet")


class StringNode(AstNode):
    def __init__(self, text):
        self.text = text
        super().__init__()

    def __str__(self):
        return f'{self.text}'

    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.text}"'
        
    def equals(self, item):
        return self.text == item


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


def python_execute(code, modules):
    if modules:
        if 'db' in modules:
            db = modules['db']
        if 'messages' in modules:
            ms = modules['messages']
        if 'events' in modules:
            ev = modules['events']
    lines = code.splitlines()
    if len(lines[0]) == 0:
        lines.pop(0)
    m = re.search(r"(^\s+)", lines[0])
    zero_indent = len(m.group(1))
    newlines = []
    for line in lines:
        line = re.sub(r"(^\s{"+str(zero_indent)+r"})", "", line)
        newlines.append(line)
    new_code = "\n".join(newlines)
    loc = dict(locals())
    exec(new_code, globals(), loc)
    if 'ret' in loc:
        return loc['ret']
    else:
        return None


class FnNode(AstNode):
    def __init__(self, fn_body):
        self.fn_body = fn_body
    
    def __str__(self):
        return f'{self.fn_body}'
        # raise Exception("Not implemented")
    
    def run(self, modules):
        next_answer = python_execute(self.fn_body.rstrip(),
                                     modules)
        if next_answer is None:
            next_answer = "> Done"
        else:
            next_answer = "> " + next_answer
        return next_answer


class IfInNode(AstNode):
    def __init__(self):
        self.variants = {}
        self.last_statements = {}
        super().__init__()

    def __str__(self):
        return f'{id(self)}'
        
    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.variants}"'

    def validate(message):
        return False


class IfNode(AstNode):
    def __init__(self):
        self.condition = None
        self.first_in_if_block = None
        self.first_in_else_block = None
        self.last4block = None
        self.last4else_block = None
        super().__init__()

    def __str__(self):
        return f'{id(self)}'

    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.condition}"'

    def validate(message):
        return False        


class NodeFactory:
    def create_node(text):
        if MessageInNode.validate(text):
            return MessageInNode(text)
        elif MessageOutNode.validate(text):
            return MessageOutNode(text)
        else:
            return StringNode(text)
