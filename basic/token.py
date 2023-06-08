from typing import Optional
from enum import Enum

OPERATORS = [
    "EQ",
    "PLUS",
    "MINUS",
    "ASTERISK",
    "SLASH",
    "EQEQ",
    "NOTEQ",
    "LT",
    "LTEQ",
    "GT",
    "GTEQ",
]

KEYWORDS = [
    "LABEL",
    "GOTO",
    "PRINT",
    "INPUT",
    "LET",
    "IF",
    "THEN",
    "ENDIF",
    "WHILE",
    "REPEAT",
    "ENDWHILE",
]

RESIDUALS = [
    "EOF",
    "NEWLINE",
    "NUMBER",
    "IDENT",
    "STRING"
]


TokenType = Enum(
    "TokenType",
    KEYWORDS + OPERATORS + RESIDUALS
)


class Token:
    def __init__(self, token_text: str, token_kind: TokenType):
        # The token's actual text. Used for identifiers, strings, and numbers
        self.text = token_text

        # The TokenType that this token is classified as.
        self.kind = token_kind

    @staticmethod
    def check_if_keyword(token_text: str) -> Optional[TokenType]:
        return TokenType[token_text] if token_text in KEYWORDS else None
