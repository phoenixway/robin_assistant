#!/usr/bin/env python3
# import re

from .input_templates import TemplatesHandler


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
        self.value = text
        super().__init__()

    def __str__(self):
        return f'{self.value}'

    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.value}"'

    def equals(self, item):
        return self.value == item


class InputNode(StringNode):
    def __init__(self, text):
        super().__init__(text)

    def validate(message):
        return message[0:2] == "< "


"""
class ParamInputNode(StringNode):
    def __init__(self, text):
        super().__init__(text.replace('%d', r'(\d+)'))

    def validate(self, message):
        if not message[0:2] == "< ":
            return False, None
        if r"(\d+)" in self.value:
            digitsRegex = re.compile(self.value)
            matches = digitsRegex.findall(message)
            return True, matches
        return False, None"""


"""
є можливий елемент сценарію - ввід користувача з параметрами.
реальне текстове повідомлення користувача слід вміти 
    - перевірити на відповідність сценарному
    - його параметри визначити 
    - і передати модулю управління відповіддю ші 
    - правильно запустити наступний сценарний елемент
Алгоритм цього наступний:
    - корстуючись peg отримати ast вузли сценарного шаблону
    - циклом перевірити усі ast nodes на те чи знахїодяться вони послідовно в реальній строці
    - зберігати при цьому поточну позицію строки реальної, на якій йде робота. 
    - очевидно при невідповідності або закінченні реальної строки - що слід контролювати - закінчити і повернути false
    - при відповідності - заповнити змінні які при успіху перевірок передати в управління 
усе сказане слід покрити тестами
"""


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


# def python_execute(code, modules):
#     if modules:
#         if 'db' in modules:
#             db = modules['db']
#         if 'messages' in modules:
#             ms = modules['messages']
#         if 'events' in modules:
#             ev = modules['events']
#         if 'vars' in modules:
#             vars = modules['vars']
#     scheduler = AsyncIOScheduler()
#     lines = code.splitlines()
#     if len(lines[0]) == 0:
#         lines.pop(0)
#     m = re.search(r"(^\s+)", lines[0])
#     zero_indent = len(m.group(1))
#     newlines = []
#     for line in lines:
#         line = re.sub(r"(^\s{"+str(zero_indent)+r"})", "", line)
#         newlines.append(line)
#     new_code = "\n".join(newlines)
#     loc = dict(locals())
#     exec(new_code, globals(), loc)
#     if 'ret' in loc:
#         return loc['ret']
#     else:
#         return None


class FnNode(AstNode):
    def __init__(self, fn_body):
        self.value = fn_body
        
    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self):
        return f'{self.value}'
        # raise Exception("Not implemented")

    # def run(self, modules):
    #     next_answer = python_execute(self.fn_body.rstrip(),
    #                                  modules)
    #     if next_answer is None:
    #         next_answer = "> Done"
    #     else:
    #         next_answer = "> " + next_answer
    #     return next_answer


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

    def __str__(self):
        return f'{id(self)}'

    def __repr__(self):
        return f'{self.__class__.__name__}: "{self.condition}"'


class NodeFactory:
    def create_node(text):
        if InputNode.validate(text):
            return InputNode(text)
        elif OutputNode.validate(text):
            return OutputNode(text)
        else:
            return StringNode(text)
