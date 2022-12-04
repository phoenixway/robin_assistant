#!/usr/bin/env python3

import re
import asyncio
import logging
import os
import sys
import json
import nest_asyncio
from lupa import LuaRuntime
from pathlib import Path
from ai_core2.rs_parser import RSParser
from .ast_nodes import IfInNode, IfNode
from .ast_nodes import MessageInNode
from .ast_nodes import MessageOutNode, FnNode

sys.path.append(os.getcwd())
nest_asyncio.apply()
lua = LuaRuntime(unpack_returned_tuples=True)


def lua_execute(code):
    res = None
    try:
        res = lua.execute(code)
    except Exception as e:
        log.error(e)
    return res


def python_execute(code):
    lines = code.splitlines()
    whitespaces = re.compile(r"\s+")

    for line in lines:
        m = whitespaces.search(line)
        line = whitespaces.sub(" ", line)
    
    return exec(code)


fn_engine = python_execute

log = logging.getLogger('pythonConfig')
source_path = Path(__file__).resolve()
source_dir = source_path.parent.parent
stories_ = {}
intents = []
SILENCE_TIME = 10

with open(source_dir/'brains/default.intents', 'r') as f:
    intents = json.load(f)


def recognize_intent(text):
    for intent in intents:
        text = text.lower()
        m = re.match(intent, text)
        if m is not None:
            return intents[intent]


class AICore:
    def __init__(self, modules):
        # create_default_stories()
        #  TODO: check that brains exist
        with open(source_dir/'brains/default.stories', 'r') as f:
            s = f.read()
            self.stories = RSParser.create_from_text(s)
        self.modules = modules
        self.active_story = None
        self.log = []
        if modules is not None:
            modules['events'].add_listener('message_received', self.message_received_handler)  # noqa: E501
            modules['events'].add_listener('message_send', self.message_send_handler)  # noqa: E501
        self.silence_task = None
        self.is_started = True
        self.repeat_if_silence = False
        self.handle_silence = True
        self.robins_story_ids = []

    def run(self, expr):
        m = self.modules
        return eval(expr, locals=[m])

    def next_str_node(self, n, log, i):
        res = None
        if isinstance(n, MessageInNode) or isinstance(n, MessageOutNode) or \
           isinstance(n, FnNode):
            res = n.next
        elif isinstance(n, IfNode):
            r = self.run(n.condition)
            if r:
                res = n.first_in_if_block
            else:
                res = n.first_in_else_block
        elif isinstance(n, IfInNode):
            lst = [it for it in n.variants if str(it) == log[i]]
            if lst:
                res = lst[0]
            else:
                res = None
        else:
            res = None
        if res is not None:
            if isinstance(res, IfNode) or isinstance(res, IfInNode):
                res = self.next_str_node(res, log, i)
        return res

    def next_in_story(self, log, s):
        # pdb.set_trace()
        # node to process
        n = s.first_node
        if (n is None) or (str(n) not in log):
            return None
        # index in log
        il = len(log) - log[::-1].index(str(n)) - 1
        # TODO: how to handle ifinnode as n and one of its variants's key as
        # log[il]?
        # TODO: what to do when n is control statement?
        while True:
            il = il + 1
            n = self.next_str_node(n, log, il)
            if (il >= len(log)) or (n is None) or (log[il] != n.log_form()):
                break
        if il < len(log) and n is not None and log[il] != n.log_form():
            return None
        else:
            return n

    def respond(self, text):
        # pdb.set_trace()
        log.debug("Parsing with aicore")
        if text == '<silence>':
            return None
        else:
            answer = f"Default answer on '{text}'"
        intent = recognize_intent(text)
        if intent is not None:
            self.log.append(f"< <intent>{intent}")
        else:
            self.log.append("< " + text)

        for story in self.stories:
            next = self.next_in_story(self.log, story)
            if next:
                if isinstance(next, FnNode):
                    # self.log.append(str(next))
                    answer = fn_engine(next.fn_body.rstrip())
                else:
                    answer = next.text
                    self.log.append(answer)
                    if "> " in answer or "< " in answer:
                        answer = answer[2:]
                break
        return answer

    def start_next_robin_story(self):
        log.debug("start_next_robin_story")
        if self.robins_story_ids:
            s = self.robins_story_ids.pop(0)
            if s is not None:
                self.start_story(s)

    async def do_silence(self):
        if not self.modules['messages'].websockets:
            return
        log.debug("Silence detected")
        await asyncio.sleep(SILENCE_TIME)
        if self.robins_story_ids:
            self.start_next_robin_story()
        # a = self.respond('<silence>')
        # if a:
        #     self.modules['messages'].say(a)
        # else:
        #     self.start_next_robin_story()

    async def message_received_handler(self, data):
        log.debug('message received handler')
        if self.handle_silence:
            if self.silence_task is not None:
                self.silence_task.cancel()
            self.silence_task = asyncio.create_task(self.do_silence())

    async def message_send_handler(self, data):
        log.debug('message send handler')
        if self.handle_silence:
            if self.silence_task is not None:
                self.silence_task.cancel()
            self.silence_task = asyncio.create_task(self.do_silence())

    def start_story(self, story_id):
        # FIXME:whole func
        if not self.modules['messages'].websockets:
            return
        log.debug("Make story start by Robin's will")
        st = [i for i in self.stories if i.name == story_id][0]
        if story_id and st:
            # TODO: parse any nodes
            next_answer = st.first_node.text
            answer = next_answer
            self.log.append(next_answer)
            self.modules['messages'].say(answer[2:])
