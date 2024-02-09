from typing import List

from pinterpret.ast import (
    Node,
    IntegerLiteral,
    BoolLiteral,
    ExpressionStatement,
    Program,
    Statement,
)
from pinterpret.obj import Object, IntegerObj, BooleanObj, NullObj


def evaluate(node: Node) -> Object:
    if isinstance(node, Program):
        return evaluate_statements(node.statements)

    elif isinstance(node, ExpressionStatement):
        return evaluate(node.expression)

    elif isinstance(node, IntegerLiteral):
        return IntegerObj(node.value)

    elif isinstance(node, BoolLiteral):
        return BooleanObj(node.value)

    return NullObj()


def evaluate_statements(stmts: List[Statement]) -> Object:
    result = NullObj()
    for stmt in stmts:
        result = evaluate(stmt)
    return result
