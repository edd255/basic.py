from token import TokenType, Token
from typing import Optional
from sys import exit


class Lexer:
    def __init__(self, source: str):
        # Source code to lex as a string. Append a newline to simplify
        # lexing/parsing the last token/statement.
        self.source = source + "\n"

        # Current character in the string
        self.current_char = ""

        # Current position in the string
        self.current_position = -1

    def next_char(self) -> None:
        """Process the next character."""
        self.current_position += 1
        self.current_char = (
            self.source[self.current_position]
            if self.current_position < len(self.source)
            else "\0"
        )

    def peek(self) -> str:
        """Return the lookahead character."""
        if self.current_position + 1 >= len(self.source):
            return "\0"
        return self.source[self.current_position + 1]

    def abort(self, message: str):
        """Invalid token found, print error message and exit."""
        exit(f"[-] Lexing error. {message}")

    def skip_whitespace(self) -> None:
        """Skip whitespace except newline, which we will use to indicate the end of a statement"""
        if self.current_char in {" ", "\t", "\r"}:
            self.next_char()

    def skip_comment(self) -> None:
        """Skip comments in the code."""
        if self.current_char == "#":
            while self.current_char != "\n":
                self.next_char()

    def get_token(self) -> Optional[TokenType]:
        """Check the first character of this token to see if we can decide
        what it is. If it is a multiple character operator (e.g., !=), number,
        identifier, or keyword then we will process the rest."""

        if self.current_char == "+":
            return Token(self.current_char, TokenType.PLUS)
        elif self.current_char == "-":
            return Token(self.current_char, TokenType.MINUS)
        elif self.current_char == "*":
            return Token(self.current_char, TokenType.ASTERISK)
        elif self.current_char == "/":
            return Token(self.current_char, TokenType.SLASH)
        elif self.current_char == "=":
            if self.peek() == "=":
                self.next_char()
                return Token("==", TokenType.EQEQ)
            else:
                return Token(self.current_char, TokenType.EQ)
        elif self.current_char == ">":
            if self.peek() == "=":
                self.next_char()
                return Token(">=", TokenType.GTEQ)
            else:
                return Token(self.current_char, TokenType.GT)
        elif self.current_char == "<":
            if self.peek() == "=":
                self.next_char()
                return Token("<=", TokenType.LTEQ)
            else:
                return Token(self.current_char, TokenType.GT)
        elif self.current_char == "!":
            if self.peek() == "=":
                self.next_char()
                return Token("!=", TokenType.NOTEQ)
            else:
                self.abort(f"Expected '!=', got '!{self.peek()}'")
        elif self.current_char == '"':
            self.next_char()
            start_position = self.current_position
            while self.current_char != '"':
                if self.current_char in {"\r", "\n", "\t", "\\", "%"}:
                    self.abort(f"Illegal character in string: {self.current_char}")
                self.next_char()
            token_text = self.source[start_position : self.current_position]
            return Token(token_text, TokenType.STRING)
        elif self.current_char == "\n":
            return Token(self.current_char, TokenType.NEWLINE)
        elif self.current_char == "\0":
            return Token(self.current_char, TokenType.EOF)
        elif self.current_char.isdigit():
            start_position = self.current_position
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == ".":
                self.next_char()
                if not self.peek().isdigit():
                    self.abort(f"Illegal character in number: {self.peek()}")
                while self.peek().isdigit():
                    self.next_char()
            token_text = self.source[start_position : self.current_position + 1]
            return Token(token_text, TokenType.NUMBER)
        elif self.current_char.isalpha():
            """Leading character is a letter, so this must be an identifier or
            a keyword. Get all consecutive alpha numeric characters."""
            start_position = self.current_position
            while self.peek().isalnum():
                self.next_char()

            # Check if the token is in the list of keywords
            token_text = self.source[start_position : self.current_position + 1]
            if (keyword := Token.check_if_keyword(token_text)) is None:
                return Token(token_text, TokenType.IDENT)
            else:
                return Token(token_text, keyword)
        else:
            return None
