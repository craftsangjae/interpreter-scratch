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
    LetStatement,
    Identifier,
    FunctionLiteral,
    CallExpression,
    Expression,
)
from pinterpret.common import Object
from pinterpret.environment import Environment
from pinterpret.obj import (
    IntegerObj,
    BooleanObj,
    NullObj,
    ReturnObj,
    ErrorObj,
    FunctionObj,
)
from pinterpret.token import TokenType


def evaluate(node: Node, env: Environment) -> Object:
    if isinstance(node, Program):
        return evaluate_statements(node.statements, env)

    elif isinstance(node, BlockStatement):
        return evaluate_statements(node.statements, env)

    elif isinstance(node, ExpressionStatement):
        return evaluate(node.expression, env)

    elif isinstance(node, PrefixExpression):
        return evaluate_prefix_expression(node, env)

    elif isinstance(node, InfixExpression):
        return evaluate_infix_expression(node, env)

    elif isinstance(node, IfExpression):
        return evaluate_if_expression(node, env)

    elif isinstance(node, ReturnStatement):
        return evaluate_return_statement(node, env)

    elif isinstance(node, LetStatement):
        value = evaluate(node.value, env)
        if isinstance(value, ErrorObj):
            return value
        env.set(node.name.value, value)

    elif isinstance(node, IntegerLiteral):
        return IntegerObj(node.value)

    elif isinstance(node, Identifier):
        val, ok = env.get(node.value)
        if ok:
            return val
        else:
            return ErrorObj("identifier not found : " + node.value)

    elif isinstance(node, FunctionLiteral):
        return FunctionObj(parameters=node.parameters, body=node.body, env=env)

    elif isinstance(node, BoolLiteral):
        return BooleanObj(node.value)

    elif isinstance(node, CallExpression):
        function: FunctionObj = evaluate(node.function, env)
        if isinstance(function, ErrorObj):
            return function

        args = evaluate_expressions(node.arguments, env)
        if len(args) == 1 and isinstance(args[0], ErrorObj):
            return args[0]
        return apply_function(function, args)

    return NullObj()


def evaluate_statements(stmts: List[Statement], env: Environment) -> Object:
    result = NullObj()
    for stmt in stmts:
        result = evaluate(stmt, env)
        if isinstance(result, ReturnObj) or isinstance(result, ErrorObj):
            return result
    return result


def evaluate_expressions(exprs: List[Expression], env: Environment) -> List[Object]:
    results = []
    for expr in exprs:
        result = evaluate(expr, env)
        if isinstance(result, ErrorObj):
            return [result]
        results.append(result)
    return results


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
    return ErrorObj(f"not supported : - {right_obj.type}")


def evaluate_prefix_expression(node: PrefixExpression, env: Environment):
    right_obj = evaluate(node.right, env)

    if isinstance(right_obj, ErrorObj):
        return right_obj

    if node.token.type == TokenType.BANG:
        return evaluate_bang_prefix_expression(right_obj)
    elif node.token.type == TokenType.MINUS:
        return evaluate_minus_prefix_expression(right_obj)
    else:
        return ErrorObj(f"not supported : {node.operator} {right_obj.type}")


def evaluate_infix_expression(node: InfixExpression, env: Environment) -> Object:
    left_obj = evaluate(node.left, env)
    right_obj = evaluate(node.right, env)

    if isinstance(left_obj, ErrorObj):
        return left_obj
    elif isinstance(right_obj, ErrorObj):
        return right_obj

    if node.operator in ("+", "-", "*", "/", "<", ">"):
        if not (isinstance(left_obj, IntegerObj) and isinstance(right_obj, IntegerObj)):
            return ErrorObj(
                f"type mismatch : {left_obj.type} {node.operator} {right_obj.type}"
            )
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
            return ErrorObj(
                f"not supported : {left_obj.type} {node.operator} {right_obj.type}"
            )
    elif node.operator in ("==", "!="):
        if not (
            (isinstance(left_obj, IntegerObj) and isinstance(right_obj, IntegerObj))
            or (isinstance(left_obj, BooleanObj) and isinstance(right_obj, BooleanObj))
        ):
            return ErrorObj(
                f"type mismatch : {left_obj.type} {node.operator} {right_obj.type}"
            )

        if node.operator == "==":
            return BooleanObj(left_obj.value == right_obj.value)
        elif node.operator == "!=":
            return BooleanObj(left_obj.value != right_obj.value)
        else:
            return ErrorObj(
                f"not supported {left_obj.type} {node.operator} {right_obj.type}"
            )
    else:
        return ErrorObj(
            f"not supported {left_obj.type} {node.operator} {right_obj.type}"
        )


def evaluate_if_expression(node: IfExpression, env: Environment) -> Object:
    value = evaluate(node.condition, env)
    if isinstance(value, ErrorObj):
        return value

    if is_truthy(value):
        return evaluate(node.consequence, env)
    elif node.alternative:
        return evaluate(node.alternative, env)
    return NullObj()


def evaluate_return_statement(node: ReturnStatement, env: Environment) -> Object:
    value = evaluate(node.return_value, env)
    if isinstance(value, ErrorObj):
        return value
    return ReturnObj(value)


def apply_function(fn: FunctionObj, args: List[Object]) -> Object:
    extended_env = extend_function_env(fn, args)
    evaluated = evaluate(fn.body, extended_env)

    if isinstance(evaluated, ReturnObj):
        return evaluated.value
    return evaluated


def extend_function_env(fn: FunctionObj, args: List[Object]) -> Environment:
    extended_env = Environment(fn.env)

    for param, arg in zip(fn.parameters, args):
        extended_env.set(param.value, arg)
    return extended_env


def is_truthy(value: Object):
    if isinstance(value, BooleanObj):
        return value.value
    elif isinstance(value, IntegerObj):
        return value.value != 0
    else:
        return False
