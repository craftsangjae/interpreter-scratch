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
    ],
)
def test_evaluate_single_statement(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result = evaluate(program)

    assert result.inspect() == str(expected)
