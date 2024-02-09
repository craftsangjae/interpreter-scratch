"""
Parsing의 정의

파서는 (주로 문자로 된) 입력 데이터를 받아 자료구조를 만들어내는 소프트웨어 컴포넌트.
자료구조 형태는 파스 트리(Parse Tree), 추상구문트리일 수 있고, 그렇지 않으면 다른 계층 구조일 수 도 있다.
파서는 자료구조를 만들면서 구조화된 표현을 더ㅏㅎ기도, 구문이 올바른지 검사하기도 한다.

"""
from enum import IntEnum
from typing import Optional, List, Dict, Callable

from pinterpret.ast import Program, Statement, LetStatement, Identifier, ReturnStatement, Expression, \
    ExpressionStatement, IntegerExpression, PrefixExpression, InfixExpression
from pinterpret.lexer import Lexer
from pinterpret.token import Token, TokenType


class OperatorPrecedence(IntEnum):
    LOWEST = 1
    EQUALS = 2
    LESSGREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7


PRECEDENCE_RELATION = {
    TokenType.EQUAL: OperatorPrecedence.EQUALS,
    TokenType.NOT_EQUAL: OperatorPrecedence.EQUALS,

    TokenType.LT: OperatorPrecedence.LESSGREATER,
    TokenType.GT: OperatorPrecedence.LESSGREATER,

    TokenType.PLUS: OperatorPrecedence.SUM,
    TokenType.MINUS: OperatorPrecedence.SUM,
    TokenType.SLASH: OperatorPrecedence.PRODUCT,
    TokenType.ASTERISK: OperatorPrecedence.PREFIX
}

# 전위함수 파싱 로직
prefix_parse_ftype = Callable[[], Expression]
infix_parse_ftype = Callable[[Expression], Expression]


class Parser:
    lexer: Lexer

    ct: Token
    nt: Token

    errors: List[str]

    prefix_parse_fns: Dict[TokenType, prefix_parse_ftype]
    infix_parse_fns: Dict[TokenType, infix_parse_ftype]

    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        # initialize current token & next_token
        self.ct = self.lexer.next_token()
        self.nt = self.lexer.next_token()

        self.errors = []
        self.prefix_parse_fns = {}
        self.infix_parse_fns = {}

        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INT, self.parse_identifier)
        self.register_prefix(TokenType.BANG, self.parse_prefix_expression)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)

        [
            self.register_infix(token_type, self.parse_infix_expression)
            for token_type in [TokenType.PLUS, TokenType.MINUS, TokenType.SLASH, TokenType.ASTERISK,
                               TokenType.LT, TokenType.GT, TokenType.EQUAL, TokenType.NOT_EQUAL, ]
        ]

    def parse_program(self) -> Program:
        program = Program()

        while self.ct.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                program.append(stmt)
            self.next_token()

        return program

    def register_prefix(self, token_type: TokenType, prefix_parse_func: prefix_parse_ftype):
        self.prefix_parse_fns[token_type] = prefix_parse_func

    def register_infix(self, token_type: TokenType, infix_parse_func: infix_parse_ftype):
        self.infix_parse_fns[token_type] = infix_parse_func

    def next_token(self):
        self.ct = self.nt
        self.nt = self.lexer.next_token()

    def parse_statement(self) -> Optional[Statement]:
        if self.ct.type == TokenType.LET:
            return self.parse_let_statement()
        elif self.ct.type == TokenType.RETURN:
            return self.parse_return_statement()
        else:
            # monkey 언어에는 실질적 명령문이 let 문과 return 문이 두 개 밖에 없기 때문에,
            # 이 두 경우가 아닐 때는 표현식 문으로 파싱한다.
            return self.parse_expression_statement()

    def parse_let_statement(self) -> Optional[LetStatement]:
        let_token = self.ct

        if not self.expect_peek(TokenType.IDENT):
            return

        identifier = Identifier(self.ct)

        if not self.expect_peek(TokenType.ASSIGN):
            return

        while not self.curr_token_is(TokenType.SEMICOLON):
            self.next_token()

            if self.curr_token_is(TokenType.EOF):
                self.peek_error(TokenType.SEMICOLON)
                break

        return LetStatement(let_token, identifier, None)

    def parse_return_statement(self) -> Optional[ReturnStatement]:
        return_token = self.ct

        while not self.curr_token_is(TokenType.SEMICOLON):
            self.next_token()

            if self.curr_token_is(TokenType.EOF):
                self.peek_error(TokenType.SEMICOLON)
                break

        return ReturnStatement(return_token, None)

    def parse_expression_statement(self) -> Optional[ExpressionStatement]:
        """ entrypoint for parsing expression.
        :return:
        """
        token = self.ct

        expression = self.parse_expression(OperatorPrecedence.LOWEST)

        if self.next_token_is(TokenType.SEMICOLON):
            # 선택적으로 처리할 수 있도록 위와 같이 구현
            # semicolon이 없어도 REPL에서 알아서 처리가능하도록.
            self.next_token()

        return ExpressionStatement(token, expression)

    def curr_token_is(self, t: TokenType) -> bool:
        return self.ct.type == t

    def next_token_is(self, t: TokenType) -> bool:
        return self.nt.type == t

    def expect_peek(self, t: TokenType):
        if self.next_token_is(t):
            self.next_token()
            return True
        self.peek_error(t)
        return False

    def peek_error(self, t: TokenType):
        error = f'expected next token to be {t.value}, got {self.nt.type} instead'
        self.errors.append(error)

    def curr_precedence(self) -> OperatorPrecedence:
        global PRECEDENCE_RELATION
        return PRECEDENCE_RELATION.get(self.ct.type, OperatorPrecedence.LOWEST)

    def next_precedence(self) -> OperatorPrecedence:
        global PRECEDENCE_RELATION
        return PRECEDENCE_RELATION.get(self.nt.type, OperatorPrecedence.LOWEST)

    def parse_expression(self, precedence: OperatorPrecedence) -> Optional[Expression]:
        if prefix := self.prefix_parse_fns.get(self.ct.type):
            left_expression = prefix()
        else:
            self.errors.append(f"no prefix parse function for {self.ct.type} found")
            return None

        while (not self.next_token_is(TokenType.SEMICOLON) and precedence < self.next_precedence()):
            infix = self.infix_parse_fns.get(self.nt.type, None)
            if infix is None:
                return left_expression
            self.next_token()
            left_expression = infix(left_expression)
        return left_expression

    def parse_identifier(self) -> Identifier:
        return Identifier(self.ct)

    def parse_integer(self) -> Expression:
        return IntegerExpression(self.ct)

    def parse_prefix_expression(self) -> Expression:
        token = self.ct
        self.next_token()
        right = self.parse_expression(OperatorPrecedence.PREFIX)
        return PrefixExpression(token, right)

    def parse_infix_expression(self, left: Expression) -> Expression:
        token = self.ct
        precedence = self.curr_precedence()
        self.next_token()
        right = self.parse_expression(precedence)
        return InfixExpression(token, left, right)
