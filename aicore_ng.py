#!/usr/bin/env python3

import string
import random 
import re


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


class RSParser:
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