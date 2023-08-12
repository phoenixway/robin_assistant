#!/usr/bin/env python3

import datetime
import re
import asyncio
import logging
import os
import sys
import json
import copy
import nest_asyncio
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time
from pprint import pformat

try:
    from ..actions_queue import Action
    from ..actions_queue import ActionType
except ImportError:
    from actions_queue import Action
    from actions_queue import ActionType

from .rs_parser import RSParser
from .ast_nodes import AstNode, IfInNode, IfNode
from .ast_nodes import InputNode
from .ast_nodes import OutputNode, FnNode, ParamInputNode
from .input_templates import TemplatesHandler, RuntimeVariables

sys.path.append(os.getcwd())
nest_asyncio.apply()
tasks = set()
log = logging.getLogger('pythonConfig')


class API:
    def today_str():
        return datetime.now().strftime('%Y-%m-%d')
    
    def is_time_between(begin_time, end_time, check_time=None): 
        # If check time is not given, default to current time
        check_time = check_time or datetime.now().time()
        if begin_time < end_time:
            return check_time >= begin_time and check_time <= end_time
        else: # crosses midnight
            return check_time >= begin_time or check_time <= end_time


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
        self.story_ids = [s.name for s in self.stories] if self.stories else []
        self.modules = modules
        self.active_story = None
        self.runtime_vars = RuntimeVariables()
        self.history = []
        if modules is not None and 'events' in modules:
            modules['events'].add_listener('message_received', self.message_received_handler)  # noqa: E501
            modules['events'].add_listener('message_send', self.message_send_handler)  # noqa: E501
        self.silence_task = None
        self.is_started = True
        self.repeat_if_silence = False
        self.handle_silence = True
        self.robins_story_ids = []
        if 'debug' in modules['config']:
            self.set_silence_time(seconds=15)
        else:
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
        if isinstance(n, (InputNode, OutputNode, FnNode, ParamInputNode)):
            res = n.next
        elif isinstance(n, IfNode):
            res = None
            if self.eval_expr(n.condition):
                res = n.next_if_true
            else: 
                if n.elif_variants:
                    for v in n.elif_variants:
                        r1 = self.run_expr(v.condition)
                        if r1:
                            res = v.node
                            break
                res = n.next_if_else
        elif isinstance(n, IfInNode):
            if lst := [it for it in n.variants if str(it) == log[i]]:
                res = lst[0]
            else:
                res = None
        else:
            res = None
        if res is not None and isinstance(res, (IfNode, IfInNode)):
            res = self.next_str_node(res, log, i)
        return res

    def is_mapped(self, n : AstNode, item) -> bool:
        """
        Check if n maps to a current history element.
        item - element of history
        """
        if isinstance(n, ParamInputNode):
            valid, vars = n.validate(item)
            if valid:
                self.runtime_vars = vars
                return True
            else:
                return False
        elif isinstance(n, (FnNode, IfNode)):
            return n.map_to_history() == str(item)
        else:
            return n.equals(item)
    
    def eat_singal(self, signal):
        pass

    def init_key(self, key : str, m : dict) -> dict:
        if key not in m:
            m[key] = None
        return m

    def init_runtime_modules(self):
        m = self.modules
        m = self.init_key('db', m)
        m = self.init_key('messages', m)
        m = self.init_key('events', m)
        return m['db'], m['messages'], m['events'], self.runtime_vars, self
    
    def eval_expr(self, e):
        db, ms, ev, vars, ai = self.init_runtime_modules()
        scheduler = AsyncIOScheduler()
        scheduler.start()
        lines = e.splitlines()
        if len(lines[0]) == 0:
            lines.pop(0)
        if m := re.search(r"(^\s+)", lines[0]):
            zero_indent = len(m[1])
            newlines = []
            for line in lines:
                line = re.sub(r"(^\s{" + str(zero_indent) + r"})", "", line)
                newlines.append(line)
            new_code = "\n".join(newlines)
        else:
            new_code = e.lstrip().rstrip("\n")
        loc = dict(locals())
        res = False
        try:
            res = eval(new_code, globals(), loc)
        except Exception as e:
            log.error(f"Error executing <if>: {e}")
        return res

    def run_code(self, c):
        db, ms, ev, vars, ai = self.init_runtime_modules()
        scheduler = AsyncIOScheduler()
        scheduler.start()
        lines = c.splitlines()
        if len(lines[0]) == 0:
            lines.pop(0)
        m = re.search(r"(^\s+)", lines[0])
        zero_indent = len(m[1])
        newlines = []
        for line in lines:
            line = re.sub(r"(^\s{" + str(zero_indent) + r"})", "", line)
            newlines.append(line)
        new_code = "\n".join(newlines)
        loc = dict(locals())
        ret = None
        try:
            exec(new_code, globals(), loc)
        except Exception as e:
            log.error(f"Error executing <fn>: {e}")
            log.debug(pformat(c))
            return f"Error executing <fn>: {e}"
        return loc.get('ret')

    def execute_fn(self, node : FnNode) -> str:
        self.history.append(node.map_to_history())
        if self.modules is None:
            self.modules = {'vars': self.runtime_vars}
        else:
            self.modules['vars'] = self.runtime_vars
        if answer := self.run_code(node.value.rstrip()):
            self.history.append(f"> {answer}")
            self.modules['actions_queue'].add_action(Action(ActionType.SendMessage, TemplatesHandler.substitute(answer, self.runtime_vars)))    
        
        # else:
        #     # TODO: поки що fnnode без текстової відповіді видаляємо з логу
        #     del self.history[-1]

    def nodes_until_input(self, node : AstNode) -> list:
        """Returns all the children nodes until first InputNode"""
        if node is None:
            return []

        if not node.next:
            return [node]
        elif not isinstance(node, (InputNode, IfInNode)):
            return [node] + self.nodes_until_input(node.next)
        else:
            return []
# l = self.nodes_until_input(n)
        # if len(l) > 1:
        #     for item in list(set(copy.deepcopy(l))):
        #         item.next = None
        #         self.implement(item)
    def raw_implement(self, n : AstNode) -> str:
        answer = None
        if isinstance(n, IfNode):
            # TODO: check conditions, process (run/send message/whatever) depending on them
            self.history.append(n.map_to_history())
            if self.eval_expr(n.condition):
                self.raw_implement(n.next_if_true)
            else:
                if n.elif_variants:
                    for item in n.elif_variants:
                        if self.eval_expr(item.condition):
                            self.raw_implement(item.node)
                            answer = 'not_None'
                            break
                if answer != 'not_None':
                    self.implement(n.next_if_else)
            answer = 'not_None'
        elif isinstance(n, FnNode):
            self.execute_fn(n)
            answer = 'not_None'
        elif isinstance(n, IfInNode):
            self.execute_fn(n)
            answer = 'not_None'
        else:
            answer = n.value
            self.history.append(answer)
            if "> " in answer or "< " in answer:
                answer = answer[2:]
            self.modules['actions_queue'].add_action(Action(ActionType.SendMessage, TemplatesHandler.substitute(answer, self.runtime_vars)))
        if n.next is not None and not isinstance(n.next, (InputNode, IfInNode)):
            self.raw_implement(n.next)
        return answer
        
    def implement(self, n: AstNode) -> str:
        return self.raw_implement(n)
        # for n in self.nodes_until_input(n):
        #     answer = 
            
    def get_next(self, history, s) -> AstNode:
        '''Get story next element'''
        # if s.name == 'day_preparation':
                 # breakpoint()
        n = s.first_node
        # detect if n is user input with parameters
        # TODO: fix bellow
        if n is None:
            return None
        if self.is_mapped(n, history[-1]):
            history[-1] = n.value
        if n.map_to_history() not in history:
            return None

        # elif n is None or (str(n) not in history):
        # TODO: replace str(n) in history() for more suitable variant. including fnnode, ifnode cases
        # TODO: take care for cases where story has several same nodes as first one
        # if str(n) not in history:
        #     return None
        il = len(history) - history[::-1].index(str(n)) - 1
        # TODO: how to handle ifinnode as n and one of its variants's key as log[il]?
        # TODO: what to do when n is control statement?
        while True:
            il = il + 1
            n = self.next_str_node(n, history, il)
            # breakpoint()
            # if (il >= len(log)) or (n is None) or ( log[il] != n.log_form()):
            if (il >= len(history)) or (n is None) or (not self.is_mapped(n, history[il])):
                break
        return None if n is None or (il < len(history) and not self.is_mapped(n, history[il])) else n
    
    def respond_text(self, text):  # sourcery skip: remove-pass-elif
        log.debug("Parsing user input with ai.respond_text")
        # import pdb; pdb.set_trace();
        sc_match = re.compile(r":(\w+)")
        if sc_match.search(text):
            self.modules['actions_queue'].add_action(Action(ActionType.SystemCommand, text.strip()))
            return
        else:
            self.history.append(self.to_canonical(text))
        answer = None
        for story in self.stories:
            # if story.name == 'day_preparation':
                # breakpoint()
            # якщо зловили story, перша частину якої від її початку пересікається з останньою частиною логу спілкування, включаючи останню запис
            # імплементуємо елемент історії, який має бути наступним
            if next_node := self.get_next(self.history, story):
                # breakpoint()
                answer = self.implement(next_node)
                break
        if not answer:
            self.modules['actions_queue'].add_action(Action(ActionType.SendMessage, TemplatesHandler.substitute(f"Default answer on '{text}'", self.runtime_vars)))

    def add_to_own_will(self, story_id):
        self.robins_story_ids.append(story_id)

    def add_story_by_source(self, source):
        new_stories = RSParser.create_from_text(source)
        # TODO: handle dublicates
        # for s in new_stories:
        #     if s.name in
        self.stories.extend(new_stories)
        self.story_ids.extend([s.name for s in new_stories])

    def force_own_will_story(self):
        log.debug("force_own_will_story")
        if self.robins_story_ids:
            s = self.robins_story_ids.pop(0)
            if s is not None:
                log.debug(f"Story: {s}")
                self.force_story(s)
            else:
                log.debug(f"No story to be forcely called")

    async def start_silence(self):
        log.debug("Silence detection started")
        while self.handle_silence and self.modules['messages'].websockets:
            log.debug(f"Waiting silence for {self.silence_time} seconds")
            await asyncio.sleep(self.silence_time)
            log.debug("Silence detected")
            if self.robins_story_ids:
                self.force_own_will_story()

    def init_silence(self):
        if not self.handle_silence:
            return
        if self.silence_task is not None:
            self.silence_task.cancel()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop is None or not (loop.is_running()):
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

    def force_say(self, text):
        self.history.append(self.to_canonical(text))
        self.modules['messages'].say(text)

    def force_story(self, story_id):
        # FIXME:whole func
        if not self.modules['messages'].websockets:
            return
        log.debug(f"Make to start the story: {story_id}")
        stories = [i for i in self.stories if i.name == story_id]
        if len(stories) > 0:
            st = stories[0]
            if story_id and st:
                # TODO: parse any nodes
                self.implement(st.first_node)
        else:
            log.debug(f"No story with such name: {story_id}")
