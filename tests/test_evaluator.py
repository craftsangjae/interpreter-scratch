import pytest

from pinterpret.evaluator import evaluate
from pinterpret.lexer import Lexer
from pinterpret.parser import Parser


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("3", 3),
        ("54", 54),
        ("false", False),
        ("true", True),
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!!true", False),
        ("-5", -5),
        ("--5", 5),
        ("5+2", 7),
        ("5/2", 2),
        ("(5+2)*3", 21),
        ("2+7*3/7*10", 32),
        ("5<2", False),
        ("5<7", True),
        ("5==5", True),
        ("5!=7", True),
        ("5!=5", False),
        ("5<3 == true", False),
        ("5<7 == true", True),
    ],
)
def test_evaluate_single_statement(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result = evaluate(program)

    assert result.inspect() == str(expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("if (3<5) {5} else {3}", 5),
        ("if (3>5) {5} else {3}", 3),
        ("if (3<5) {5;2;} else {3}", 2),
        ("if (3>5) {5;2;}", "null"),
        ("if (10) {5} else {2}", 5),
        ("if (0) {5} else {2}", 2),
    ],
)
def test_evaluate_if_expression(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result = evaluate(program)

    assert result.inspect() == str(expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("return 5; 3", 5),
        ("return 5", 5),
        ("5;return 3", 3),
        ("5;return 3; 7;", 3),
        ("5;return 3;return 5; 4;", 3),
    ],
)
def test_evaluate_return_statements(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result = evaluate(program)

    assert result.inspect() == str(expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("5==true", "Error: type mismatch : ObjectType.Integer == ObjectType.Boolean"),
        (
            "if(5==false) {3}",
            "Error: type mismatch : ObjectType.Integer == ObjectType.Boolean",
        ),
    ],
)
def test_handle_error(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result = evaluate(program)

    assert result.inspect() == str(expected)
