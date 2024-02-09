from lexer import Lexer

if __name__ == "__main__":
    text = input(">>> ")
    while text:
        lexer = Lexer(text)
        while True:
            token = lexer.next_token()
            if lexer.closed:
                break
            print(token.type, token.literal)
        text = input(">>> ")
