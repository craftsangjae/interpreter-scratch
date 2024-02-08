from pinterpret.token import Token


class Lexer:
    """
    read source codes and return the array of tokens.
    """
    input: str
    pos: int  # current index of input string
    rpos: int  # next index of input string
    char: str  # character

    def __init__(self, input: str):
        self.input = input
        self.pos = 0
        self.rpos = 0
        self.char = ''
        self.read_char()

    @property
    def closed(self):
        return self.pos > len(self.input)

    def read_char(self):
        self.char = self.peek_char()
        self.pos = self.rpos
        self.rpos += 1

    def peek_char(self):
        if self.rpos >= len(self.input):
            return ''
        else:
            return self.input[self.rpos]

    def next_token(self) -> Token:
        self.skip_whitespace()

        if self.char.isalpha():
            # reserved word or identifier
            text = self.read_identifier()
        elif self.char.isnumeric():
            # integer or float
            text = self.read_integer()
        else:
            if self.char == '=' and self.peek_char() == '=':
                self.read_char()
                text = '=='
            elif self.char == '!' and self.peek_char() == '=':
                self.read_char()
                text = '!='
            else:
                text = self.char
            self.read_char()
        return Token(text)

    def skip_whitespace(self):
        while self.char in {' ', '\n', '\t', '\r'}:
            self.read_char()

    def read_identifier(self):
        pos = self.pos
        while True:
            self.read_char()
            if not self.char.isalnum():
                break
        return self.input[pos:self.pos]

    def read_integer(self):
        pos = self.pos
        while True:
            self.read_char()
            if not (self.char.isnumeric() or self.char == '.'):
                break
        return self.input[pos:self.pos]
