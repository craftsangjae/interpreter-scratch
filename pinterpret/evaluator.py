from typing import List

from pinterpret.ast import (
    Node,
    IntegerLiteral,
    BoolLiteral,
    ExpressionStatement,
    Program,
    Statement,
    PrefixExpression,
    InfixExpression,
    IfExpression,
    BlockStatement,
    ReturnStatement,
)
from pinterpret.obj import Object, IntegerObj, BooleanObj, NullObj, ReturnObj
from pinterpret.token import TokenType


def evaluate(node: Node) -> Object:
    if isinstance(node, Program):
        return evaluate_statements(node.statements)

    elif isinstance(node, BlockStatement):
        return evaluate_statements(node.statements)

    elif isinstance(node, ExpressionStatement):
        return evaluate(node.expression)

    elif isinstance(node, PrefixExpression):
        return evaluate_prefix_expression(node)

    elif isinstance(node, InfixExpression):
        return evaluate_infix_expression(node)

    elif isinstance(node, IfExpression):
        return evaluate_if_expression(node)

    elif isinstance(node, ReturnStatement):
        return evaluate_return_statement(node)

    elif isinstance(node, IntegerLiteral):
        return IntegerObj(node.value)

    elif isinstance(node, BoolLiteral):
        return BooleanObj(node.value)

    return NullObj()


def evaluate_statements(stmts: List[Statement]) -> Object:
    result = NullObj()
    for stmt in stmts:
        result = evaluate(stmt)
        if isinstance(result, ReturnObj):
            return result
    return result


def evaluate_bang_prefix_expression(right_obj: Object) -> Object:
    if right_obj == BooleanObj(True):
        return BooleanObj(False)
    elif right_obj == BooleanObj(False):
        return BooleanObj(True)
    elif right_obj == NullObj():
        return BooleanObj(True)
    else:
        return BooleanObj(False)


def evaluate_minus_prefix_expression(right_obj: Object) -> Object:
    if isinstance(right_obj, IntegerObj):
        return IntegerObj(-right_obj.value)
    return NullObj()


def evaluate_prefix_expression(node: PrefixExpression):
    right_obj = evaluate(node.right)

    if node.token.type == TokenType.BANG:
        return evaluate_bang_prefix_expression(right_obj)
    elif node.token.type == TokenType.MINUS:
        return evaluate_minus_prefix_expression(right_obj)
    else:
        return NullObj()


def evaluate_infix_expression(node: InfixExpression) -> Object:
    left_obj = evaluate(node.left)
    right_obj = evaluate(node.right)

    if node.operator in ("+", "-", "*", "/", "<", ">"):
        if not (isinstance(left_obj, IntegerObj) and isinstance(right_obj, IntegerObj)):
            return NullObj()
        if node.operator == "+":
            return IntegerObj(left_obj.value + right_obj.value)
        elif node.operator == "-":
            return IntegerObj(left_obj.value - right_obj.value)
        elif node.operator == "*":
            return IntegerObj(left_obj.value * right_obj.value)
        elif node.operator == "/":
            return IntegerObj(left_obj.value // right_obj.value)
        elif node.operator == "<":
            return BooleanObj(left_obj.value < right_obj.value)
        elif node.operator == ">":
            return BooleanObj(left_obj.value > right_obj.value)
        else:
            return NullObj()
    elif node.operator in ("==", "!="):
        if not (
            (isinstance(left_obj, IntegerObj) and isinstance(right_obj, IntegerObj))
            or (isinstance(left_obj, BooleanObj) and isinstance(right_obj, BooleanObj))
        ):
            return NullObj()

        if node.operator == "==":
            return BooleanObj(left_obj.value == right_obj.value)
        elif node.operator == "!=":
            return BooleanObj(left_obj.value != right_obj.value)
        else:
            return NullObj()
    else:
        return NullObj()


def evaluate_if_expression(node: IfExpression) -> Object:
    value = evaluate(node.condition)

    if is_truthy(value):
        return evaluate(node.consequence)
    elif node.alternative:
        return evaluate(node.alternative)
    return NullObj()


def evaluate_return_statement(node: ReturnStatement) -> Object:
    value = evaluate(node.return_value)
    return ReturnObj(value)


def is_truthy(value: Object):
    if isinstance(value, BooleanObj):
        return value.value
    elif isinstance(value, IntegerObj):
        return value.value != 0
    else:
        return False
