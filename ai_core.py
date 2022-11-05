# from nltk import word_tokenize
# from nltk.corpus import stopwords
import asyncio
import logging
import re, os, sys
import json
sys.path.append(os.getcwd())
import actions.default
from pathlib import Path

log = logging.getLogger('pythonConfig')
source_path = Path(__file__).resolve()
source_dir = source_path.parent
stories = {}
intents = []

def recognize_intent(text):
    for intent in intents:
        text = text.lower()
        m = re.search(intent, text)
        if m is not None:
            return intents[intent]

def create_default_stories():
    s = {}
    s['greetings'] = ("<intent>greetings", "<func>say_hello", "<intent>i_planned_day", "You planned your day, congratulations!")
    s['goodbye'] = ("<intent>bye", "<func>say_bye")
    s['cursing'] = ("<intent>cursing","<func>answer_cursing")
    with open(source_dir/'brains/default.stories', 'w') as f:
        json.dump(s, f, sort_keys=True, indent=4)

def init_brains():
    global stories
    global intents
    with open(source_dir/'brains/default.stories', 'r') as f:
        stories = json.load(f)

    with open(source_dir/'brains/default.intents', 'r') as f:
        intents = json.load(f)

#TODO: study it
def contains(subseq, inseq):
    return any(inseq[pos:pos + len(subseq)] == subseq for pos in range(0, len(inseq) - len(subseq) + 1))

def contains_in_end(subseq, inseq):
    if len(subseq) == 0:
        return False
    for i in range(len(subseq)):
        if subseq[i] != inseq[len(inseq) - len(subseq) + i]:
            return False
    return True

def is_story_in_log(story, l):
    result = False, -1
    if len(l) > len(story):
        i = len(story)
        while i >= 0:
            if contains_in_end(story[0:i], l):
                return True, i
            i = i - 1
    elif len(l) < len(story):
        i = len(l)
        while i >= 0:
            if contains_in_end(story[0:i], l):
                return True, i
            i = i - 1
    return result


SILENCE_TIME = 10

class AICore:
    def __init__(self, modules):
        # create_default_stories()
        #TODO: check that brains exist
        init_brains()
        self.modules = modules
        self.active_story = None
        self.log = []
        modules['events'].add_listener('message_received', self.message_received_handler)
        self.silence_task = None
        self.is_started = True

    async def wait_to_talk(self):
        while True:
            await asyncio.sleep(SILENCE_TIME)
            self.start_story('robin_asks')

    async def message_received_handler(self, data):
        log.debug('message received handler')
        if self.silence_task is not None:
            self.silence_task.cancel()
        self.silence_task = asyncio.create_task(self.wait_to_talk())
        # asyncio.run(self.silence_task)

    def parse(self, text):
        log.debug("Parsing with aicore")
        answer = f"Default answer on '{text}'"
        try:
            intent = recognize_intent(text)
            self.log.append(f"<intent>{intent}")
            if intent:
                for story_id in stories:
                    is_active_story, pos = is_story_in_log(stories[story_id], self.log)    
                    if is_active_story:
                        next_answer = stories[story_id][pos]
                        if next_answer.startswith('<func>'):
                            fn_name = (stories[story_id][pos])[6:]
                            fn = getattr(actions.default, fn_name)
                            #TODO: get rid of sending modules each time fn calls
                            answer = fn(self.modules)
                            self.log.append(next_answer)
                        else:
                            answer = next_answer
                            self.log.append(next_answer)
                        break
        except Exception as e:
            answer = f"Error happened in ai_core.parse(): {e}"
        return answer

    def start_story(self, story_id):
        #FIXME:whole func
        log.debug("Make story start by Robin's will")
        if story_id in stories and len(stories[story_id]) > 0:
            next_answer = stories[story_id][0]
            if next_answer.startswith('<func>'):
                fn_name = (stories[story_id][0])[6:]
                fn = getattr(actions.default, fn_name)
                #TODO: get rid of sending modules each time fn calls
                answer = fn(self.modules)
                self.log.append(next_answer)
            else:
                answer = next_answer
                self.log.append(next_answer)
            self.modules['messages'].say(answer)
