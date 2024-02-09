from abc import ABC, abstractmethod

from pinterpret.obj import ObjectType


class Object(ABC):
    type: ObjectType

    @abstractmethod
    def inspect(self) -> str:
        pass
