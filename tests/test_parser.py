import pytest

from pinterpret.ast import LetStatement, ReturnStatement, ExpressionStatement, Identifier
from pinterpret.lexer import Lexer
from pinterpret.parser import Parser
from pinterpret.token import TokenType
from tests.consts import SOURCE_CODE_TEST_004


@pytest.mark.parametrize('test_input,expected_identifiers,expected_types', [
    (
            SOURCE_CODE_TEST_004,
            ['x', '', ''],
            [TokenType.LET, TokenType.RETURN, TokenType.RETURN]
    )
])
def test_parse_let_and_return_statements(test_input, expected_identifiers, expected_types):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert program.statements is not None

    assert len(program.statements) == len(expected_identifiers)

    for i, (stmt, identifier, type) in enumerate(zip(program.statements, expected_identifiers, expected_types)):
        if isinstance(stmt, LetStatement):
            assert stmt.token.type == type
            assert stmt.name.token_literal() == identifier
        elif isinstance(stmt, ReturnStatement):
            assert stmt.token.type == type
        else:
            assert False, f"{i}th stmt fails to match"


@pytest.mark.parametrize('test_input,expected_message', [
    (
            "let x  3;", ''
    ),
    (
            "let  = 3;", ''
    ),
    (
            "let  = ;", ''
    ),
    (
            "let x = 3", ''
    )
])
def test_parse_wrong_let_statements(test_input, expected_message):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert parser.errors


@pytest.mark.parametrize('test_input,expected', [
    ('foobar;', 'foobar'),
    ('baby;', 'baby'),
    ('5;', '5'),
    ('7;', '7'),
])
def test_parse_single_line_expression_statement(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    identifier: Identifier = stmt.expression
    assert identifier.value == expected
