#!/usr/bin/env python3

import string
import random


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
