import pytest

from pinterpret.common import Object
from pinterpret.environment import Environment
from pinterpret.evaluator import evaluate
from pinterpret.lexer import Lexer
from pinterpret.obj import FunctionObj
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

    result = evaluate(program, Environment())

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

    result = evaluate(program, Environment())

    assert result.inspect() == str(expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("return 5; 3", 5),
        ("return 5", 5),
        ("5;return 3", 3),
        ("5;return 3; 7;", 3),
        ("5;return 3;return 5; 4;", 3),
        ("let a = 5;a;", 5),
        ("let a = 5;a + a + 3;", 13),
    ],
)
def test_evaluate_return_statements(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result = evaluate(program, Environment())

    assert result.inspect() == str(expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("5==true", "Error: type mismatch : ObjectType.Integer == ObjectType.Boolean"),
        (
            "if(5==false) {3}",
            "Error: type mismatch : ObjectType.Integer == ObjectType.Boolean",
        ),
        ("hello", "Error: identifier not found : hello"),
    ],
)
def test_handle_error(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result = evaluate(program, Environment())

    assert result.inspect() == str(expected)


@pytest.mark.parametrize(
    "test_input,expected_params,expected_body",
    [
        ("fn(x,y,z) {x+y+z}", ["x", "y", "z"], ["((x+y)+z)"]),
    ],
)
def test_evaluate_function_literal(test_input, expected_params, expected_body):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result: FunctionObj = evaluate(program, Environment())

    assert len(result.parameters) == len(expected_params)
    for param, expected in zip(result.parameters, expected_params):
        assert param.value == expected

    for body, expected in zip(result.body.statements, expected_body):
        assert str(body) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("let add = fn(a,b) { return a+b }; add(2,3);", 5),
        ("let add = fn(a,b) { return a+b }; add(2,3) + add(5,7);", 17),
        ("let add = fn(a,b) { return a+b }; add(add(2,3),add(5,7));", 17),
        (
            "let add = fn(a,b) { return a+b }; let mul = fn(a,b) {a*b;}; mul(add(2,3),add(5,7));",
            60,
        ),
    ],
)
def test_evaluate_call_expression(test_input, expected):
    lexer = Lexer(test_input)
    parser = Parser(lexer)

    program = parser.parse_program()

    result: Object = evaluate(program, Environment())

    assert result.inspect() == str(expected)
