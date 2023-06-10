from lexer import Lexer
from parser import Parser
from emitter import Emitter
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
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        dest="output",
        action="store",
        type=str,
        help="destination file",
    )
    return parser


def main():
    print("Teeny Tiny Compiler")
    parser = get_argparser()
    args = parser.parse_args()

    with open(args.file, "r") as input_file:
        source = input_file.read()

    lexer = Lexer(source)
    emitter = Emitter(args.output)
    parser = Parser(lexer, emitter)

    parser.rule_program()
    emitter.write_file()

    print("Transpiling completed.")


if __name__ == "__main__":
    main()
