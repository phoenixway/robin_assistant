#!/usr/bin/env python3
from parsimonious.grammar import Grammar

from ..ai_core2.rs_parser import RSParser   # noqa: F403, F401
from ..ai_core2.ast_nodes import IfInNode, IfNode, NodeFactory, MessageOutNode, MessageInNode  # noqa: E501
from ..ai_core2.story import Story
from ..ai_core2.ai_core import AICore


def test_message_in_node():
    n = NodeFactory.create_node("< test text")
    assert isinstance(n, MessageInNode), "MessageInNode expected"
    assert AICore.node2answer(n) == "< test text", "Wrong answer"


def test_message_out_node():
    n = NodeFactory.create_node("> test text")
    assert isinstance(n, MessageOutNode), "MessageInNode expected"
    assert AICore.node2answer(n) == "> test text", "Wrong answer"


def test_if_node():
    n = IfNode()
    n.condition = "True"
    n.first_in_if_block = NodeFactory.create_node("> if True block")
    n.first_in_else_block = NodeFactory.create_node("> else block")
    assert AICore.node2answer(n) == "> if True block", "Wrong answer"


def test_if_in_node():
    n = IfInNode()
    n = NodeFactory.create_node("< test text")
    assert isinstance(n, MessageInNode), "MessageInNode expected"
    assert AICore.node2answer(n) == "< test text", "Wrong answer"