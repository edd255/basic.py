from lexer import Lexer
from parser import Parser
from argparse import ArgumentParser


def get_argparser() -> ArgumentParser:
    parser = ArgumentParser(description="Teeny Tiny Compiler")
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        dest="file",
        action="store",
        type=str,
        help="source file",
    )
    return parser


def main():
    print("Teeny Tiny Compiler")
    parser = get_argparser()
    args = parser.parse_args()

    with open(args.file, "r") as input_file:
        source = input_file.read()

    lexer = Lexer(source)
    parser = Parser(lexer)
    parser.rule_program()
    print("Parsing completed.")


if __name__ == "__main__":
    main()
