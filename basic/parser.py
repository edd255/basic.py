from lexer import Lexer
from tokens import TokenType
from emitter import Emitter
from sys import exit


# program    ::= {statement}
# statement  ::= "PRINT" (expression | string) newline
#              | "IF" comparison "THEN" nl {statement} "ENDIF" newline
#              | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" newline
#              | "LABEL" ident newline
#              | "GOTO" ident newline
#              | "LET" ident "=" expression newline
#              | "INPUT" ident newline
# comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
# expression ::= term {( "-" | "+" ) term}
# term       ::= unary {( "/" | "*" ) unary}
# unary      ::= ["+" | "-"] primary
# primary    ::= number | ident
# newline    ::= '\n'+
class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter) -> None:
        self.lexer = lexer
        self.emitter = emitter

        # Variables declared so far
        self.symbols = set()

        # Labels declared so far
        self.declared_labels = set()

        # Labels goto'ed so far
        self.gotoed_labels = set()

        self.current_token = None
        self.peek_token = None
        self.next_token()
        self.next_token()

    def check_token(self, kind: TokenType) -> bool:
        return kind == self.current_token.kind

    def check_tokens(self, kinds: list[TokenType]) -> bool:
        return self.current_token.kind in kinds

    def check_peek(self, kind: TokenType) -> bool:
        return kind == self.peek_token.kind

    def match(self, kind: TokenType) -> None:
        if not self.check_token(kind):
            self.abort(f"Expected {kind.name}, got {self.current_token.name}")
        self.next_token()

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message: str) -> None:
        exit(f"Error: {message}")

    # ---- PRODUCTION RULES ----------------------------------------------------
    # program := {statement}
    def rule_program(self) -> None:
        print("PROGRAM")
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void) {")

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        # Parse all statements in the program
        while not self.check_token(TokenType.EOF):
            self.rule_statement()

        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")

        # CHeck that each label referenced in a GOTO is declared.
        for label in self.gotoed_labels:
            if label not in self.declared_labels:
                self.abort(f"Attempting to GOTO to undeclared label: {label}")

    # statement ::= "PRINT" (expression | string) nl
    def rule_statement(self) -> None:
        # Check the first token to see what kind of statement this is.
        # "PRINT" (expression | string)
        match self.current_token.kind:
            # "PRINT" (expression | string)
            case TokenType.PRINT:
                print("STATEMENT-PRINT")
                self.next_token()
                if self.check_token(TokenType.STRING):
                    # Simple stritng
                    self.emitter.emit_line(f'printf("{self.current_token.text}\\n");')
                    self.next_token()
                else:
                    # Expect an expression
                    self.emitter.emit('printf("%' + '.2f\\n", (float)(')
                    self.rule_expression()
                    self.emitter.emit_line("));")

            # "IF" comparison "THEN" {statement} "ENDIF"
            case TokenType.IF:
                print("STATEMENT-IF")
                self.next_token()
                self.emitter.emit("if(")
                self.rule_comparison()

                self.match(TokenType.THEN)
                self.rule_newline()
                self.emitter.emit_line(") {")

                # Zero or more statements in the body
                while not self.check_token(TokenType.ENDIF):
                    self.rule_statement()

                self.match(TokenType.ENDIF)
                self.emitter.emit_line("}")

            # "WHILE" comparison "REPEAT" {statement} "ENDWHILE"
            case TokenType.WHILE:
                print("STATEMENT-WHILE")
                self.next_token()
                self.emitter.emit("while(")
                self.rule_comparison()

                self.match(TokenType.REPEAT)
                self.rule_newline()
                self.emitter.emit_line(") {")

                # Zero or more statements in the loop body.
                while not self.check_token(TokenType.ENDWHILE):
                    self.rule_statement()

                self.match(TokenType.ENDWHILE)
                self.emitter.emit_line("}")

            # "LABEL" ident
            case TokenType.LABEL:
                print("STATEMENT-LABEL")
                self.next_token()

                # Make sure this label doesn't already exist.
                if self.current_token.text in self.declared_labels:
                    self.abort(f"Label aready exists: {self.current_token.text}")

                self.declared_labels.add(self.current_token.text)
                self.emitter.emit_line(f"{self.current_token.text}:")
                self.match(TokenType.IDENT)

            # "GOTO" ident
            case TokenType.GOTO:
                print("STATEMENT-GOTO")
                self.next_token()
                self.gotoed_labels.add(self.current_token.text)
                self.emitter.emit_line(f"goto {self.current_token.text};")
                self.match(TokenType.IDENT)

            # "LET" ident "=" expression
            case TokenType.LET:
                print("STATEMENT-LET")
                self.next_token()

                # Check if ident exists in symbol table. If not, declare it.
                if self.current_token.text not in self.symbols:
                    self.symbols.add(self.current_token.text)
                    self.emitter.header_line(f"float {self.current_token.text};")

                self.emitter.emit(f"{self.current_token.text} = ")
                self.match(TokenType.IDENT)
                self.match(TokenType.EQ)

                self.rule_expression()
                self.emitter.emit_line(";")

            # "INPUT" ident
            case TokenType.INPUT:
                print("STATEMENT-INPUT")
                self.next_token()

                # If variable doesn't already exist, declare it
                if self.current_token.text not in self.symbols:
                    self.symbols.add(self.current_token.text)
                    self.emitter.header_line(f"float {self.current_token.text};")

                self.emitter.emit_line(
                    f'if (0 == scanf("%f", &{self.current_token.text})) ' + "{"
                )
                self.emitter.emit_line(f"{self.current_token.text} = 0;")
                self.emitter.emit('scanf("%')
                self.emitter.emit_line('*s");')
                self.emitter.emit_line("}")
                self.match(TokenType.IDENT)

            case _:
                self.abort(
                    f"Invalid statement at {self.current_token.text}",
                    f"({self.current_token.kind.name})",
                )

        # Newline.
        self.rule_newline()

    # newline ::= "\n"+
    def rule_newline(self) -> None:
        print("NEWLINE")

        # Require at least one newline
        self.match(TokenType.NEWLINE)

        # But we'll allow extra newlines, too, of course.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def rule_comparison(self) -> None:
        print("COMPARISON")

        self.rule_expression()
        # Must be at least one comparison operator and another expression.
        if self.is_comparison_operator():
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.rule_expression()
        else:
            self.abort(f"Expected comparison oerator at {self.current_token.text}")

        while self.is_comparison_operator():
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.rule_expression()

    # Return true if the current token is a comparison operator.
    def is_comparison_operator(self) -> bool:
        return self.check_tokens(
            [
                TokenType.GT,
                TokenType.GTEQ,
                TokenType.LT,
                TokenType.LTEQ,
                TokenType.LTEQ,
                TokenType.EQEQ,
                TokenType.NOTEQ,
            ]
        )

    # expression ::= term {( "-" | "+" ) term}
    def rule_expression(self):
        print("EXPRESSION")

        self.rule_term()
        # Can have 0 or more +/- expressions
        while self.check_tokens([TokenType.PLUS, TokenType.MINUS]):
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.rule_term()

    # term ::= unary { ( "/" | "*" ) unary}
    def rule_term(self) -> None:
        print("TERM")

        self.rule_unary()

        # Can have 0 or more *// and expressions
        while self.check_tokens([TokenType.ASTERISK, TokenType.SLASH]):
            self.emitter.emit(self.current_token.text)
            self.next_token()
            self.rule_unary()

    # unary ::= ["+" | "-"] primary
    def rule_unary(self) -> None:
        print("UNARY")

        # Optional unary +/-
        if self.check_tokens([TokenType.PLUS, TokenType.MINUS]):
            self.emitter.emit(self.current_token.text)
            self.next_token()

        self.rule_primary()

    def rule_primary(self) -> None:
        print(f"PRIMARY ({self.current_token.text})")

        if self.check_token(TokenType.NUMBER):
            self.emitter.emit(self.current_token.text)
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.current_token.text not in self.symbols:
                self.abort(
                    f"Referencing variable before assignment: {self.current_token.text}"
                )

            self.emitter.emit(self.current_token.text)
            self.next_token()
        else:
            self.abort(f"Unexpected token at {self.current_token.text}")
