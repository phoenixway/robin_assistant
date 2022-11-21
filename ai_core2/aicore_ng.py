#!/usr/bin/env python3

import re
import asyncio
import logging
import os
import sys
import json
import actions.default
from pathlib import Path

from rs_parser import RSParser
from ast_nodes import IfNode, StringNode  # noqa: E501

sys.path.append(os.getcwd())

log = logging.getLogger('pythonConfig')
source_path = Path(__file__).resolve()
source_dir = source_path.parent
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
        self.robins_stories = ['robin_asks2::0']

    def next_in_story(log, story):
        n1 = story.first_node
        n = n1
        s = str(n1)
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
            elif isinstance(n, IfNode):
                if log[i][2:] not in n.variants:
                    return None
                else:
                    n = n.variants[log[i][2:]]
            i = i + 1
        return n

    def start_next_robin_story(self):
        log.debug("start_next_robin_story")
        # TODO: get rid of it
        if self.robins_stories:
            s = self.robins_stories.pop(0)
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
        # if self.silence_task is not None:
        #     self.silence_task.cancel()
        # self.silence_task = asyncio.create_task(self.do_silence())

    async def message_send_handler(self, data):
        log.debug('message send handler')
        # if self.silence_task is not None:
        #     self.silence_task.cancel()
        # self.silence_task = asyncio.create_task(self.do_silence())

    def respond(self, text):
        log.debug("Parsing with aicore")
        answer = None if text == '<silence>' else f"Default answer on '{text}'"
        try:
            intent = recognize_intent(text)
            if intent is not None:
                self.log.append(f"< <intent>{intent}")
            else:
                self.log.append("< " + text)
            # FIXME: take any input
            for story in self.stories:
                next = AICore.next_in_story(self.log, story)
                if next:
                    answer = next.text
                    self.log.append(answer)
                    if "> " in answer or "< " in answer:
                        answer = answer[2:]
                    break
        except Exception as e:
            answer = f"Error happened in ai_core.parse(): {e}"
        return answer

    def start_story(self, story_id):
        # FIXME:whole func
        log.debug("Make story start by Robin's will")
        if story_id in self.stories and len(self.stories[story_id]) > 0:
            next_answer = self.stories[story_id][0]
            if next_answer.startswith('<func>'):
                fn_name = (self.stories[story_id][0])[6:]
                fn = getattr(actions.default, fn_name)
                # TODO: get rid of sending modules each time fn calls
                answer = fn(self.modules)
                self.log.append(next_answer)
            else:
                answer = next_answer
                self.log.append(next_answer)
            self.modules['messages'].say(answer)