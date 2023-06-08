from lex import Lexer
from token import TokenType


def main():
    source = "IF+-123 foo*THEN/"
    lexer = Lexer(source)
    lexer.next_char()
    token = lexer.get_token()
    while token.kind != TokenType.EOF:
        print(f"[+] {token.kind}")
        lexer.next_char()
        lexer.skip_whitespace()
        lexer.skip_comment()
        token = lexer.get_token()
        if token is None:
            print(lexer.current_char)
            lexer.abort("Unknown token.")


if __name__ == "__main__":
    main()
