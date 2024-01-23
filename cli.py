import argparse
import os
import sys

from attrs import define


@define
class Options:
    input: str
    output: str


def parse():
    parser = argparse.ArgumentParser(description="todo: write a description here", add_help=True)

    parser.add_argument("--input", type=str, help="target directory to scan", required=True)
    parser.add_argument("--output", type=str, help="target directory to write into", required=True)

    if len(sys.argv) < 2:
        parser.print_help()
        parser.exit(1)

    args = parser.parse_args()

    if not os.path.isdir(args.input):
        raise NotADirectoryError(f"Folder \"{args.input}\" is not a directory!")
    if not os.path.isdir(args.output):
        raise NotADirectoryError(f"Folder \"{args.output}\" is not a directory!")

    opt = Options(args.input, args.output)
    return opt
