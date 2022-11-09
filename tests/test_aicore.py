from .. import ai_core
import ai_core
from ai_core import contains_in_end, AICore
from ..actions import default
import copy
from pprint import pprint

def test_aicore():
    ai_core.init_brains()
    aicore = AICore(None)
    assert len(ai_core.stories_) > 0, 'There should be at least one story'
    s = ai_core.stories_.get('trees', None)
    assert s is not None, 'cant access to trees story'
    l = ["Do u know yr main priorities for today?", "<intent>yes"]
    assert isinstance(ai_core.stories_['trees'], list), 'stories[tree] exception'
    assert aicore is not None, 'aicore creation failed'


def test_make_canonical_simple():
    lst = ['a0', 'a1', 'b2', 'a3', 'b4']
    res, is_collection = ai_core.make_canonical(lst)
    assert is_collection == False, 'must be not a collection'
    assert len(res) == 5, 'fail'
    needed = ['a0', 'a1', 'b2', 'a3', 'b4']
    result = all(r == n for r, n in zip(res, needed))
    assert result, 'fail'

def test_make_canonical_1():
    lst = ['a1', 'a2', {'a3': 'b4', 'a5': 'b6'}, 'b7', 'a8']
    res, are_branches = ai_core.make_canonical(lst)
    assert are_branches == True, 'Branches must be true'
    assert len(res) == 2, 'len error'
    needed = ['a1', 'a2', 'a3', 'b4', 'b7', 'a8']
    result = all(r == n for r, n in zip(res[0], needed))
    assert result, '1 list is wrong'
    needed = ['a1', 'a2', 'a5', 'b6', 'b7', 'a8']
    result = all(r == n for r, n in zip(res[1], needed))
    assert result, '2 list is wrong'

def test_make_canonical_2():
    lst = ['a1', 'a2', {'a3': ['b4', 'a41', 'b42'], 'a5': 'b6'}, 'b7', 'a8']
    res, are_branches = ai_core.make_canonical(lst)
    assert are_branches == True, 'Branches must be true'
    assert len(res) == 2, 'len error'
    needed = ['a1', 'a2', 'a3', 'b4', 'a41', 'b42', 'b7', 'a8']
    result = all(r == n for r, n in zip(res[0], needed))
    assert result, '1 list is wrong'
    needed = ['a1', 'a2', 'a5', 'b6', 'b7', 'a8']
    result = all(r == n for r, n in zip(res[1], needed))
    assert result, '2 list is wrong'

def test_make_canonical_3():
    lst = ['a1', 'a2', {'a3': ['b4', {'a41': 'b42', 'a51': 'b52'}], 'a5': 'b6'}, 'b7', 'a8']
    res, are_branches = ai_core.make_canonical(lst)
    assert are_branches == True, 'Branches must be true'
    assert len(res) == 3, 'len error'
    needed = ['a1', 'a2', 'a3', 'b4', 'a41', 'b42', 'b7', 'a8']
    result = all(r == n for r, n in zip(res[0], needed))
    assert result, '1 list is wrong'
    needed = ['a1', 'a2', 'a3', 'b4', 'a51', 'b52', 'b7', 'a8']
    result = all(r == n for r, n in zip(res[1], needed))
    assert result, '1 list is wrong'
    needed = ['a1', 'a2', 'a5', 'b6', 'b7', 'a8']
    result = all(r == n for r, n in zip(res[2], needed))
    assert result, '3 list is wrong'

# def test_make_canonical_hard1():
#     lst = ['in1', 'out2', 'in3', 'out4', [
#         ['in5', 'out6'], ['ii1', 'oo2']], 'in9', 'out10']
#     res, is_collection = ai_core.make_canonical(lst)
#     assert is_collection == True, 'not collection althrough it must be'
#     assert len(res) == 2, 'fail'
#     needed = ['in1', 'out2', 'in3', 'out4', 'in5', 'out6', 'in9', 'out10']
#     result = all(r == n for r, n in zip(res[0], needed))
#     assert result, 'first list is wrong'
#     needed = 'in1', 'out2', 'in3', 'out4', 'ii1', 'oo2', 'in9', 'out10'
#     result = all(r == n for r, n in zip(res[1], needed))
#     assert result, 'second list is wrong'
# def test_make_canonical_hard2():
#     lst = ['in1', 'out2', 'in3', 'out4', [
#         ['in5', 'out6', [['f1', 'f2'], ['f3', 'f4']]], 
#         ['ii1', 'oo2']
#     ], 'in9', 'out10']
#     res, is_collection = ai_core.make_canonical(lst)
#     assert is_collection == True, 'not collection althrough it must be'
#     assert len(res) == 2, 'fail'
#     needed = ['in1', 'out2', 'in3', 'out4',
#               'in5', 'out6', 'f1', 'f2', 'in9', 'out10']
#     result = all(r == n for r, n in zip(res[0], needed))
#     assert result, 'first list is wrong'
#     needed = ['in1', 'out2', 'in3', 'out4',
#               'in5', 'out6', 'f3', 'f4', 'in9', 'out10']
#     result = all(r == n for r, n in zip(res[1], needed))
#     assert result, 'second list is wrong'

def test_canonize():
    aicore = AICore(None)
    s = ai_core.stories_['trees']
    assert s is not None, 'no story'
    res = AICore.canonize({'trees': s})
    pprint(res)
    assert res is not None, 'no canonized stories'
    assert len(res) == 3, 'expected 3 canonized stories'
    key = (list(res.keys()))[0]
    assert res[key]

def test_story_in_log_simple():
    aicore = AICore(None)
    s = aicore.stories['greetings']
    assert s is not None, 'no story'
    log = ['<intent>greetings']
    res, i = ai_core.is_story_in_log(s, log)
    assert res == True, 'story is not in log'
    assert i == 1, 'wrong next statement index'

def test_parse():
    aicore = AICore(None)
    s = aicore.get_story('trees')
    assert s is not None, 'no story'
    l = ["Do u know yr main priorities for today?", "<intent>yes"]
    assert isinstance(s, list), 'stories[tree] exception'
    assert aicore is not None, 'aicore creation failed'
    assert aicore.stories is not None, 'stories creation failed'
    text = 'Hey'
    res = aicore.respond(text)
    assert res is not None, 'parse exception'
