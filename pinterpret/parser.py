from typing import Optional

from pinterpret.ast import Program, Statement, LetStatement, Identifier
from pinterpret.lexer import Lexer
from pinterpret.token import Token, TokenType


class Parser:
    lexer: Lexer

    ct: Token
    nt: Token

    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.ct = None
        self.nt = None
        self.next_token()
        self.next_token()

    def parse_program(self) -> Program:
        program = Program()

        while self.ct.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                program.append(stmt)
            self.next_token()

        return program

    def next_token(self):
        self.ct = self.nt
        self.nt = self.lexer.next_token()

    def parse_statement(self) -> Optional[Statement]:
        if self.ct.type == TokenType.LET:
            return self.parse_let_statement()
        else:
            return None

    def parse_let_statement(self) -> LetStatement:
        let_token = self.ct

        if not self.expect_peek(TokenType.IDENT):
            return None

        identifier = Identifier(self.ct)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        while not self.curr_token_is(TokenType.SEMICOLON):
            self.next_token()

        return LetStatement(let_token, identifier, None)

    def curr_token_is(self, t: TokenType) -> bool:
        return self.ct.type == t

    def next_token_is(self, t: TokenType) -> bool:
        return self.nt.type == t

    def expect_peek(self, t: TokenType):
        if self.next_token_is(t):
            self.next_token()
            return True
        return False
