#!/usr/bin/env python3
# import re

from .input_templates import TemplatesHandler
from .fn_runner import FnRunner

try:
    from ..actions_queue import Action
    from ..actions_queue import ActionType
except ImportError:
    from actions_queue import Action
    from actions_queue import ActionType


fn_runner_obj = FnRunner()


class AstNode:
    def __init__(self):
        self.parent = None
        self.next = None

    def __str__(self):
        return f'{self.__class__.__name__}'

    def __repr__(self):
        return f'{self.__class__.__name__}'

    def map_to_history(self) -> str:
        return str(self.value)
    
    def equals(self, item):
        return self.map_to_history() == str(item)

    def implement(modules : dict) -> str:
        raise Exception("Not implemented yet!") 


class StringNode(AstNode):
    def __init__(self, text):
        self.value = text
        super().__init__()

    def __str__(self):
        return f'{self.value}'

    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.value}"'

    def implement(self, modules : dict) -> str:
        answer = self.value
        # FIXME: do smt with repeation of output
        # if isinstance(n, OutputNode) and self.is_repeating(n):
        #     pass
        # else:
        #     self.history.append(answer)
        #     if "> " in answer or "< " in answer:
        #         answer = answer[2:]
        #     self.modules['actions_queue'].add_action(Action(ActionType.SendMessage, TemplatesHandler.substitute(answer, self.runtime_vars)))
        #     if "> " in answer or "< " in answer:
        #         answer = answer[2:]
        modules['ai'].history.append(answer)
        if "> " in answer or "< " in answer:
            answer = answer[2:]
        modules['actions_queue'].add_action(Action(ActionType.SendMessage, TemplatesHandler.substitute(answer, modules['vars'])))
        if "> " in answer or "< " in answer:
            answer = answer[2:]
        if self.next is not None and not isinstance(self.next, (InputNode, IfInNode)):
            self.next.implement(modules)
        return answer

class InputNode(StringNode):
    def __init__(self, text):
        super().__init__(text)

    def validate(message):
        return message[0:2] == "< "


class ParamInputNode(StringNode):
    def __init__(self, text):
        # парсить при створенні
        _, self.ast = parsed, ast = TemplatesHandler.validate_template(text)
        super().__init__(text)

    def validate(self, message):
        '''Check if message entered by user suites this ParamInputNode instance's template, stored in self.value
        '''
        result = TemplatesHandler.validate(self, message)
        return result


class OutputNode(StringNode):
    def __init__(self, message):
        super().__init__(message)

    def validate(message):
        return message[0:2] == "> "


class IfInNode(AstNode):
    def __init__(self):
        self.variants = {}
        self.last_statements = {}
        super().__init__()

    def __str__(self):
        return f'{id(self)}'

    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.variants}"'


class ElifVariant():
    def __init__(self, condition=None, node=None) -> None:
        self.condition = condition
        self.node = node


class IfNode(AstNode):

    def __init__(self):
        self.condition = None
        self.next_if_true = None
        self.elif_variants = None
        self.next_if_else = None
        self.next = None
        super().__init__()

    def __hash__(self) -> int:
        return hash(self.value)
    
    def map_to_history(self) -> str:
        return str(hash(self.condition))

    def __str__(self):
        return self.map_to_history()

    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.condition}"'
    
    def implement(self, modules : dict) -> str:
        # FIXME implement is recursive, so changes to aicore.history are needed
        answer = "error"
        try:
            modules['ai'].history.append(self.map_to_history())
            fn_runner_obj.modules = modules
            if fn_runner_obj.eval_expr(self.condition, modules):
                self.next_if_true.implement(modules)
            else:
                if n.elif_variants:
                    for item in n.elif_variants:
                        if self.eval_expr(item.condition):
                            item.node.implement(modules)
                            answer = 'not_None'
                            break
                if answer != 'not_None':
                    n.next_if_else.implement(modules)
            answer = 'not_None'
        except Exception as e:
            log.error(e)
        return answer

class NodeFactory:
    def create_node(text):
        if InputNode.validate(text):
            return InputNode(text)
        elif OutputNode.validate(text):
            return OutputNode(text)
        else:
            return StringNode(text)
