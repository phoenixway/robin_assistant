# from nltk import word_tokenize
# from nltk.corpus import stopwords
import re, os, sys, datetime
import json
sys.path.append(os.getcwd())
import actions.default
from pathlib import Path

# intents = {}
# intents[r"(hello|hey|hi|(good day))"] = "greetings"
# intents[r"i planned day"] = "i_planned_day"
# intents[r"(bye|exit|(quit))"] = "bye"

def recognize_intent(text):
    for intent in intents:
        text = text.lower()
        m = re.search(intent, text)
        if m is not None:
            return intents[intent]

# story1 = ["greetings", 'say_hello', "i_planned_day", 'you_planned_day']
# story2 = ["bye", 'say_bye']
# stories = []
# stories.append(story1)
# stories.append(story2)

# #TODO: load from file
# with open('brains/default.stories', 'w') as f:
#     json.dump(stories, f)

# with open('brains/default.intents', 'w') as f:
#     json.dump(intents, f)

source_path = Path(__file__).resolve()
source_dir = source_path.parent

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

class AICore:
    def __init__(self, modules):
        self.modules = modules
        self.active_story = None
        self.log = []

    def parse(self, text):
        answer = f"Default answer on '{text}'"
        try:
            intent = recognize_intent(text)
            self.log.append(intent)
            if intent:
                for story in stories:
                    is_active_story, pos = is_story_in_log(story, self.log)    
                    if is_active_story:
                        fn_name = story[pos]
                        fn = getattr(actions.default, fn_name)
                        #TODO: get rid of sending modules each time fn calls
                        answer = fn(self.modules)
                        self.log.append(fn_name)
                        break
        except:
            answer = "Error happened!"
        return answer