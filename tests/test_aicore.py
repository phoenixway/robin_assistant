from .. import ai_core
# from ai_core import contains_in_end, AICore, story
from ..actions import default


def test_contains_in_end():
    l1 = ['a', 'b', 'c', 'd', 'e']
    l2 = ['d', 'e']
    l3 = ['c', 'e']
    res = ai_core.contains_in_end(l2, l1)
    assert res == True, 'contains_in_end must be True'
    res = ai_core.contains_in_end(l3, l1)
    assert res == False, 'contains_in_end must be False'

def test_aicore():
    ac = ai_core.AICore(None)
    ac.log = ["greetings", 'say_hello', "i_planned_day"]
    res = ai_core.is_story_in_log(ai_core.story, ac.log)
    assert res[0] == True, "is_story_in_log error"
