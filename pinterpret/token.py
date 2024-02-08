from enum import Enum
from typing import Iterable, Union


class TokenType(Enum):
    ILLEGAL = 'ILLEGAL'
    EOF = 'EOF'

    IDENT = 'IDENT'
    INT = 'INT'

    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    BANG = '!'
    ASTERISK = '*'
    SLASH = '/'

    LT = '<'
    GT = '>'

    EQUAL = '=='
    NOT_EQUAL = '!='

    COMMA = ","
    SEMICOLON = ';'

    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'

    FUNCTION = 'fn'
    LET = 'let'
    TRUE = 'true'
    FALSE = 'false'
    IF = 'if'
    ELSE = 'else'
    RETURN = 'return'

    @classmethod
    def symbols(cls) -> Iterable['TokenType']:
        return (
            TokenType.ASSIGN,
            TokenType.PLUS,
            TokenType.COMMA,
            TokenType.MINUS,
            TokenType.BANG,
            TokenType.ASTERISK,
            TokenType.SLASH,
            TokenType.LT,
            TokenType.GT,
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.SEMICOLON,
            TokenType.LPAREN,
            TokenType.RPAREN,
            TokenType.LBRACE,
            TokenType.RBRACE,
        )

    @classmethod
    def reserved_words(cls) -> Iterable['TokenType']:
        """ 예약어

        :return:
        """
        return (
            TokenType.FUNCTION, TokenType.LET,
            TokenType.TRUE, TokenType.FALSE,
            TokenType.IF, TokenType.ELSE,
            TokenType.RETURN
        )

    def __eq__(self, other: Union['TokenType', str]):
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)


class Token:
    """ Lexical Analysis를 통해, 소스코드에서 나온 단어를 토큰 열로 변환
    """
    type: TokenType
    literal: str

    def __init__(self, word: str):
        if not word:
            self.type = TokenType.EOF
            self.literal = ''
            return

        for symbol in TokenType.symbols():
            if word == symbol:
                self.type = symbol
                self.literal = word
                return

        for token in TokenType.reserved_words():
            if word == token:
                self.type = token
                self.literal = word
                return

        if word.isnumeric():
            self.type = TokenType.INT
            self.literal = word
        elif word[0].isalnum() and word.isalnum():
            self.type = TokenType.IDENT
            self.literal = word
        else:
            self.type = TokenType.ILLEGAL
            self.literal = word
