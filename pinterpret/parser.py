"""
Parsing의 정의

파서는 (주로 문자로 된) 입력 데이터를 받아 자료구조를 만들어내는 소프트웨어 컴포넌트.
자료구조 형태는 파스 트리(Parse Tree), 추상구문트리일 수 있고, 그렇지 않으면 다른 계층 구조일 수 도 있다.
파서는 자료구조를 만들면서 구조화된 표현을 더ㅏㅎ기도, 구문이 올바른지 검사하기도 한다.

프랫파서 로직으로 구현되어 있음
<Top Down Operator Precedence, Vaughan Pratt>에 따른 로직

프랫파서의 역할

INPUT               OUTPUT
1 + 2 + 3;   ==>    ((1 + 2) + 3);
2 + 3 * 4;   ==>    (2 + (3  * 4);
-3 + 2 * 7;  ==>    ((-3) + (2 * 7));

"""
from enum import IntEnum
from typing import Optional, List, Dict, Callable

from pinterpret.ast import Program, Statement, LetStatement, Identifier, ReturnStatement, Expression, \
    ExpressionStatement, IntegerExpression, PrefixExpression, InfixExpression, BoolExpression, IfExpression, \
    BlockStatement
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

        # register identifier
        [self.register_prefix(t, self.parse_identifier) for t in [TokenType.IDENT, TokenType.INT]]

        # register bool literal
        [self.register_prefix(t, self.parse_bool) for t in [TokenType.TRUE, TokenType.FALSE]]

        # register prefix expression
        [self.register_prefix(t, self.parse_prefix_expression) for t in [TokenType.BANG, TokenType.MINUS]]

        # register infix expression
        [
            self.register_infix(t, self.parse_infix_expression)
            for t in [TokenType.PLUS, TokenType.MINUS, TokenType.SLASH, TokenType.ASTERISK,
                      TokenType.LT, TokenType.GT, TokenType.EQUAL, TokenType.NOT_EQUAL, ]
        ]

        # register group expression
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)

        # register group expression
        self.register_prefix(TokenType.IF, self.parse_if_expression)

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
        """ 프렛파서에서 핵심이 되는 로직
        case 1. 'a + b * c;'
        1) ct -> a을 바라봄
        2) a에 parse_identifier 적용
        3) depth1-while 구문 진입 --> infix_function 나옴
        4) infix_function 내 진입 --> parse_expression 호출 (이때, +의 precedence를 물고 호출)
        5) depth2-while 구문 진입 --> infix_function 나옴 (이때, *가 +보다 우선순위 높기 때문)
        6) infix_function 내 진입 --> parse_expression 호출
        7) depth3-while 구문 진입 --> 세미콜론 만나면서 탈출
        8) depth2-while 구문으로 나옴 --> (b * c)
        9) depth1-while 구문으로 나옴 --> a + (b * c)

        case 2. 'a + b + c;'
        1) ct -> a을 바라봄
        2) a에 parse_identifier 적용
        3) depth1-while 구문 진입 --> infix_function 나옴
        4) infix_function 내 진입 --> parse_expression 호출 (이때, +의 precedence를 물고 호출)
        5) depth2-while 구문 진입 --> 스킵
           => 주어진 피연산자가
           left_expr에 빨려들어갈 것인지, right_expr에 빨려들어갈 것인지를
           precedence < self.next_precedence()로 결정
        6) depth1-while 구문으로 나옴 --> l_expr에 (a+b)가 됨

        :param precedence:
        :return:
        """
        if prefix := self.prefix_parse_fns.get(self.ct.type):
            l_expr = prefix()
        else:
            self.errors.append(f"no prefix parse function for {self.ct.type} found")
            return None

        while not self.next_token_is(TokenType.SEMICOLON) and precedence < self.next_precedence():
            infix_function = self.infix_parse_fns.get(self.nt.type, None)
            if infix_function is None:
                return l_expr
            self.next_token()
            l_expr = infix_function(l_expr)
        return l_expr

    def parse_identifier(self) -> Identifier:
        return Identifier(self.ct)

    def parse_integer(self) -> Expression:
        return IntegerExpression(self.ct)

    def parse_bool(self) -> Expression:
        return BoolExpression(self.ct)

    def parse_prefix_expression(self) -> Expression:
        token = self.ct
        self.next_token()
        right = self.parse_expression(OperatorPrecedence.PREFIX)
        return PrefixExpression(token, right)

    def parse_infix_expression(self, left_expr: Expression) -> Expression:
        token = self.ct
        precedence = self.curr_precedence()
        self.next_token()
        right_expr = self.parse_expression(precedence)
        return InfixExpression(token, left_expr, right_expr)

    def parse_grouped_expression(self) -> Optional[Expression]:
        self.next_token()

        expr = self.parse_expression(OperatorPrecedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return

        return expr

    def parse_if_expression(self) -> Optional[Expression]:
        token = self.ct

        if not self.expect_peek(TokenType.LPAREN):
            return

        self.next_token()
        condition = self.parse_expression(OperatorPrecedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return

        if not self.expect_peek(TokenType.LBRACE):
            return

        consequence = self.parse_block_statement()

        if self.next_token_is(TokenType.ELSE):
            self.next_token()

            if not self.expect_peek(TokenType.LBRACE):
                return None
            alternatives = self.parse_block_statement()
            return IfExpression(token, condition, consequence, alternatives)
        else:
            return IfExpression(token, condition, consequence)

    def parse_block_statement(self) -> BlockStatement:
        token = self.ct

        self.next_token()
        stmts = []
        while not (self.curr_token_is(TokenType.RBRACE) or self.curr_token_is(TokenType.EOF)):
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
            self.next_token()
        return BlockStatement(token, stmts)
