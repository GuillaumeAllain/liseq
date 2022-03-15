__version__ = "1.0"

from pyparsing.helpers import nested_expr, alphas
from re import sub, compile, findall, MULTILINE
from ._codev_lang import codev_builtin_func, codev_macro_words
from copy import copy


fun_words = ["vie", "fie", "fma", "mtf"]
loop_words = ["for", "while", "unt"]
arith_words = [
    "..",
    "+",
    "-",
    "*",
    "**",
    "/",
    "==",
    ">",
    "<",
    "~=",
    "not=",
    "and",
    "or",
]
arith_trans = {}
for words in arith_words:
    arith_trans[words] = words
arith_trans["=="] = "="
arith_trans["from"] = ".."
arith_trans["to"] = ".."
arith_trans.update(dict.fromkeys(["~=", "not="], "<>"))
other_keys = ["yes", "no", "n", "y", "true", "false", "if", "else"]
definitions = ["local", "global", "num", "char"]

keywords = (
    fun_words
    + loop_words
    + arith_words
    + codev_macro_words
    + other_keys
    + codev_builtin_func
    + definitions
)
ldm_match = lambda exp: bool(compile(r"[abcefgijlqrstuwz][\dacilos]\b").match(exp))
attr_match = lambda exp: bool(compile(r"[\dacilos]\b").match(exp))
buf_func_match = lambda exp: bool(compile(r"buf\..*").match(exp))
codev_func_match = lambda exp: bool(compile(r"codev\..*").match(exp))
string_match = lambda exp: not exp == exp.replace('"', "") or exp.startswith(":")


def parse_var(exp):
    if (
        exp.lower() not in keywords
        and not exp.isnumeric()
        and not ldm_match(exp)
        and not buf_func_match(exp)
        and not string_match(exp)
        and not codev_func_match(exp)
    ):
        return True
    else:
        return False


def indent_whitespace(number):
    return "    ".join(["" for x in range(number + 1)])


def list2codev(exp_input, indent=0):
    exp = copy(exp_input)
    start = ""
    close = ""
    join = " "
    pre = indent_whitespace(indent)
    if len(exp) == 0:
        return ""
    elif isinstance(exp, str):
        if parse_var(exp):
            return exp if exp.startswith("^") else f"^{exp}"
        else:
            if exp.startswith(":"):
                return f'"{exp[1:]}"'
            else:
                return exp
    elif isinstance(exp[0], list):
        if len(exp[0]) >= 3 and exp[0][0] == "." and exp[0][1] in ["num", "str"]:
            exp.insert(0, exp[0][1])
            return list2codev(exp)
        join = "\n\n"
    elif exp[0] in fun_words:
        join = ";"
        close = "; go"
    elif exp[0] in loop_words:
        if len(exp) < 2:
            raise SyntaxError("Cannot parse loop")
        join = "\n"
        close = f"\n{indent_whitespace(indent)}end {exp[0]}"
        if exp[0] == "for":
            if not isinstance(exp[1], list) or len(exp[1]) < 3:
                raise SyntaxError("Cannot parse for loop init")
            start = f"{list2codev(exp[0])} {list2codev(exp[1][0])} {list2codev(exp[1][1:])}\n"
        elif exp[0] == "while":
            start = f"{list2codev(exp[0])} {list2codev(exp[1])}\n"
        elif exp[0] == "unt":
            start = f"{list2codev(exp[0])}\n"
            close += f" {exp[1]}"
        exp.pop(0)
        exp.pop(0)
        indent += 1
    elif exp[0] == "fct":
        if len(exp) < 5:
            raise SyntaxError("Cannot parse function")
        args = (
            ", ".join([list2codev(x) for x in exp[2]])
            if isinstance(exp[2][0], list)
            else list2codev(exp[2])
        )
        start = f"{indent_whitespace(indent)}fct @{exp[1]}({args})\n"
        join = "\n"
        close = f"\n{indent_whitespace(indent)}end fct {list2codev(exp[4])}"
        exp.pop(0)
        exp.pop(0)
        exp.pop(0)
        exp.pop(-1)
        indent += 1

    elif exp[0] == "if":
        if len(exp) < 2:
            raise SyntaxError("Cannot parse if")
        if len(exp) == 2:
            return f"if {list2codev(exp[1])}\n{indent_whitespace(indent)}end if"

        if len(exp) % 2:
            return (
                f"if {list2codev(exp[1])}\n{indent_whitespace(indent+1)}{list2codev(exp[2], indent=indent+1)}\n"
                # + "\n".join(exp[2])
                + "\n".join(
                    [
                        indent_whitespace(indent)
                        + "else if "
                        + list2codev(x[0])
                        + "\n"
                        + indent_whitespace(indent + 1)
                        + list2codev(x[1], indent=indent + 1)
                        + "\n"
                        for x in zip(exp[3::2], exp[4::2])
                    ]
                )
                + f"{indent_whitespace(indent)}end if"
            )
        elif not len(exp) % 2:
            return (
                f"if {list2codev(exp[1])}\n{indent_whitespace(indent+1)}{list2codev(exp[2],indent+1)}\n"
                + "\n".join(
                    [
                        indent_whitespace(indent)
                        + "else if "
                        + list2codev(x[0])
                        + "\n"
                        + indent_whitespace(indent + 1)
                        + list2codev(x[1], indent=indent + 1)
                        + "\n"
                        for x in zip(exp[3::2], exp[4::2])
                    ]
                )
                + (
                    f"{indent_whitespace(indent)}else\n{indent_whitespace(indent+1)}{list2codev(exp[-1], indent=indent+1)}\n"
                )
                + f"{indent_whitespace(indent)}end if"
            )
    # elif exp[0] == "else":
    #     pass

    elif exp[0] in codev_builtin_func:
        if len(exp[0]) < 2:
            raise SyntaxError("Cannot parse function call")
        start = f"{list2codev(exp[0])}("
        join = ","
        close = ")"
        exp.pop(0)
    elif exp[0] == "fctcall":
        if len(exp[0]) < 2:
            raise SyntaxError("Cannot parse function call")
        start = f"@{exp[1]}("
        join = ","
        close = ")"
        exp.pop(0)
        exp.pop(0)
    elif exp[0] == ".":
        # table_lookup
        if len(exp) < 3:
            raise SyntaxError("Cannot parse table lookup")
        start = f"{list2codev(exp[1])}("
        join = ","
        close = ")"
        exp.pop(0)
        exp.pop(0)
    elif exp[0] == "eva":
        # database lookup
        return f'({" ".join([list2codev(exp[x]) for x in range(1,len(exp))])})'
    elif exp[0] == "not":
        start = "not("
        close = ")"
        exp.pop(0)
    elif exp[0] in ["goto", "lbl"]:
        return f"{exp[0]} {exp[1]}"
    elif exp[0] == "compact":
        join = ";"
        exp.pop(0)

    elif "dro" in exp[0]:
        start = f"{exp[0].replace('drop','dro')} "
        exp.pop(0)
        close = list2codev(exp)
        exp = []

    elif exp[0] in ("num", "str", "local", "global"):
        start = f"{exp[0].replace('global', 'gbl').replace('local', 'lcl')} "
        if not isinstance(exp[1], str) and len(exp[1]) >= 3 and exp[1][1] in ["num", "str"]:
            var_size = ",".join(exp[1][2:])
        else:
            var_size = 0
        if var_size != 0:
            exp[2:] = [f"{x}({var_size})" for x in exp[2:]]
            if exp[0] in ["num", "str"]:
                exp.pop(0)
            else:
                exp[1] = exp[1][1]
        exp.pop(0)

    elif exp[0] in (alphas):
        if len(exp) != 2 and parse_var(exp[1]):
            raise SyntaxError("Buffer or Surface call error")
        if len(exp[1]) == 1:
            return f"{list2codev(exp[0]+exp[1])}"
        elif len(exp[1]) == 3 and exp[1][0] in arith_trans.keys():
            exp[1].append(0)
            return f"{exp[0]}{list2codev(exp[1])}"
        else:
            return f"{exp[0]}{list2codev(exp[1])}"

    elif exp[0] == "var":
        if len(exp) not in (3, 4):
            raise SyntaxError("Cannot parse var assignation")

        var_name = exp[-2] if isinstance(exp[-2], str) else exp[-2][1]
        var_type = (
            (exp[1] if isinstance(exp[1], str) else exp[1][1]) if len(exp) == 4 else ""
        )
        var_size = (
            (0 if isinstance(exp[1], str) else " ".join(exp[1][2:]))
            if len(exp) == 4
            else 0
        )
        if var_type != "":
            assign = (
                list2codev(
                    [
                        "local",
                        var_type,
                        var_name
                        if var_size == 0
                        else [".", var_name, *var_size.split(" ")],
                    ]
                )
                + "\n"
                + indent_whitespace(indent)
            )
        else:
            assign = ""
        return f"{assign}{list2codev(exp[-2])} == {list2codev(exp[-1])}"
    elif exp[0] in arith_trans.keys():
        if len(exp) not in (3, 4) or exp[0] not in arith_trans.keys():
            raise SyntaxError("Cannot parse lisp comparison")
        if len(exp) == 4:
            dist = int(exp[3])
            exp.pop(3)
        else:
            if arith_trans[exp[0]] == "..":
                dist = 0
            else:
                dist = 1
        parentflag1 = ["", ""] if isinstance(exp[1], str) else "()"
        parentflag2 = ["", ""] if isinstance(exp[2], str) else "()"
        return f"{parentflag1[0]}{list2codev(exp[1],indent=0) if not isinstance(exp[1],str) or not attr_match(exp[1]) else exp[1]}{parentflag1[1]}{' '*dist}{arith_trans[exp[0]]}{' '*dist}{parentflag2[0]}{list2codev(exp[2],indent=0) if not isinstance(exp[2],str) or not attr_match(exp[2]) else exp[2]}{parentflag2[1]}"
    pre = "    ".join(["" for x in range(indent + 1)])

    # surface_fnl_call
    # exp_up = [x[1:] if isinstance(x, str) and x[:2].lower() == ":s" else x for x in exp]
    exp_up = exp
    # resolve_subcalls
    if "\n" not in join:
        pre = ""
    exp_up = [pre + list2codev(y, indent=indent) for y in exp_up]

    if len(exp_up) == 1:
        return f"{start}{f'{join}'.join(exp_up)}{close}".strip()
    else:
        return f"{start}{f'{join}'.join(exp_up)}{close}".strip()


def expand_macro(program_input):
    program = copy(program_input)
    codev_parse_input = compile(r"codev.parseinput(.*)")
    if len(codev_parse_input.findall(program)) > 0:
        parse_inputs = findall(
            r'(?:"[\w\s]+")|(?:\w+)', codev_parse_input.findall(program)[0]
        )
        if bool((len(parse_inputs) - 1) % 3):
            raise SyntaxError("Parse Inputs error")
        parse_func_name = parse_inputs[0].replace('"', "")
        parse_inputs = [parse_inputs[1:][x::3] for x in range(3)]
        parse_inputs[2] = [f"""{x.replace('"', "")}""" for x in parse_inputs[2]]
        program = codev_parse_input.sub(
            list2codev(
                [
                    ["buf.emp.find", "bparseinput"],
                    ["buf.emp.find", "bparsesyntax"],
                    ["buf", "del", ["b", "bparseinput"]],
                    [
                        "buf",
                        "put",
                        ["b", "bparsesyntax"],
                        ["i", ["+", "l", "1"]],
                        ["j", "1"],
                        f'''"syntax: {parse_func_name} {' '.join([f'[{x}]' for x in parse_inputs[2]])} <----- uses text qualifiers entered in any order"''',
                    ],
                    [
                        "buf",
                        "put",
                        ["b", "bparsesyntax"],
                        ["i", ["+", "l", "1"]],
                        ["j", "1"],
                        '"      - or - "',
                    ],
                    [
                        "buf",
                        "put",
                        ["b", "bparsesyntax"],
                        ["i", ["+", "l", "1"]],
                        ["j", "1"],
                        f'''"syntax: {parse_func_name} {' '.join(parse_inputs[2])} <----- uses numeric inputs in this order only "''',
                    ],
                    ["buf", "del", ["b", "bparseinput"]],
                    [
                        "for",
                        ["input", "1", str(len(parse_inputs) - 1)],
                        [
                            "buf",
                            "put",
                            ["b", "bparseinput"],
                            [
                                "i",
                                [
                                    "+",
                                    "l",
                                    "1",
                                ],
                            ],
                            [".", "rfstr", "input"],
                        ],
                    ],
                    ["in", '"cv_macro:ParseInputs.seq"', "bparseinput"],
                    [
                        "for",
                        ["i", "1", ["eva", "buf.lst", ["b", "bparseinput"]]],
                        [
                            "var",
                            "str",
                            "parseinput",
                            [
                                "eva",
                                "buf.str",
                                ["b", "bparseinput"],
                                ["i", "i"],
                                ["j", "1"],
                            ],
                        ],
                        [
                            "var",
                            "str",
                            "parsequalifier",
                            [
                                "eva",
                                "buf.str",
                                ["b", "bparseinput"],
                                ["i", "i"],
                                ["j", "2"],
                            ],
                        ],
                        [
                            "var",
                            "num",
                            "parsevalue",
                            [
                                "str_to_num",
                                [
                                    "eva",
                                    "buf.str",
                                    ["b", "bparseinput"],
                                    ["i", "i"],
                                    ["j", "3"],
                                ],
                            ],
                        ],
                        [
                            "if",
                            [
                                "or",
                                ["eva", ["==", ["upcase", "parseinput"], '"H"']],
                                ["eva", ["==", ["upcase", "parseinput"], '"HELP"']],
                            ],
                            [
                                ["out", "y"],
                                "wri",
                                ["buf", "lis", "nol", ["b", "bparsesyntax"]],
                                ["goto", "end"],
                            ],
                            *[
                                item
                                for sublist in zip(
                                    [
                                        ["==", "parsequalifier", x.upper()]
                                        for x in parse_inputs[0]
                                    ],
                                    [
                                        ["var", "num", y, "parsevalue"]
                                        for y in parse_inputs[1]
                                    ],
                                )
                                for item in sublist
                            ],
                            ["==", "parsequalifier", '"IsNum"'],
                            [
                                "if",
                                *[
                                    item
                                    for sublist in zip(
                                        [
                                            ["==", "i", str(x + 1)]
                                            for x in range(len(parse_inputs[1]))
                                        ],
                                        [
                                            ["var", x, "parsevalue"]
                                            for x in parse_inputs[1]
                                        ],
                                    )
                                    for item in sublist
                                ],
                            ],
                            [
                                ["ver", "n"],
                                ["out", "y"],
                                "wri",
                                [
                                    "var",
                                    "num",
                                    "result",
                                    ["cverror", '"Unrecognized input"', "0"],
                                ],
                                ["wri", ["concat", '"Invalid input: "', "parseinput"]],
                                ["wri"],
                                ["buf", "lis", "nol", ["b", "bparsesyntax"]],
                                ["wri"],
                                ["goto", "end"],
                            ],
                        ],
                    ],
                ]
            ),
            program,
        )
        program = f'rfd ""\n{program}'
    program_start = copy(program)

    buf_empty_macro = compile(r"buf.emp.find\s\^(.*)")
    if len(buf_empty_macro.findall(program)) > 0:
        program = buf_empty_macro.sub(
            list2codev(
                [
                    ["var", "num", r"\1", "1"],
                    [
                        "while",
                        ["not", ["buf.emp", ["b", r"\1"]]],
                        ["var", r"\1", ["+", r"\1", "1"]],
                    ],
                    [
                        "buf",
                        "put",
                        ["b", r"\1"],
                        [
                            "i",
                            [
                                "+",
                                "l",
                                "1",
                            ],
                        ],
                        ":placeover",
                    ],
                ]
            ),
            program,
        )
    codev_supress_macro = compile(r"codev\.supressoutput.*")
    if len(codev_supress_macro.findall(program)) > 0:
        program = codev_supress_macro.sub(
            list2codev(
                [
                    [
                        "if",
                        ["eva", "out"],
                        ["var", "str", "origoutsetting", '"y"'],
                        ["var", "origoutsetting", '"n"'],
                    ],
                    ["var", "str", "outvar", '"n"'],
                    ["out", "outvar"],
                    [
                        "if",
                        ["eva", "ver"],
                        ["var", "str", "origverSetting", '"y"'],
                        ["var", "origversetting", '"n"'],
                    ],
                    ["ver", "n"],
                ]
            ),
            program,
        )

    lblend = f"{';'.join([list2codev(['buf', 'del', ['b', x]]) for x in buf_empty_macro.findall(program_start)])}"
    if codev_supress_macro.findall(program_start) != []:
        add_out = list2codev(
            [
                ["out", "origoutsetting"],
                ["if", ["==", "origversetting", '"y"'], ["ver", "y"]],
            ]
        )
        lblend = f"{lblend}\n{add_out}"
    program = f"{program}\nlbl end\n{lblend}" if lblend != "" else program
    return program


def move_def_to_top(program_input):
    program = copy(program_input)
    lclstr = compile(r"lcl\sstr.*")
    lclnum = compile(r"lcl\snum.*")
    str_def = lclstr.findall(program)
    num_def = lclnum.findall(program)
    definitions = (
        f"lcl str {' '.join(set([y for x in str_def for y in x.split()[2:]]))}\n"
        if len(str_def) > 0
        else ""
    )
    definitions += (
        f"lcl num {' '.join(set([y for x in num_def for y in x.split()[2:]]))}\n"
        if len(num_def) > 0
        else ""
    )

    program = f"""{definitions}{lclnum.sub("", lclstr.sub("", program))}"""
    return sub("\n$", "", sub("\n\s*\n", "\n", program), MULTILINE)


def transpiler(program):
    program = "\n".join(
        [x for x in program.split("\n") if not x.lstrip().startswith(";")]
    )
    program = sub(r"\[", r"(", program)
    program = sub(r"]", ")", program)
    ast = nested_expr().parseString(f"({program})")[0].asList()
    return move_def_to_top(expand_macro(list2codev(ast)))
