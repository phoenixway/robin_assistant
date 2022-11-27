#!/usr/bin/env python3

from parsimonious.grammar import Grammar
from .visitor import RSVisitor


class RSParser:
    # TODO: прибрати зайве
    rs_grammar = Grammar(r"""
        stories = story+
        story = maybe_ws story_start_keyword maybe_ws maybe_story_name maybe_ws block maybe_ws  # noqa: E501
        story_start_keyword = ~r"story"
        story_ends_keyword = ~r"story_ends"
        maybe_story_name = story_name*
        story_name = ~r"[\w_\d]+"
        statement = (if_in_statement / oneliner / fn_statement)
        if_in_statement = maybe_ws if_in_start maybe_ws if_in_variant_must maybe_ws if_end maybe_ws
        if_in_start = ~r'<if input>'
        if_end = ~r'</if>'
        if_in_variant_must = if_in_variant+
        if_in_variant = maybe_ws parameter maybe_ws then_keyword maybe_ws if_in_variant_block
        then_keyword = ~r"=>"
        block = lbr maybe_ws maybe_statements maybe_ws rbr
        if_in_variant_block = lbr maybe_ws maybe_statements maybe_ws rbr
        rbr = ~r"\}"
        lbr = ~r"\{"
        oneliner = inout ws_must text
        inout = ~r"[<>]"
        text = (intent_text / simple_text)
        fn_statement = maybe_ws fn_start code fn_end maybe_ws
        fn_start = ~r'<fn>'
        fn_end = ~r'</fn>'
        code = ~r"[\w\s\d\(\)\{\}\[\]\;\,\.\"\'\~\?\n\!\=/\+\-\*\:_\&#\%]+"
        intent_text = maybe_intent_keyword raw_text
        simple_text = raw_text
        parameter = (intent_parameter / simple_parameter)
        simple_parameter = raw_text
        intent_parameter = maybe_intent_keyword raw_text
        raw_text = ~r"[-\w\s\?\!\.\,\d\'\`]+"
        ws = ~r"\s"
        intent_keyword = ~r"<intent>"
        maybe_ws = ws*
        ws_must = ws+
        maybe_intent_keyword = intent_keyword+
        maybe_statements = statement*
    """)

    def create_from_text(text):
        res = RSParser.rs_grammar.parse(text)
        v = RSVisitor()
        ret = v.visit(res)
        return ret
