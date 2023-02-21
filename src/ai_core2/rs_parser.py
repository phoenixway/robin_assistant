#!/usr/bin/env python3

from parsimonious.grammar import Grammar
from .visitor import RSVisitor

rs_grammar_old = Grammar(r"""
        stories = story+
        story = maybe_ws story_start_keyword maybe_ws maybe_story_name maybe_ws block maybe_ws  # noqa: E501
        story_start_keyword = ~r"story"
        story_ends_keyword = ~r"story_ends"
        maybe_story_name = story_name*
        story_name = ~r"[\w_\d]+"
        statement = (if_statement / if_in_statement / oneliner / fn_statement / oneliner_with_params)
        if_in_statement = maybe_ws if_in_start maybe_ws if_in_variant_must maybe_ws if_end maybe_ws
        if_in_start = ~r'<if in>'
        if_end = ~r'</if>'
        if_in_variant_must = if_in_variant+
        if_in_variant = maybe_ws parameter maybe_ws then_keyword maybe_ws if_in_variant_block
        then_keyword = ~r"=>"
        block = lbr maybe_ws maybe_statements maybe_ws rbr
        if_in_variant_block = lbr maybe_ws maybe_statements maybe_ws rbr
        if_statement = maybe_ws if_start maybe_ws if_block maybe_ws maybe_else_part maybe_ws if_end maybe_ws
        if_start = if_start_keyword ws_must if_condition maybe_ws if_start_end_keyword
        if_start_keyword = ~r'<if'
        if_start_end_keyword = ~r'>'
        if_condition = raw_text
        maybe_else_part = else_part?
        else_part = else_keyword maybe_ws if_block
        else_keyword = ~r'<else>'
        if_block = statement+
        rbr = ~r"\}"
        lbr = ~r"\{"
        oneliner = inout ws_must text
        oneliner_with_params = variable
        text_with_params = raw_text_or_variable_with_spaces+
        raw_text_or_variable_with_spaces = maybe_ws raw_text_or_variable maybe_ws
        raw_text_or_variable = (raw_text / variable)
        variable = let_keyword_open let_keyword_close 
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
        let_keyword_open = ~r"<let>"
        let_keyword_close = ~r"</let>"
        maybe_var_name = var_name*
        var_name = ~r"[\w\s_\d]+" 
        maybe_ws = ws*
        ws_must = ws+
        maybe_intent_keyword = intent_keyword+
        maybe_statements = statement*
    """)

class RSParser:
    # TODO: прибрати зайве
    # noqa: E501
    rs_grammar = Grammar(r"""
        stories = story+
        story = maybe_ws story_start_keyword maybe_ws maybe_story_name maybe_ws block maybe_ws  # noqa: E501
        story_start_keyword = ~r"story"
        maybe_story_name = story_name*
        story_name = ~r"[\w_\d]+"
        block = lbr maybe_ws maybe_statements maybe_ws rbr
        rbr = ~r"\}"
        lbr = ~r"\{"
        statement = (oneliner_with_params / oneliner)
        oneliner_with_params = inout ws_must text_with_params
        text_with_params = text_with_param+
        text_with_param = many_raw_text variable many_raw_text
        many_raw_text = raw_text*
        oneliner = inout ws_must text
        variable = let_keyword_open maybe_ws let_keyword_close maybe_ws
        inout = ~r"[<>]"
        text = (intent_text / simple_text)
        intent_text = maybe_intent_keyword raw_text
        simple_text = raw_text
        parameter = (intent_parameter / simple_parameter)
        simple_parameter = raw_text
        intent_parameter = maybe_intent_keyword raw_text
        raw_text = ~r"[-\w\s\?\!\.\,\d\'\`]+"
        ws = ~r"\s"
        intent_keyword = ~r"<intent>"
        let_keyword_open = ~r"<let>"
        let_keyword_close = ~r"</let>"
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
