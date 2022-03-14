import argparse
from liseq.core import transpiler

parser = argparse.ArgumentParser(
    description="Transpile s-exp to macro-plus CODEV language."
)

parser.add_argument("filename", type=str, help="Input filename (Required)")

parser.add_argument(
    "-o",
    "--output",
    type=str,
    help="Output file location. Default: output to terminal",
    default=None,
)

args = parser.parse_args()


def main():
    with open(args.filename, "r") as file:
        program = file.read()
    output_string = transpiler(program)
    if args.output is not None:
        with open(args.output, "w") as file:
            file.write(output_string)
    else:
        print(output_string)


if __name__ == "__main__":
    main()
