import pytest

from pinterpret.lexer import Lexer
from pinterpret.token import TokenType
from tests.consts import SOURCE_CODE_TEST_001, SOURCE_CODE_TEST_002


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            "=,;{}()",
            [
                TokenType.ASSIGN,
                TokenType.COMMA,
                TokenType.SEMICOLON,
                TokenType.LBRACE,
                TokenType.RBRACE,
                TokenType.LPAREN,
                TokenType.RPAREN,
            ],
        ),
        (
            "let five = 5;",
            [
                TokenType.LET,
                TokenType.IDENT,
                TokenType.ASSIGN,
                TokenType.INT,
                TokenType.SEMICOLON,
            ],
        ),
        (
            SOURCE_CODE_TEST_001,
            [
                TokenType.LET,
                TokenType.IDENT,
                TokenType.ASSIGN,
                TokenType.INT,
                TokenType.SEMICOLON,
                TokenType.LET,
                TokenType.IDENT,
                TokenType.ASSIGN,
                TokenType.INT,
                TokenType.SEMICOLON,
                TokenType.LET,
                TokenType.IDENT,
                TokenType.ASSIGN,
                TokenType.FUNCTION,
                TokenType.LPAREN,
                TokenType.IDENT,
                TokenType.COMMA,
                TokenType.IDENT,
                TokenType.RPAREN,
                TokenType.LBRACE,
                TokenType.IDENT,
                TokenType.PLUS,
                TokenType.IDENT,
                TokenType.SEMICOLON,
                TokenType.RBRACE,
                TokenType.SEMICOLON,
            ],
        ),
        (
            SOURCE_CODE_TEST_002,
            [
                TokenType.INT,
                TokenType.EQUAL,
                TokenType.INT,
                TokenType.SEMICOLON,
                TokenType.INT,
                TokenType.NOT_EQUAL,
                TokenType.INT,
                TokenType.SEMICOLON,
                TokenType.IF,
                TokenType.LPAREN,
                TokenType.INT,
                TokenType.LT,
                TokenType.INT,
                TokenType.RPAREN,
                TokenType.LBRACE,
                TokenType.RETURN,
                TokenType.TRUE,
                TokenType.SEMICOLON,
                TokenType.RBRACE,
                TokenType.ELSE,
                TokenType.LBRACE,
                TokenType.RETURN,
                TokenType.FALSE,
                TokenType.SEMICOLON,
                TokenType.RBRACE,
            ],
        ),
    ],
)
def test_token_type_of_read_tokens_is_correct(test_input, expected):
    lexer = Lexer(test_input)
    for i, e in enumerate(expected):
        token = lexer.next_token()
        assert token.type == e, f"{i}th token is failed"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            SOURCE_CODE_TEST_001,
            [
                "let",
                "five",
                "=",
                "5",
                ";",
                "let",
                "ten",
                "=",
                "10",
                ";",
                "let",
                "add",
                "=",
                "fn",
                "(",
                "x",
                ",",
                "y",
                ")",
                "{",
                "x",
                "+",
                "y",
                ";",
                "}",
                ";",
                "let",
                "result",
                "=",
                "add",
                "(",
                "five",
                ",",
                "ten",
                ")",
                ";",
            ],
        )
    ],
)
def test_token_literal_of_read_tokens_is_correct(test_input, expected):
    lexer = Lexer(test_input)
    for i, e in enumerate(expected):
        token = lexer.next_token()
        assert token.literal == e, f"{i}th token is failed"


@pytest.mark.parametrize(
    "test_input,expected", [("abc ", ["abc"]), ("ab1c ", ["ab1c"])]
)
def test_read_identifier(test_input, expected):
    lexer = Lexer(test_input)
    for e in expected:
        assert e == lexer.read_identifier()
