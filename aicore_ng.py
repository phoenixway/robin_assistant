#!/usr/bin/env python3

import string
import random 
import re

class AstNode:
    pass


class StoryFactory:
    def create_from_text(text):
        m = re.match(r"^(\s*)story(\s+)(\w+)(\s+)\{().*)\}$", text)
        if m is None:
            return None
        else:
            return None

class Story:
    def contains(self, item):
        pass

    def __init__(self, name = "", first_node = None):
        self._name = name
        self.first_node = first_node

    @property
    def name(self):
        if not self._name and not self.first_node:
            raise Exception("Not initialized story!")
        elif not self._name:
            letters = string.ascii_letters
            self._name = ''.join(random.choice(letters) for i in range(10)) 
        return self._name

             
class AICore:
    def log_contains(log, text):
        return False   
