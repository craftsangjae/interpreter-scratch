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


class BooleanObj(Object):
    value: bool

    def __init__(self, value: bool):
        self.type = ObjectType.Boolean
        self.value = value

    def inspect(self) -> str:
        return str(self.value)


class NullObj(Object):
    def __init__(self):
        self.type = ObjectType.Null

    def inspect(self) -> str:
        return "null"
