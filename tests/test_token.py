import pytest

from pinterpret.token import Token, TokenType


@pytest.mark.parametrize('test_input,expected', [
    ('+', TokenType.PLUS),
    ('=', TokenType.ASSIGN),
    (",", TokenType.COMMA),
    (';', TokenType.SEMICOLON),
    ('(', TokenType.LPAREN),
    (')', TokenType.RPAREN),
    ('{', TokenType.LBRACE),
    ('}', TokenType.RBRACE),
])
def test_initialize_token(test_input, expected):
    assert Token(test_input).type == expected
