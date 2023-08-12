#!/usr/bin/env python3
import logging
from parsimonious.grammar import Grammar
from parsimonious.exceptions import ParseError
from .visitor import RSVisitor


log = logging.getLogger('pythonConfig')

#        oneliner_with_params = inout ws_must maybe_raw_text input_var maybe_raw_text


grammar_new = r"""
        stories = story+
        story = maybe_ws story_start_keyword maybe_ws maybe_story_name maybe_ws block maybe_ws  # noqa: E501
        story_start_keyword = ~r"story"
        story_ends_keyword = ~r"story_ends"
        maybe_story_name = story_name*
        story_name = ~r"[\w_\d]+"
        statement = (if_statement / if_in_statement / oneliner_with_params / fn_statement / oneliner)
        fn_statement = maybe_ws code maybe_ws
        code = ~r"(<fn>)([\w\W]+?)(<\/fn>)"m
        if_in_statement = maybe_ws if_in_start maybe_ws if_in_variant_must maybe_ws if_end maybe_ws
        if_in_start = ~r'<if in>'
        if_end = ~r'</if in>'
        if_in_variant_must = if_in_variant+
        if_in_variant = maybe_ws parameter maybe_ws then_keyword maybe_ws if_in_variant_block
        then_keyword = ~r"=>"
        block = lbr maybe_ws maybe_statements maybe_ws rbr
        if_in_variant_block = lbr maybe_ws maybe_statements maybe_ws rbr
        if_statement = maybe_ws if_tag maybe_ws then_part maybe_ws maybe_elif_substatements maybe_ws maybe_else_part maybe_ws
        if_tag = ~r"(<if>)([\w\W]+)(</if>)"
        then_part = (statement / block)
        maybe_else_part = else_substatement?
        else_substatement = else_keyword maybe_ws then_part
        else_keyword = ~r'<else>'
        elif_tag =  ~r"(<elif>)([\w\W]+)(</elif>)"
        elif_substatement = elif_tag maybe_ws then_part
        maybe_elif_substatements = elif_substatement*
        rbr = ~r"\}"
        lbr = ~r"\{"
        oneliner = inout ws_must text
        oneliner_with_params = (oneliner_with_vars / random_input)
        oneliner_with_vars = inout ws_must maybe_text input_var maybe_text
        random_input = maybe_ws random_symbols maybe_ws
        random_symbols = ~r"< \*"
        input_var = ~r"%\w"
        maybe_text = text*
        inout = ~r"[<>]"
        text = (intent_text / simple_text)
        intent_text = maybe_intent_keyword raw_text
        simple_text = raw_text
        parameter = (intent_parameter / simple_parameter)
        simple_parameter = raw_text
        intent_parameter = maybe_intent_keyword raw_text
        raw_text = ~r"[-\w\s\?\!\.\,\d\'\`$]+"
        ws = ~r"\s"
        intent_keyword = ~r"<intent>"
        maybe_ws = ws*
        ws_must = ws+
        maybe_intent_keyword = intent_keyword+
        maybe_statements = statement*
    """
# (<fn>)([\w\W]+)(</fn>)
grammar_old = r"""
        stories = story+
        story = maybe_ws story_start_keyword maybe_ws maybe_story_name maybe_ws block maybe_ws  # noqa: E501
        story_start_keyword = ~r"story"
        story_ends_keyword = ~r"story_ends"
        maybe_story_name = story_name*
        story_name = ~r"[\w_\d]+"
        statement = (if_statement / if_in_statement / oneliner_with_params / fn_statement / oneliner)
        if_in_statement = maybe_ws if_in_start maybe_ws if_in_variant_must maybe_ws if_end maybe_ws
        if_in_start = ~r'<if in>'
        if_end = ~r'</if>'
        if_in_variant_must = if_in_variant+
        if_in_variant = maybe_ws parameter maybe_ws then_keyword maybe_ws if_in_variant_block
        then_keyword = ~r"=>"
        block = lbr maybe_ws maybe_statements maybe_ws rbr
        if_in_variant_block = lbr maybe_ws maybe_statements maybe_ws rbr
        if_statement = maybe_ws if_tag maybe_ws then_part maybe_ws maybe_elif_substatements maybe_ws maybe_else_part maybe_ws
        if_tag = if_start_keyword ws_must if_condition maybe_ws if_start_end_keyword
        if_start_keyword = ~r'<if'
        if_start_end_keyword = ~r'>'
        if_condition = code
        then_part = (statement / block)
        maybe_else_part = else_substatement?
        else_substatement = else_keyword maybe_ws then_part
        else_keyword = ~r'<else>'
        elif_keyword = ~r'<elif '
        elif_tag = elif_keyword code close_tag_symbol
        elif_substatement = elif_tag maybe_ws then_part
        maybe_elif_substatements = elif_substatement*
        rbr = ~r"\}"
        lbr = ~r"\{"
        oneliner = inout ws_must text
        oneliner_with_params = (oneliner_with_vars / random_input)
        oneliner_with_vars = inout ws_must maybe_text input_var maybe_text
        random_input = maybe_ws random_symbols maybe_ws
        random_symbols = ~r"< \*"
        input_var = ~r"%\w"
        maybe_text = text*
        inout = ~r"[<>]"
        text = (intent_text / simple_text)
        fn_statement = maybe_ws fn_start code fn_end maybe_ws
        code = ~r"[\w\s\d\(\)\{\}\[\]\;\,\.\"\'\~\?\n<\!\=/\+\-\*\:_\&#\%]+"
        intent_text = maybe_intent_keyword raw_text
        simple_text = raw_text
        parameter = (intent_parameter / simple_parameter)
        simple_parameter = raw_text
        intent_parameter = maybe_intent_keyword raw_text
        raw_text = ~r"[-\w\s\?\!\.\,\d\'\`$]+"
        ws = ~r"\s"
        intent_keyword = ~r"<intent>"
        inline_fn = inline_fn_tag_start code close_tag_symbol
        inline_fn_tag_start = ~r"<f "
        maybe_inline_fn = inline_fn?
        maybe_var_name = var_name*
        var_name = ~r"[\w\s_\d]+"
        close_tag_symbol = ~r">"
        maybe_ws = ws*
        ws_must = ws+
        maybe_intent_keyword = intent_keyword+
        maybe_statements = statement*
        fn_start = ~r'<fn>'
        fn_end = ~r'</fn>'
    """


class RSParser:
    # TODO: прибрати зайве
    # noqa: E501
    rs_grammar = Grammar(grammar_new)

    def create_from_text(text):
        try:
            res = RSParser.rs_grammar.parse(text)
            v = RSVisitor()
            res = v.visit(res)
            return res
        except ParseError as e:
            log.error(f"Stories parsing error: {e}")
        except Exception as e:
            log.error(f"Visiting stories error: {e}")
