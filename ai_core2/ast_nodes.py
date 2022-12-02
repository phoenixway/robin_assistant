#!/usr/bin/env python3

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


class FnNode(AstNode):
    def __init__(self, fn_body):
        self.fn_body = fn_body
    
    def __str__(self):
        return f'{self.fn_body}'
        # raise Exception("Not implemented")


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
