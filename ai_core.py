# from nltk import word_tokenize
# from nltk.corpus import stopwords
import asyncio
from copy import deepcopy
import logging
import re, os, sys
import json
sys.path.append(os.getcwd())
import actions.default
from pathlib import Path

log = logging.getLogger('pythonConfig')
source_path = Path(__file__).resolve()
source_dir = source_path.parent
stories_ = {}
intents = []

def recognize_intent(text):
    for intent in intents:
        text = text.lower()
        m = re.match(intent, text)
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
    global stories_
    global intents
    with open(source_dir/'brains/default.stories', 'r') as f:
        stories_ = json.load(f)
    with open(source_dir/'brains/default.intents', 'r') as f:
        intents = json.load(f)

def way_to_beginning(lst, val):
    result = []
    cur_way = []
    cur_ways = []
    done = False
    is_collection = False
    for s in lst:
        if done:
            break
        if isinstance(s, str):
            if len(cur_ways) > 0:
                cur_ways = [cw + [s] for cw in cur_ways ]
            else:
                cur_way.append(s)
            if s == val:
                print('found!')
                if len(cur_ways) > 0:
                    # for cw in cur_ways:
                    #     cw.extend(cur_way)
                    result = cur_ways
                    is_collection = True
                else:
                    result = cur_way    
                    is_collection = False            
                break
        elif isinstance(s, list) and not any(isinstance(item, str) for item in s):
            for l1 in s:
                base = cur_way
                res, aaaa = way_to_beginning(l1, val)
                if len(res) > 0:
                    cur_way.extend(res)
                    result = cur_way
                    done = True
                    break
                else:
                    ll = deepcopy(base)
                    ll.extend(l1)
                    cur_ways.append(ll)
                        
    return result, is_collection
    
def make_canonical(data):
    linear_way = []
    ways = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                if len(ways) > 0:
                    for w in ways:
                        w.append(item)
                else:
                    linear_way.append(item)
            elif isinstance(item, dict):
                branches, _ = make_canonical(item)
                for b in branches:
                    lw = deepcopy(linear_way)
                    lw.extend(b)
                    ways.append(lw)
    elif isinstance(data, dict):
        branches = []
        for item in data:
            if isinstance(data[item], list):
                ##what if branches
                l, are_branches = make_canonical(data[item])
                if are_branches:
                    for it in l:
                        branches.append([item] + it)
                else:
                    branches.append([item] + l)
            elif isinstance(data[item], str):
                branches.append([item, data[item]])
        return branches, True
                
    if len(ways) > 0:
        return ways, True
    else:
        return linear_way, False

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
    # key = (story.keys())[0]
    # way, is_collection = story[key], True
    way, is_collection = way_to_beginning(story, l[-1])
    if len(way) == 0:
        return result
    if not is_collection:
        story = way
    if len(l) > len(story):
        i = len(story)
        while i >= 0:
            if contains_in_end(story[0:i], l):
                return True, i
            # elif contains_in_end(story[0:i], l):
            #     return True, i
            i = i - 1
    elif len(l) <= len(story):
        i = len(l)
        while i >= 0:
            if contains_in_end(story[0:i], l):
                return True, i
            i = i - 1
    return result

SILENCE_TIME = 10

class AICore:
    def canonize(stories):
        final = {}
        for s in stories:
            story_body = stories[s]
            branches, has_branches = make_canonical(story_body)
            if has_branches:
                i = 0
                
                for b in branches:
                    final[f"{s}::{i}"] = b
                    i = i + 1
            else:
                final[s] = stories[s]
        return final

    def __init__(self, modules):
        # create_default_stories()
        #TODO: check that brains exist
        init_brains()
        self.stories = AICore.canonize(stories_)
        self.modules = modules
        self.active_story = None
        self.log = []
        if modules is not None:
            modules['events'].add_listener('message_received', self.message_received_handler)
        self.silence_task = None
        self.is_started = True
        self.repeat_if_silence = False
        self.robins_stories = ['trees::0']

    def get_story(self, key):
        s = self.stories.get(key, None)
        if s is None:
            keys = self.stories.keys()
            key2 = [k for k in keys if k.startswith(key)]
            s = self.stories[key2[0]]
        return s 


    async def wait_to_talk(self, s):
        await asyncio.sleep(SILENCE_TIME)
        self.start_story(s)
        while self.repeat_if_silence:
            await asyncio.sleep(SILENCE_TIME)
            if self.robins_stories:
                s = self.robins_stories.pop()
                if s is not None:
                    self.start_story(s)

    async def message_received_handler(self, data):
        log.debug('message received handler')
        if self.robins_stories:
            s = self.robins_stories.pop()
            if s is not None:
                if self.silence_task is not None:
                    self.silence_task.cancel()
                self.silence_task = asyncio.create_task(self.wait_to_talk(s))
        # asyncio.run(self.silence_task)

    def parse(self, text):
        log.debug("Parsing with aicore")
        answer = f"Default answer on '{text}'"
        try:
            intent = recognize_intent(text)
            if intent is not None:
                self.log.append(f"<intent>{intent}")
            else:
                self.log.append(text)
            #FIXME: take any input
            if intent:
                for story_id in self.stories:
                    is_active_story, pos = is_story_in_log(self.stories[story_id], self.log)    
                    if is_active_story:
                        ##FIXME
                        next_answer = self.stories[story_id][pos]
                        if next_answer.startswith('<func>'):
                            fn_name = (self.stories[story_id][pos])[6:]
                            fn = getattr(actions.default, fn_name)
                            #TODO: get rid of sending modules each time fn calls
                            answer = fn(self.modules)
                            self.log.append(next_answer)
                        else:
                            answer = next_answer
                            self.log.append(next_answer)
                        break
            else:
                for story_id in self.stories:
                    is_active_story, pos = is_story_in_log(self.stories[story_id], self.log)    
                    if is_active_story:
                        ##FIXME
                        next_answer = self.stories[story_id][pos]
                        if next_answer.startswith('<func>'):
                            fn_name = (self.stories[story_id][pos])[6:]
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
        if story_id in self.stories and len(self.stories[story_id]) > 0:
            next_answer = self.stories[story_id][0]
            if next_answer.startswith('<func>'):
                fn_name = (self.stories[story_id][0])[6:]
                fn = getattr(actions.default, fn_name)
                #TODO: get rid of sending modules each time fn calls
                answer = fn(self.modules)
                self.log.append(next_answer)
            else:
                answer = next_answer
                self.log.append(next_answer)
            self.modules['messages'].say(answer)
