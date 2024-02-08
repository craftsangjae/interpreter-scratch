from typing import Optional, List

from pinterpret.ast import Program, Statement, LetStatement, Identifier
from pinterpret.lexer import Lexer
from pinterpret.token import Token, TokenType


class Parser:
    lexer: Lexer

    ct: Token
    nt: Token

    errors: List[str]

    def __init__(self, lexer: Lexer):
        self.lexer = lexer

        # initialize current token & next_token
        self.ct = self.lexer.next_token()
        self.nt = self.lexer.next_token()

        self.errors = []

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
