#!/usr/bin/env python3

import re
import asyncio
import logging
import os
import sys
import json
import nest_asyncio
from pathlib import Path
from .rs_parser import RSParser
from .ast_nodes import IfInNode, IfNode
from .ast_nodes import InputNode
from .ast_nodes import OutputNode, FnNode, ParamInputNode
from .input_templates import TemplatesHandler, RuntimeVariables

sys.path.append(os.getcwd())
nest_asyncio.apply()

tasks = set()
log = logging.getLogger('pythonConfig')
# source_path = Path(__file__).resolve()
# source_dir = source_path.parent.parent


class AI:
    def __init__(self, modules):
        # create_default_stories()
        #  TODO: check that brains exist
        source_dir = Path(modules['config']['brains_path'])
        self.intents = []
        with open(source_dir / 'default.intents', 'r') as f:
            self.intents = json.load(f)
        with open(source_dir / 'default.stories', 'r') as f:
            s = f.read()
            self.stories = RSParser.create_from_text(s)
        self.story_ids = [s.name for s in self.stories]
        self.modules = modules
        self.active_story = None
        self.runtime_vars = RuntimeVariables()
        self.history = []
        if modules is not None:
            modules['events'].add_listener('message_received', self.message_received_handler)  # noqa: E501
            modules['events'].add_listener('message_send', self.message_send_handler)  # noqa: E501
        self.silence_task = None
        self.is_started = True
        self.repeat_if_silence = False
        self.handle_silence = True
        self.robins_story_ids = []
        self.set_silence_time(minutes=2)

    def recognize_intent(self, text):
        for intent in self.intents:
            text = text.lower()
            m = re.match(intent, text)
            if m is not None:
                return self.intents[intent]

    # text_input_to_canonical_form
    def to_canonical(self, text):
        res = f"< {text}"
        intent = self.recognize_intent(text)
        if intent is not None:
            res = f"< <intent>{intent}"
        # TODO: combine intents and parameters
        return res

    def set_silence_time(self, minutes=0, seconds=0):
        self.silence_time = minutes * 60 + seconds

    def run_expr(self, expr):
        m = self.modules
        return eval(expr, globals(), locals())

    def next_str_node(self, n, log, i):
        res = None
        if isinstance(n, InputNode) or isinstance(n, OutputNode) or \
           isinstance(n, FnNode) or isinstance(n, ParamInputNode):
            res = n.next
        elif isinstance(n, IfNode):
            r = self.run_expr(n.condition)
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

    def get_next(self, log, s):
        '''Get story next element'''
        n = s.first_node
        # detect if n is user input with parameters
        if isinstance(n, ParamInputNode):
            valid, vars = n.validate(log[0])
            if valid:
                self.runtime_vars = vars
                log[-1] = n.value
            else:
                return None
        elif (n is None) or (str(n) not in log):
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

    def eat_singal(self, signal):
        pass

    def eat_text(self, text):
        log.debug("Parsing user input with ai.eat_text")
        if text == '<silence>':
            return None
        else:
            answer = f"Default answer on '{text}'"
        # спочатку задетектити чи не регекс
        self.history.append(self.to_canonical(text))
        # next in story must return also list of variables' values
        # or something similar

        for story in self.stories:
            next = self.get_next(self.history, story)
            if next:
                if isinstance(next, FnNode):
                    if self.modules is None:
                        self.modules = dict()
                    self.modules['vars'] = self.runtime_vars
                    answer = next.run(self.modules)
                else:
                    answer = next.value
                break
        self.history.append(answer)
        if "> " in answer or "< " in answer:
            answer = answer[2:]
        return TemplatesHandler.substitute(answer, self.runtime_vars)

    def add_to_own_will(self, story_id):
        self.robins_story_ids.append(story_id)

    def add_story_by_source(self, source):
        new_stories = RSParser.create_from_text(source)
        # TODO: handle dublicates
        # for s in new_stories:
        #     if s.name in 
        self.stories.extend(new_stories)
        pass

    def force_own_will_story(self):
        log.debug("force_own_will_story")
        if self.robins_story_ids:
            s = self.robins_story_ids.pop(0)
            if s is not None:
                self.force_story(s)

    async def start_silence(self):
        log.debug("Silence detection started")
        while self.handle_silence and self.modules['messages'].websockets:
            log.debug(f"Waiting silence for {self.silence_time} seconds")
            await asyncio.sleep(self.silence_time)
            log.debug("Silence detected")
            if self.robins_story_ids:
                self.force_own_will_story()
        # a = self.respond('<silence>')
        # if a:
        #     self.modules['messages'].say(a)
        # else:
        #     self.start_next_robin_story()

    def init_silence(self):
        if self.handle_silence:
            if self.silence_task is not None:
                self.silence_task.cancel()
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if (loop is not None) and (loop.is_running()):
                self.silence_task = loop.create_task(self.start_silence())
            else:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.silence_task = loop.create_task(self.start_silence())
            tasks.add(self.silence_task)
            # self.silence_task = asyncio.create_task(self.start_silence())

    async def message_received_handler(self, data):
        log.debug('message received handler')
        self.init_silence()

    async def message_send_handler(self, data):
        log.debug('message send handler')
        self.init_silence()

    def force_story(self, story_id):
        # FIXME:whole func
        if not self.modules['messages'].websockets:
            return
        log.debug("Make story start")
        st = [i for i in self.stories if i.name == story_id][0]
        if story_id and st:
            # TODO: parse any nodes
            if isinstance(st.first_node, FnNode):
                next_answer = st.first_node.run(self.modules)
            else:
                next_answer = TemplatesHandler.substitute(st.first_node.value, self.runtime_vars)
                # if "> " in next_answer or "< " in next_answer:
                #     next_answer = next_answer[2:]
            self.history.append(next_answer)
            self.modules['messages'].say(next_answer[2:])