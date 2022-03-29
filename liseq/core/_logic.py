__version__ = "1.0"

from pyparsing.helpers import nested_expr, alphas
from re import sub, compile, findall, search, escape, MULTILINE
from copy import copy


loop_words = ["for", "while", "unt"]
arith_words = [
    "..",
    "+",
    "-",
    "**",
    "*",
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
keywords = ["yes", "no", "n", "y", "true", "false", "if", "else", "m", "t"]
arith_symbols = [
    x for x in [sub(f"[{alphas}]+", "", y) for y in arith_trans.keys()] if x
]
special_letter_match = lambda exp: bool(compile(r"[abcefgijolqrstuwz]$").match(exp))
attr_match = lambda exp: bool(compile(r"[\dacilos]$").match(exp))
string_match = lambda exp: not exp == exp.replace('"', "") or exp.startswith(":")


def is_number(s):
    """Returns True is string is a number."""
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_arith(exp):
    if string_match(exp):
        return False, None
    elif is_number(exp) and exp[0] not in arith_symbols or exp[0] == "-":
        return False, None
    output_bool = False
    for symbol in arith_symbols:
        split_output = exp.split(symbol)
        if len(split_output) > 1:
            output_bool = True
            split_output.insert(0, symbol)
            split_output = [x for x in split_output if x]
            break
        else:
            split_output
    return (output_bool, split_output if output_bool else None)


def parse_var(exp):
    if (
        not is_number(exp.lower())
        and not string_match(exp.lower())
        and exp not in keywords
    ):
        return True
    else:
        return False


# def parse_var(exp):
#     return True


def indent_whitespace(number):
    return "    ".join(["" for x in range(number + 1)])


def list2codev(exp_input, indent=0, scope="lcl"):
    exp = copy(exp_input)
    start = ""
    close = ""
    join = " "
    pre = indent_whitespace(indent)
    if isinstance(exp, list) and len(exp) > 0:
        exp[0] = exp[0].lower() if isinstance(exp[0], str) else exp[0]
    if len(exp) == 0:
        return ""
    elif isinstance(exp, str):
        arith_bool, arith_output = is_arith(exp)

        if exp == "nil":
            return ""
        elif arith_bool:
            return list2codev(arith_output)
        elif parse_var(exp):
            return exp if exp.startswith("^") else f"^{exp}"
        else:
            if exp.startswith(":"):
                return f'"{exp[1:]}"'
            else:
                return exp
    elif isinstance(exp[0], list):
        join = "\n\n"
    elif exp[0] == "raw":
        for subindex, substring in enumerate(exp[1:]):
            if not isinstance(substring, str):
                raise SyntaxError(f"Cannot parse subelement of type: {type(substring)}")
            if substring.startswith(":"):
                exp[subindex + 1] = substring[1:]
            elif substring.startswith('"') and substring.endswith('"'):
                exp[subindex + 1] = substring[1:-1]
            else:
                raise SyntaxError("Cannot parse substring")
        return "\n".join(exp[1:])
    elif exp[0] in ["tset"]:
        if isinstance(exp[1], str):
            exp[1] = [
                exp[1],
            ]
        if isinstance(exp[2], str):
            exp[2] = [
                exp[2],
            ]
        if isinstance(exp[2][0], str):
            return list2codev(
                [
                    [
                        [
                            ["set", ["nth", list2codev(e), str(xi + 1)], list2codev(x)]
                            for xi, x in enumerate(exp[2])
                        ]
                        for ei, e in enumerate(exp[1])
                    ]
                ]
            )
        elif isinstance(exp[2][0], list):
            return list2codev(
                [
                    [
                        [
                            [
                                [
                                    "set",
                                    ["nth", list2codev(e), str(yi + 1), str(xi + 1)],
                                    list2codev(x[yi]),
                                ]
                                for xi, x in enumerate(exp[2])
                            ]
                            for yi in range(len(exp[2][0]))
                        ]
                        for ei, e in enumerate(exp[1])
                    ]
                ]
            )
    elif exp[0] in ["set", "setq"]:
        if len(exp[1:]) % 2:
            raise SyntaxError("Cannot parse set statement: " + str(exp))
        output_string = ""
        for var, val in zip(exp[1::2], exp[2::2]):
            if isinstance(var, list) and len(var) >= 2 and var[0] in ["num", "str"]:
                output_string += (
                    list2codev(var, scope=scope) + "\n" + indent_whitespace(indent)
                )

                var = var[1]
            output_string += (
                f"{list2codev(var,scope=scope)} == {list2codev(val,scope=scope)}\n"
            )
        return output_string

    elif exp[0] in ["setd"]:
        if len(exp[1:]) % 2:
            raise SyntaxError("Cannot parse set statement: " + str(exp))
        for var, val in zip(exp[1::2], exp[2::2]):
            output_string = ""
            if isinstance(var, list) and len(var) >= 2:
                output_string += " ".join(
                    [x if isinstance(x, str) else list2codev(x) for x in var]
                )
                output_string += " "
                var = var[1]
            else:
                output_string += f"{var} "
            output_string += list2codev(val) + "\n" + indent_whitespace(indent)
        return output_string

    elif exp[0] == "database":
        return f'({" ".join([x if isinstance(x, str) else list2codev(x) for x in exp[1:]])})'

    elif exp[0] in ["num", "str"]:
        if len(exp) < 2:
            raise SyntaxError(
                "Var definition should at minimum include type and name (type name): "
                + str(exp)
            )
        if scope == "fundef":
            return f"{exp[0]} {list2codev(exp[1])}"
        else:
            return list2codev(["local"] + exp, scope=scope)

    elif exp[0] in ("local", "global"):
        # print(exp)
        # if len(exp[2:]) % 2:
        #     raise SyntaxError("Cannot parse var definition")
        start = f"{exp[0].replace('global', 'gbl').replace('local', scope)} "
        start += f"{exp[1]} "
        exp.pop(0)
        exp.pop(0)
        exp = [list2codev(x, scope=scope) for x in exp]
    elif exp[0] in ["nth", "."]:

        if len(exp) < 3:
            raise SyntaxError("Cannot parse array access: " + exp)

        var_size = ",".join(exp[2:])
        return f"{list2codev(exp[1])}({var_size})"

    elif exp[0] in ["fct", "fn", "defun"]:
        if len(exp) < 3:
            raise SyntaxError(
                """Function statement must contain at least 3 args,
                    (defun fun_name ((arg1 def) [arg2 def] ...) body (return_variable)):"""
                + str(exp)
            )
        exp[2] = (
            [x if isinstance(x, list) else ["num", x] for x in exp[2]]
            if isinstance(exp[2], list)
            else ["num", exp[2]]
        )
        args = (
            ", ".join([list2codev(x, scope="fundef") for x in exp[2]])
            if isinstance(exp[2][0], list)
            else list2codev(exp[2], scope="fundef")
        )
        start = f"{indent_whitespace(indent)}fct @{exp[1]}({args})\n"
        join = "\n"
        close = (
            f"\n{indent_whitespace(indent)}end fct {list2codev(exp[-1],scope=scope)}"
        )
        exp.pop(0)
        exp.pop(0)
        exp.pop(0)
        exp.pop(-1)
        indent += 1
        scope = "fctlcl"

    elif exp[0] in ["callu"]:
        exp[0] = "call"
        exp[1] = "@" + str(exp[1])
        return list2codev(exp, scope=scope, indent=indent)
    elif exp[0] in ["call"]:
        if len(exp[0]) < 2:
            raise SyntaxError("Cannot parse function call")
        start = f"{exp[1]}("
        join = ","
        close = ")"
        exp.pop(0)
        exp.pop(0)
    elif exp[0] in ["load", "require", "in"]:
        start = "in "
        exp.pop(0)
    elif exp[0] in ["print", "format", "wri"]:
        start = "wri "
        exp.pop(0)
    elif exp[0] == "option":
        start = exp[1] + "\n"
        join = "\n"
        close = "\ngo"
        indent += 1
        exp.pop(0)
        exp.pop(0)

    elif exp[0] in ["goto", "lbl", "label", "got"]:
        return f"{sub('label','lbl',exp[0])} {exp[1]}"

    elif exp[0] in loop_words:
        if len(exp) < 2:
            raise SyntaxError("Cannot parse loop")
        join = "\n"
        close = f"\n{indent_whitespace(indent)}end {exp[0]}"
        if exp[0] == "for":
            if not isinstance(exp[1], list) or len(exp[1]) < 3:
                raise SyntaxError("Cannot parse for loop init")
            start = f"{exp[0]} {list2codev(exp[1][0],scope=scope)} {' '.join([list2codev(x) for x in exp[1][1:]])}\n"
        elif exp[0] == "while":
            start = (
                f"{list2codev(exp[0],scope=scope)} {list2codev(exp[1],scope=scope)}\n"
            )
        elif exp[0] == "unt":
            start = f"{list2codev(exp[0],scope=scope)}\n"
            close += f" {exp[1]}"
        exp.pop(0)
        exp.pop(0)
        indent += 1

    elif "dro" in exp[0]:
        return "dro ^" + " ^".join(exp[1:])

    elif exp[0] == "not":
        start = "not("
        close = ")"
        exp.pop(0)
    elif exp[0] == "if":
        if len(exp) < 2:
            raise SyntaxError("Cannot parse if")
        if len(exp) == 2:
            return f"if {list2codev(exp[1],scope=scope)}\n{indent_whitespace(indent)}end if"

        if len(exp) % 2:
            return (
                f"if {list2codev(exp[1],scope=scope)}\n{indent_whitespace(indent+1)}{list2codev(exp[2], indent=indent+1,scope=scope)}\n"
                # + "\n".join(exp[2])
                + "\n".join(
                    [
                        indent_whitespace(indent)
                        + "else if "
                        + list2codev(x[0], scope=scope)
                        + "\n"
                        + indent_whitespace(indent + 1)
                        + list2codev(x[1], indent=indent + 1, scope=scope)
                        + "\n"
                        for x in zip(exp[3::2], exp[4::2])
                    ]
                )
                + f"{indent_whitespace(indent)}end if"
            )
        elif not len(exp) % 2:
            return (
                f"if {list2codev(exp[1],scope=scope)}\n{indent_whitespace(indent+1)}{list2codev(exp[2],indent+1,scope=scope)}\n"
                + "\n".join(
                    [
                        indent_whitespace(indent)
                        + "else if "
                        + list2codev(x[0], scope=scope)
                        + "\n"
                        + indent_whitespace(indent + 1)
                        + list2codev(x[1], indent=indent + 1, scope=scope)
                        + "\n"
                        for x in zip(exp[3::2], exp[4::2])
                    ]
                )
                + (
                    f"{indent_whitespace(indent)}else\n{indent_whitespace(indent+1)}{list2codev(exp[-1], indent=indent+1,scope=scope)}\n"
                )
                + f"{indent_whitespace(indent)}end if"
            )

    elif exp[0] in arith_trans.keys():
        if len(exp) != 3 or exp[0] not in arith_trans.keys():
            raise SyntaxError(
                "Arithmetic statement must be of the form (arith arg1 arg2): "
                + str(exp)
            )
        # elif len(exp) >= 4:
        #     raise SyntaxError("Cannot parse s-expr arithmetics")
        if arith_trans[exp[0]] == ".." or (
            isinstance(exp[1], list)
            and len(exp[1]) == 2
            and special_letter_match(exp[1][0])
        ):
            dist = 0
        else:
            dist = 1
        parentflag1 = (
            ["", ""]
            if isinstance(exp[1], str)
            or not len(exp[1]) == 3
            or not exp[1][0] in arith_trans.keys()
            else "()"
        )
        parentflag2 = (
            ["", ""]
            if isinstance(exp[2], str)
            or not len(exp[2]) == 3
            or not exp[2][0] in arith_trans.keys()
            else "()"
        )
        return f"{'(' if dist!=0 else ''}{parentflag1[0]}{list2codev(exp[1],indent=0,scope=scope) if not isinstance(exp[1],str) or not attr_match(exp[1]) else exp[1]}{parentflag1[1]}{' '*dist}{arith_trans[exp[0]]}{' '*dist}{parentflag2[0]}{list2codev(exp[2],indent=0,scope=scope) if not isinstance(exp[2],str) or not attr_match(exp[2]) else exp[2]}{parentflag2[1]}{')' if dist!=0 else ''}"

    elif special_letter_match(exp[0]):
        if len(exp) != 2:
            raise SyntaxError("Arguments must be only 2: " + exp)
        return f"{exp[0]}{exp[1] if isinstance(exp[1], str) and special_letter_match(exp[1]) else list2codev(exp[1])}"
    else:
        if len(exp) == 1:
            return list2codev(exp[0], scope=scope)
        else:
            raise SyntaxError("Cannot parse expr: " + str(exp_input))

    pre = "    ".join(["" for x in range(indent + 1)])

    exp_up = exp
    # resolve_subcalls
    if "\n" not in join:
        pre = ""
    exp_up = [pre + list2codev(y, indent=indent, scope=scope) for y in exp_up]

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
                        ["raw", '"il+1"'],
                        ["j", "1"],
                        f'''"syntax: {parse_func_name} {' '.join([f'[{x}]' for x in parse_inputs[2]])} <----- uses text qualifiers entered in any order"''',
                    ],
                    [
                        "buf",
                        "put",
                        ["b", "bparsesyntax"],
                        ["raw", '"il+1"'],
                        ["j", "1"],
                        '"      - or - "',
                    ],
                    [
                        "buf",
                        "put",
                        ["b", "bparsesyntax"],
                        ["raw", '"il+1"'],
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
                            ["raw", '"il+1"'],
                            [".", "rfstr", "input"],
                        ],
                    ],
                    ["in", '"cv_macro:ParseInputs.seq"', "bparseinput"],
                    [
                        "for",
                        ["i", "1", ["eva", "buf.lst", ["b", "bparseinput"]]],
                        [
                            "set",
                            [
                                "str",
                                "parseinput",
                            ],
                            [
                                "eva",
                                "buf.str",
                                ["b", "bparseinput"],
                                ["i", "^i"],
                                ["j", "1"],
                            ],
                        ],
                        [
                            "set",
                            [
                                "str",
                                "parsequalifier",
                            ],
                            [
                                "eva",
                                "buf.str",
                                ["b", "bparseinput"],
                                ["i", "^i"],
                                ["j", "2"],
                            ],
                        ],
                        [
                            "set",
                            [
                                "num",
                                "parsevalue",
                            ],
                            [
                                "str_to_num",
                                [
                                    "eva",
                                    "buf.str",
                                    ["b", "bparseinput"],
                                    ["i", "^i"],
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
                                        ["set", ["num", y], "parsevalue"]
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
                                            ["==", "^i", str(x + 1)]
                                            for x in range(len(parse_inputs[1]))
                                        ],
                                        [
                                            ["set", x, "parsevalue"]
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
                    ["set", ["num", r"\1"], "1"],
                    [
                        "while",
                        ["not", ["database", "buf.emp", ["b", r"\1"]]],
                        ["set", r"\1", ["+", r"\1", "1"]],
                    ],
                    [
                        "setd",
                        [
                            "buf",
                            "put",
                            ["b", r"\1"],
                            ["raw", '"il+1"'],
                        ],
                        ":placeover",
                    ],
                ]
            ),
            program,
        )
    codev_supress_macro = compile(r"codev\.suppressoutput.*")
    if len(codev_supress_macro.findall(program)) > 0:
        program = codev_supress_macro.sub(
            list2codev(
                [
                    [
                        "if",
                        ["database", "out"],
                        ["set", ["str", "origoutsetting"], '"y"'],
                        ["set", "origoutsetting", '"n"'],
                    ],
                    ["set", ["str", "outvar"], '"n"'],
                    ["setd", "out", "outvar"],
                    [
                        "if",
                        ["database", "ver"],
                        ["set", ["str", "origverSetting"], '"y"'],
                        ["set", "origversetting", '"n"'],
                    ],
                    ["setd", "ver", "n"],
                ]
            ),
            program,
        )

    lblend = f"{';'.join([list2codev(['setd',['buf', 'del'], ['b', x]]) for x in buf_empty_macro.findall(program_start)])}"
    if codev_supress_macro.findall(program_start) != []:
        add_out = list2codev(
            [
                ["setd", "out", "origoutsetting"],
                ["if", ["==", "origversetting", '"y"'], ["setd", "ver", "y"]],
            ]
        )
        lblend = f"{lblend}\n{add_out}"
    program = f"{program}\nlbl end\n{lblend}" if lblend != "" else program
    return program


def move_def_to_top(program_input):
    program = copy(program_input)
    lclstr = compile(r"^\s*lcl\sstr.*", MULTILINE)
    lclnum = compile(r"^\s*lcl\snum.*", MULTILINE)
    # lclfctget = compile(r"(^\s*fct.*)", MULTILINE)
    # fct_local_get = lclfctget.findall(program)

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

    if search("rfd.*", program.split("\n")[0]):
        first_line = program.split("\n")[0]
        program = sub(escape(first_line), "", program)
        definitions = first_line + "\n" + definitions
    program = f"""{definitions}{lclnum.sub("", lclstr.sub("", program))}"""
    fct_local_get = findall(r"(^\s*fct.*)", program, MULTILINE)
    fct_local_get = fct_local_get
    fct_index = [
        i for i, item in enumerate(fct_local_get) if search(r"^\s*fct\s.*", item)
    ]
    program = sub(r"(fctlcl.*)", "", program, MULTILINE)
    for ii, xx in enumerate(fct_index):
        if len(fct_index) > (ii + 1):
            elements = fct_local_get[xx + 1 : fct_index[ii + 1]]
        else:
            elements = fct_local_get[xx + 1 :]
        elements = [x.strip().replace("fctlcl", "lcl") for x in elements]
        elements_str = [x for x in elements if lclstr.search(x)]
        elements_num = [x for x in elements if lclnum.search(x)]
        definitions = (
            f"{indent_whitespace(1)}lcl str {' '.join(set([y for x in elements_str for y in x.split()[2:]]))}\n"
            if len(elements_str) > 0
            else ""
        )
        definitions += (
            f"{indent_whitespace(1)}lcl num {' '.join(set([y for x in elements_num for y in x.split()[2:]]))}\n"
            if len(elements_num) > 0
            else ""
        )
        program = sub(
            escape(fct_local_get[xx]),
            fct_local_get[xx] + r"\n" + definitions,
            program,
            MULTILINE,
        )
    return sub("\n$", "", sub("\n\s*\n", "\n", program), MULTILINE)


def transpiler(program):
    program = "\n".join(
        [x for x in program.split("\n") if not x.lstrip().startswith(";")]
    )
    program = sub(r"\[", r"(", program)
    program = sub(r"]", ")", program)
    ast = nested_expr().parseString(f"({program})")[0].asList()
    return move_def_to_top(expand_macro(list2codev(ast)))
