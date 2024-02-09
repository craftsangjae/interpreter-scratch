from abc import ABC, abstractmethod
from enum import Enum


class ObjectType(Enum):
    Integer = "INTEGER"
    Boolean = "BOOLEAN"
    Null = "NULL"
    Return = "RETURN"
    Error = "ERROR"
    Function = "FUNCTION"


class Object(ABC):
    type: ObjectType

    @abstractmethod
    def inspect(self) -> str:
        pass
