import pytest

from pinterpret.ast import (
    LetStatement, ReturnStatement, ExpressionStatement,
    Identifier, PrefixExpression, InfixExpression, IfExpression, FunctionLiteral, CallExpression
)
from pinterpret.lexer import Lexer
from pinterpret.parser import Parser
from pinterpret.token import TokenType
from tests.consts import SOURCE_CODE_TEST_004


@pytest.mark.parametrize('test_input,expected_identifiers,expected_types', [
    (
            SOURCE_CODE_TEST_004,
            ['x', '', ''],
            [TokenType.LET, TokenType.RETURN, TokenType.RETURN]
    ),
    (
            'let x = true;',
            ['x'],
            [TokenType.LET]
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
    ('true;', True),
    ('false;', False)
])
def test_parse_single_line_expression_statement(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    identifier: Identifier = stmt.expression
    assert identifier.value == expected


@pytest.mark.parametrize('test_input,expected', [
    ('!5;', ['!', '5']),
    ('-7;', ['-', '7']),
])
def test_parse_single_line_prefix_expression(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    identifier: PrefixExpression = stmt.expression
    assert identifier.operator == expected[0]
    assert identifier.right.token_literal() == expected[1]


@pytest.mark.parametrize('test_input,expected', [
    ('5 + 5;', ['5', '+', '5']),
    ('5 - 5;', ['5', '-', '5']),
    ('5 * 5;', ['5', '*', '5']),
    ('5 / 5;', ['5', '/', '5']),
    ('5 > 5;', ['5', '>', '5']),
    ('5 < 5;', ['5', '<', '5']),
    ('5 == 5;', ['5', '==', '5']),
    ('5 != 5;', ['5', '!=', '5']),
])
def test_parse_single_line_infix_expression(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    identifier: InfixExpression = stmt.expression
    assert identifier.left.token_literal() == expected[0]
    assert identifier.operator == expected[1]
    assert identifier.right.token_literal() == expected[2]


@pytest.mark.parametrize('test_input,expected', [
    ('a + b + c;', '((a+b)+c)'),
    ('a + b - c;', '((a+b)-c)'),
    ('a + b / c;', '(a+(b/c))'),
    ('a + b / c + d * e', '((a+(b/c))+(d*e))'),
    ('3 > 5 == false', '((3>5)==false)'),
    ('true == 3 < 5', '(true==(3<5))')
])
def test_parse_multiple_lines_infix_expression(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    assert str(stmt) == expected


@pytest.mark.parametrize('test_input,expected', [
    ('- 5 * (3 + 2);', '((-5)*(3+2))'),
    ('3 + (2 - 5) * 2;', '(3+((2-5)*2))'),
])
def test_parse_grouped_expression(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    assert str(stmt) == expected


@pytest.mark.parametrize('test_input,expected_cond,expected_consequence,expected_alternatives', [
    ('if (x<y) {y};', '(x<y)', 'y', None),
    ('if (x<y) {y} else {x}', '(x<y)', 'y', 'x'),
])
def test_parse_if_expression(test_input, expected_cond, expected_consequence, expected_alternatives):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    if_stmt: IfExpression = stmt.expression

    assert if_stmt.token.type == TokenType.IF
    assert str(if_stmt.condition) == expected_cond
    assert str(if_stmt.consequence) == expected_consequence
    assert str(if_stmt.alternative) == str(expected_alternatives)


@pytest.mark.parametrize('test_input,expected_parameters,expected_body', [
    ('fn (x,y,z) {x+y+z}', ['x', 'y', 'z'], '((x+y)+z)'),
])
def test_parse_function_literal(test_input, expected_parameters, expected_body):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()

    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    function_literal: FunctionLiteral = stmt.expression

    assert function_literal.token.type == TokenType.FUNCTION

    assert len(function_literal.parameters) == len(expected_parameters)
    for param, expected_param in zip(function_literal.parameters, expected_parameters):
        assert str(param) == expected_param

    assert str(function_literal.body) == expected_body


@pytest.mark.parametrize('test_input,expected_expression,expected_arguments', [
    ('abc()', 'abc', []),
    ('abc(1)', 'abc', ['1']),
    ('abc(a,b+2)', 'abc', ['a', '(b+2)']),
    ('abc(1+2,a,b)', 'abc', ['(1+2)', 'a', 'b']),
])
def test_parse_single_call_expression(test_input, expected_expression, expected_arguments):
    lexer = Lexer(test_input)
    parser = Parser(lexer)
    program = parser.parse_program()
    for statement in program.statements:
        print(statement)
    assert len(program.statements) == 1

    stmt: ExpressionStatement = program.statements[0]
    call_expr: CallExpression = stmt.expression

    assert call_expr.token.type == TokenType.LPAREN

    assert len(call_expr.arguments) == len(expected_arguments)
    for arg, expected_arg in zip(call_expr.arguments, expected_arguments):
        assert str(arg) == expected_arg

    assert str(call_expr.function) == expected_expression
