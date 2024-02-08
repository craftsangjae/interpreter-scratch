from abc import ABC, abstractmethod
from typing import List, Optional

from pinterpret.token import Token


class Node(ABC):

    @abstractmethod
    def token_literal(self) -> str:
        pass


class Statement(Node):
    """ 명령문

    명령문 vs 표현식
    명령문 : 값을 만들지 않음 (ex : return 5;)

    표현식 : 값을 만듦 (ex: add(5,3);)
    """
    pass


class Expression(Node):
    """표현식
    """
    pass


class Identifier(Expression):
    """ 식별자 노드
    """
    token: Token
    value: str

    def __init__(self, token: Token):
        self.token = token
        self.value = token.literal

    def token_literal(self) -> str:
        return self.token.literal


class LetStatement(Statement):
    """
    ex)  let x = 5 + 2;
    let: token(Token)
    x : name(identifier)
    5 + 2 : value(Expression)
    """
    token: Token
    name: Identifier
    value: Expression

    def __init__(self, token: Token, name: Identifier, value: Expression):
        self.token = token
        self.name = name
        self.value = value

    def token_literal(self) -> str:
        return self.token.literal


class ReturnStatement(Statement):
    """
    ex) return 5;
    """
    token: Token
    return_value: Expression

    def __init__(self, token: Token, return_value: Expression):
        self.token = token
        self.return_value = return_value

    def token_literal(self) -> str:
        return self.token.literal


class Program(Node):
    statements: List[Statement]

    def __init__(self, statements: Optional[List[Statement]] = None):
        self.statements = statements if statements else []

    def append(self, statement: Statement):
        self.statements.append(statement)

    def token_literal(self) -> str:
        if self.statements:
            return self.statements[0].token_literal()
        else:
            return ''
