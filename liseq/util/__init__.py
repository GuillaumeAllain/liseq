from pyparsing.helpers import nested_expr
from re import sub


def liseq_to_list(program):
    program = "\n".join(
        [x for x in program.split("\n") if not x.lstrip().startswith(";")]
    )
    program = sub(r"\[", r"(", program)
    program = sub(r"]", ")", program)
    ast = nested_expr().parseString(f"({program})")[0].asList()
    return ast


def list_depth(L):
    return isinstance(L, list) and max(map(list_depth, L)) + 1


def open_file(filename):
    with open(filename, "r") as f:
        return f.read()
