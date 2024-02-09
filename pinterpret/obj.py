from typing import List

from pinterpret.ast import Identifier, BlockStatement
from pinterpret.common import Object, ObjectType
from pinterpret.environment import Environment


class IntegerObj(Object):
    value: int

    def __init__(self, value: int):
        self.type = ObjectType.Integer
        self.value = value

    def inspect(self) -> str:
        return str(self.value)

    def __eq__(self, other: "NullObj"):
        return isinstance(other, IntegerObj) and (self.value == other.value)


class BooleanObj(Object):
    value: bool

    def __init__(self, value: bool):
        self.type = ObjectType.Boolean
        self.value = value

    def inspect(self) -> str:
        return str(self.value)

    def __eq__(self, other: "BooleanObj"):
        return (
            isinstance(other, BooleanObj)
            and (self.type == other.type)
            and (self.value == other.value)
        )


class NullObj(Object):
    def __init__(self):
        self.type = ObjectType.Null

    def inspect(self) -> str:
        return "null"

    def __eq__(self, other: "NullObj"):
        return isinstance(other, NullObj)


class ReturnObj(Object):

    def __init__(self, value: Object):
        self.type = ObjectType.Return
        self.value = value

    def inspect(self) -> str:
        return self.value.inspect()

    def __eq__(self, other: Object):
        return self.value == other


class ErrorObj(Object):

    def __init__(self, message: str):
        self.type = ObjectType.Return
        self.message = message

    def inspect(self) -> str:
        return "Error: " + self.message


class FunctionObj(Object):
    parameters: List[Identifier]
    body: BlockStatement

    env: Environment

    def __init__(
        self, parameters: List[Identifier], body: BlockStatement, env: Environment
    ):
        self.type = ObjectType.Function
        self.parameters = parameters
        self.body = body
        self.env = env

    def inspect(self) -> str:
        params = ",".join([p.value for p in self.parameters])
        return f"fn ({params}) {{{self.body}}}"
