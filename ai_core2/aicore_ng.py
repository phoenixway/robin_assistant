#!/usr/bin/env python3

import re
import asyncio
import logging
# import pdb
import os
import sys
import json
import nest_asyncio
from py_mini_racer import py_mini_racer
# from quickjs import Function
import js2py
from js2py import require
import lupa
from lupa import LuaRuntime
import actions.default
from pathlib import Path
from ai_core2.rs_parser import RSParser
from ai_core2.ast_nodes import IfInNode, IfNode, StringNode, FnNode  # noqa: E501

sys.path.append(os.getcwd())
nest_asyncio.apply()

# racer = py_mini_racer.MiniRacer()
lua = LuaRuntime(unpack_returned_tuples=True)


def lua_execute(code):
    res = None
    try:
        res = lua.execute(code)
    except Exception as e:
        print(e)
    return res


fn_engine = lua_execute

log = logging.getLogger('pythonConfig')
source_path = Path(__file__).resolve()
source_dir = source_path.parent.parent
stories_ = {}
intents = []
SILENCE_TIME = 10

# s = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, s)

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
        self.robins_story_ids = ['robin_asks']
    
    def get_next_node(n, l, i):
        # pdb.set_trace()
        if isinstance(n, StringNode) or isinstance(n, FnNode):
            return n.next
        elif isinstance(n, IfNode):
            r = eval(n.condition)
            if r:
                return n.first_in_if_block
            else:
                return n.first_in_else_block
        elif isinstance(n, IfInNode):
            if (l[i].startswith("< ") or l[i].startswith("> ")):
                if l[i][2:] not in n.variants:
                    return None
                else:
                    return n.variants[l[i][2:]]
            else:
                if l[i] not in n.variants:
                    return None
                else:
                    return n.variants[l[i]]
        else:
            return None
                    
    def next_in_story(log, s):
        # pdb.set_trace()
        # node to process
        n = s.first_node
        if str(n) not in log:
            return None
        # index in log
        il = len(log) - log[::-1].index(str(n)) - 1
        while (il < len(log)) and (n != None) and (log[il] == n.log_form()):
            il = il + 1
            n = AICore.get_next_node(n, log, il)
        # if story is not actual one
        if il <= len(log) - 1 and log[il] != n.log_form():
            return None
        else:
            return n
            
        
    def next_in_story_old(log, story):
        
        n1 = story.first_node
        n = n1
        s = str(n1)
        # TODO: fix it
        if s not in log:
            return None
        i1 = len(log) - log[::-1].index(s) - 1
        # i1 = log.index(s)
        i = i1
        while i < len(log) and n is not None:
            if isinstance(n, StringNode):
                if log[i] != n.text:
                    return None
                n = n.next
            elif isinstance(n, IfInNode):
                if (log[i].startswith("< ") or log[i].startswith("> ")):
                    if log[i][2:] not in n.variants:
                        return None
                    else:
                        n = n.variants[log[i][2:]]
                else:
                    if log[i] not in n.variants:
                        return None
                    else:
                        n = n.variants[log[i]]
            elif isinstance(n, IfNode):
                # FIXME: see below
                c = eval(n.condition)
                pass
            elif isinstance(n, FnNode):
                # FIXME: add this fnnode to aicore.log
                answer = fn_engine(n.fn_body.rstrip())
                if log[i] != answer:
                    return None
                n = n.next
            else:
                return None
            i = i + 1
        return n

    def start_next_robin_story(self):
        log.debug("start_next_robin_story")
        # TODO: get rid of it
        if self.robins_story_ids:
            s = self.robins_story_ids.pop(0)
            if s is not None:
                self.start_story(s)

    async def do_silence(self):
        log.debug("Silence started")
        await asyncio.sleep(SILENCE_TIME)
        a = self.respond('<silence>')
        if a:
            self.modules['messages'].say(a)
        else:
            self.start_next_robin_story()

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
            next = AICore.next_in_story(self.log, story)
            if next:
                if isinstance(next, FnNode):
                    self.log.append(str(next))
                    answer = fn_engine(n.fn_body.rstrip())
                else:
                    answer = next.text
                    self.log.append(answer)
                    if "> " in answer or "< " in answer:
                        answer = answer[2:]
                break
        return answer

    def start_story(self, story_id):
        # FIXME:whole func
        log.debug("Make story start by Robin's will")
        st = [i for i in self.stories if i.name == story_id][0]
        if story_id and st:
            next_answer = st.first_node.text
            answer = next_answer
            self.log.append(next_answer)
            self.modules['messages'].say(answer[2:])
