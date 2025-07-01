#!/usr/bin/env python3
"""
Test SLY parser to understand the correct syntax
"""

from sly import Lexer, Parser

class TestLexer(Lexer):
    tokens = { 'NUM', 'PLUS' }
    
    NUM = r'\d+'
    PLUS = r'\+'
    ignore = ' \t'

class TestParser(Parser):
    tokens = TestLexer.tokens
    
    @_('NUM PLUS NUM')
    def expr(self, p):
        return p.NUM0 + p.NUM1

if __name__ == "__main__":
    lexer = TestLexer()
    parser = TestParser()
    
    result = parser.parse(lexer.tokenize("1 + 2"))
    print(f"Result: {result}")
