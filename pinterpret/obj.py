from abc import ABC, abstractmethod
from enum import Enum


class ObjectType(Enum):
    Integer = "INTEGER"
    Boolean = "BOOLEAN"
    Null = "NULL"


class Object(ABC):
    type: ObjectType

    @abstractmethod
    def inspect(self) -> str:
        pass


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
