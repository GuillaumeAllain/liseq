__version__ = "1.0"

from pyparsing.helpers import alphas
from re import sub, compile, findall, search, escape, MULTILINE
from copy import copy
from liseq.macro import macro_dict, macro_dict_raw
from liseq.util import liseq_to_list

set_words = ["APE", "EPD", "FNO", "NA", "NAO", "CIG", "VIX", "VIY"]
loop_words = ["for", "while", "unt"]
bool_list = ["=", "<=", ">=", ">", "<", "and", "or", "<>"]
arith_words = bool_list + [
    "..",
    "+",
    "-",
    "**",
    "*",
    "/",
]
arith_trans = {}
for words in arith_words:
    arith_trans[words] = words
# arith_trans["=="] = "="
# arith_trans["eq"] = "="
arith_trans["from"] = ".."
arith_trans["to"] = ".."
# arith_trans["leq"] = "<="
# arith_trans["geq"] = ">="
arith_trans.update(dict.fromkeys(["~=", "not=", "neq"], "<>"))
arith_trans.update(dict.fromkeys(["==", "eq"], "="))
arith_trans.update(dict.fromkeys(["<=", "leq"], "<="))
arith_trans.update(dict.fromkeys([">=", "geq"], ">="))
keywords = ["yes", "no", "n", "y", "true", "false", "if", "else", "m", "t"]
arith_symbols = [
    x for x in [sub(f"[{alphas}]+", "", y) for y in arith_trans.keys()] if x
]
special_letter_match = lambda exp: bool(compile(r"[abcefgijolqrstuwzL]$").match(exp))
attr_match = lambda exp: bool(compile(r"[\dacilos]$").match(exp))
string_match = lambda exp: not exp == exp.replace('"', "") or exp.startswith(":")


plt_options = ["vie", "fie", "rim", "foo", "fma"]
ras_options = ["v3d"]
END_ACC = ""


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


def indent_whitespace(number):
    return "    ".join(["" for x in range(number + 1)])


def list2codev(exp_input, indent=0, scope="lcl"):
    global END_ACC
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
        elif arith_bool and not (exp.startswith("`") or exp.startswith("'")):
            return list2codev(arith_output)
        else:
            if exp.startswith(":") or exp.startswith("`") or exp.startswith("'"):
                return f'"{exp[1:]}"'
            else:
                return exp
    elif isinstance(exp[0], list):
        join = "\n\n"
    elif exp[0] == "raw":
        for subindex, substring in enumerate(exp[1:]):
            if isinstance(substring, list):
                substring.insert(0, "raw")
                exp[subindex + 1] = list2codev(substring)
                # raise SyntaxError(f"Cannot parse subelement of type: {type(substring)}")
            elif substring.startswith(":"):
                exp[subindex + 1] = substring[1:]
            elif substring.startswith('"') and substring.endswith('"'):
                exp[subindex + 1] = substring[1:-1]
            # else:
            #     raise SyntaxError("Cannot parse substring: "+str(exp))
        return " ".join(exp[1:])
    elif exp[0] in ["tset"]:
        # FIXME: Tablename (var quelquechos)
        shape = None
        if isinstance(exp[1], str):
            exp[1] = [
                exp[1],
            ]
        elif isinstance(exp[1], list) and exp[1][0] in ["nth", "."]:
            shape = exp[1][1:-1]
            exp[1] = [
                exp[1][-1],
            ]
        if isinstance(exp[2], str):
            exp[2] = [
                exp[2],
            ]

        if isinstance(exp[2][0], str) or (shape is not None and len(shape) == 1):
            return list2codev(
                [
                    [
                        [
                            ["set", ["nth", str(xi + 1), list2codev(e)], list2codev(x)]
                            if e != "var"
                            else []
                            for xi, x in enumerate(exp[2])
                        ]
                        for ei, e in enumerate(exp[1])
                    ]
                ],
                scope=scope,
                indent=indent,
            )
        elif isinstance(exp[2][0], list):
            return list2codev(
                [
                    [
                        [
                            [
                                [
                                    "set",
                                    ["nth", str(yi + 1), str(xi + 1), list2codev(e)]
                                    if e != "var"
                                    else [],
                                    list2codev(x[yi]),
                                ]
                                if list2codev(x[yi]).strip() != ""
                                else ""
                                for xi, x in enumerate(exp[2])
                            ]
                            for yi in range(len(exp[2][0]))
                        ]
                        for ei, e in enumerate(exp[1])
                    ]
                ],
                scope=scope,
                indent=indent,
            )
    elif exp[0] in ["arg"]:
        if len(exp) < 2:
            raise SyntaxError("Arg statement should at least contain one variable")
        return list2codev(
            [
                y if y.startswith("#") else "#" + y
                for y in [list2codev(x) for x in exp[1:]]
            ],
            scope=scope,
            indent=indent,
        )
    elif exp[0] in ["var"]:
        if len(exp) < 2:
            raise SyntaxError("Var statement should at least contain one variable")
        return list2codev(
            [
                y if y.startswith("^") else "^" + y
                for y in [list2codev(x) for x in exp[1:]]
            ],
            scope=scope,
            indent=indent,
        )
    elif exp[0] in macro_dict.keys():
        args = {}
        scope += "noout"
        if len(exp) >= 2:
            for i, arg in enumerate(exp[1:]):
                args[f"__codev_arg{str(i+1)}"] = arg
        return list2codev(macro_dict[exp[0]](args), scope=scope, indent=indent)
    elif exp[0] in ["set", "setq"]:
        if len(exp[1:]) % 2:
            raise SyntaxError("Cannot parse set statement: " + str(exp))
        if type(exp[1]) is str and exp[1].upper() in set_words:
            return "set " + list2codev(exp[1:])
        output_string = ""
        for var, val in zip(exp[1::2], exp[2::2]):
            if isinstance(var, list) and len(var) >= 2 and var[0] in ["num", "str"]:
                output_string += (
                    list2codev(var, scope=scope) + "\n" + indent_whitespace(indent)
                )

                var = var[1]
            output_string += f"{list2codev(['var',var] if var[0]!='@' else var,scope=scope)} == {list2codev(val,scope=scope)}\n"
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

    elif "codev" in exp[0]:
        exp.insert(0, "raw")
        return list2codev(exp)
    elif exp[0] == "database":
        return f'({" ".join([x if isinstance(x, str) else list2codev(x) for x in exp[1:]])})'

    elif exp[0] in ["num", "str"]:
        if len(exp) < 2:
            raise SyntaxError(
                "Var definition should at minimum include type and name (type name): "
                + str(exp)
            )
        if "fundef" in scope:
            return f"{exp[0]} {list2codev(['var', list2codev(exp[1])])}"
        else:
            return list2codev(["local"] + exp, scope=scope)

    elif exp[0] in ("local", "global"):
        start = f"{exp[0].replace('global', 'gbl').replace('local', 'lclaut' if 'aut' in scope else ('fctlcl' if 'fct' in scope else 'lcl'))} "
        start += f"{exp[1]} "
        exp.pop(0)
        exp.pop(0)
        exp = [list2codev(["var"] + [x], scope=scope) for x in exp]
    elif exp[0] in ["nth", "."]:

        if len(exp) < 3:
            raise SyntaxError("Cannot parse array access: " + exp)

        var_size = ",".join([list2codev(x) for x in exp[1:-1]])
        return f"{list2codev(['var',exp[-1]]) if (isinstance(exp[-1], str) and not exp[-1]=='rfstr') else list2codev(exp[-1])}({var_size})"

    elif exp[0] in ["fct", "fn", "defun"]:
        if len(exp) < 4:
            raise SyntaxError(
                """Function statement must contain at least 4 args,
                    (defun fun_name ((arg1 def) [arg2 def] ...) body (return_variable)):"""
                + str(exp)
            )
        if exp[2] == ["nil"]:
            args = ""
        else:
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
        start = f"{indent_whitespace(indent)}fct @{exp[1]}{'(' if args != '' else ''}{args}{')' if args != '' else ''}\n"
        join = "\n"
        close = f"\n{indent_whitespace(indent)}end fct {list2codev(['var'] + [exp[-1],],scope=scope)}"
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
        if len(exp) < 2:
            raise SyntaxError(f"Cannot parse load statement: {str(exp)}")
        start = "in "
        close = " "
        if "cv_macro" in exp[1]:
            close = (
                f";out ^__cv_macro_orig_out\n{indent_whitespace(indent)}"
                + list2codev(
                    liseq_to_list(
                        "(if"
                        ' (== (var __cv_macro_orig_ver) "y")'
                        " (setd ver y) (setd ver n))",
                    ),
                    indent=indent,
                )
            )

            start = (
                list2codev(macro_dict["codev.get_out"]({}), indent=indent)
                + f"\n{indent_whitespace(indent)}"
                + list2codev(macro_dict["codev.get_ver"]({}), indent=indent)
                + f"\n{indent_whitespace(indent)}"
                + start
            )
        exp.pop(0)
    elif exp[0] in ["print", "format", "wri"]:
        start = (
            (
                list2codev(macro_dict["codev.get_out"]({}), indent=indent)
                + f"\n{indent_whitespace(indent)}out y;"
            )
            if "noout" not in scope
            else ""
        ) + "wri "
        close = ";out ^__cv_macro_orig_out" if "noout" not in scope else ""
        exp.pop(0)
    elif exp[0] == "option":
        start = exp[1] + "\n"
        join = "\n"
        close = "\ngo"
        close += (
            "; ras"
            if exp[1] in ras_options
            else "; plt"
            if exp[1] in plt_options
            else ""
        )
        indent += 1
        if exp[1] == "aut":
            scope = "aut"
        exp.pop(0)
        exp.pop(0)

    elif exp[0] in ("command", "cmd"):
        start = exp[1] + " "
        join = " "
        close = " "
        # indent += 1
        if "res" in exp[1]:
            close = (
                f";out ^__cv_macro_orig_out\n{indent_whitespace(indent)}"
                + list2codev(
                    liseq_to_list(
                        "(if"
                        ' (== (var __cv_macro_orig_ver) "y")'
                        " (setd ver y) (setd ver n))",
                    ),
                    indent=indent,
                )
            )

            start = (
                list2codev(macro_dict["codev.get_out"]({}), indent=indent)
                + f"\n{indent_whitespace(indent)}"
                + list2codev(macro_dict["codev.get_ver"]({}), indent=indent)
                + f"\n{indent_whitespace(indent)}"
                + start
            )
        exp.pop(0)
        exp.pop(0)

    elif exp[0] in ["goto", "lbl", "label", "got"]:
        return f"{sub('goto','got',sub('label','lbl',exp[0]))} {exp[1]}"

    elif exp[0] in loop_words:
        if len(exp) < 2:
            raise SyntaxError("Cannot parse loop")
        join = "\n"
        close = f"\n{indent_whitespace(indent)}end {exp[0]}"
        if exp[0] == "for":
            if not isinstance(exp[1], list) or len(exp[1]) < 3:
                raise SyntaxError("Cannot parse for loop init")
            start = f"{exp[0]} {list2codev(['var',exp[1][0]],scope=scope)} {' '.join([list2codev(x) for x in exp[1][1:]])}\n"
        elif exp[0] == "while":
            start = f"{exp[0]} {list2codev(exp[1],scope=scope)}\n"
        elif exp[0] == "unt":
            start = f"{exp[0]}\n"
            close += f" {exp[1]}"
        exp.pop(0)
        exp.pop(0)
        indent += 1

    elif exp[0] == "end":
        END_ACC += f"{list2codev(exp[1:])}\n"
        return ""

    elif "dro" in exp[0]:
        if len(exp) < 3:
            raise SyntaxError("Cannot parse drop")
        if str(exp[1]).lower() not in ("fct", "gbl", "rec", "lcl"):
            raise SyntaxError(
                f'Second argument of drop must be in {str(["fct", "gbl", "rec", "lcl"])}'
            )

        funcs = (
            f'{"@" if exp[1].lower() == "fct" else "^"}'
            + f' {"@" if exp[1].lower() == "fct" else "^"}'.join(exp[2:])
        )
        return f"dro {exp[1]} {funcs}"
    elif exp[0] == "not":
        start = "not("
        close = ")"
        exp.pop(0)
    elif exp[0] == "if":
        if len(exp) < 2:
            raise SyntaxError("Cannot parse if")
        if len(exp) == 2:
            return f"\n{indent_whitespace(indent)}if {list2codev(exp[1],scope=scope)}\n{indent_whitespace(indent)}end if"

        if len(exp) % 2:
            return (
                f"\n{indent_whitespace(indent)}if {list2codev(exp[1],scope=scope)}\n{indent_whitespace(indent+1)}{list2codev(exp[2], indent=indent+1,scope=scope)}\n"
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
                f"\n{indent_whitespace(indent)}if {list2codev(exp[1],scope=scope)}\n{indent_whitespace(indent+1)}{list2codev(exp[2],indent=indent+1,scope=scope)}\n"
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

    elif exp[0] in (set(arith_trans.keys()) | set(arith_words)):
        if len(exp) < 2:
            raise SyntaxError(
                "Arithmetic statement must be of the form (arith arg1 arg2): "
                + str(exp)
            )
        if len(exp) == 2:
            return f"{exp[0]} {list2codev(exp[1], scope=scope, indent=0)}"

        if len(exp) > 3:
            return list2codev([exp[0], exp[1], [exp[0], *exp[2:]]])

        if arith_trans[exp[0]] == "..":
            scope += "nospace"
        if (
            arith_trans[exp[0]] == ".."
            or "nospace" in scope
            # or (isinstance(exp[1], list) and exp[1][0] != "var")
            or (len(exp[1]) == 2 and special_letter_match(exp[1][0]))
        ) and (arith_trans[exp[0]] not in bool_list):
            dist = 0
        elif ("aut" in scope) and (arith_trans[exp[0]] in bool_list):
            dist = 0
            exp[1].insert(0, "cmd") if (
                exp[1][0] != "cmd" and isinstance(exp[1], list)
            ) and exp[1][0] not in (
                set(arith_trans.keys()) | set(arith_words)
            ) else None
        elif ("aut" in scope) and (isinstance(exp[1], str) and exp[1][0] == "@"):
            dist = 0

        else:
            dist = 1
        parentflag1 = (
            ["", ""]
            if isinstance(exp[1], str)
            or "nospace" in scope
            or not len(exp[1]) == 3
            or (not exp[1][0] in arith_trans.keys() or "aut" in scope)
            else "()"
        )
        parentflag2 = (
            ["", ""]
            if isinstance(exp[2], str)
            or "nospace" in scope
            or not len(exp[2]) == 3
            or (not exp[2][0] in arith_trans.keys() or "aut" in scope)
            else "()"
        )
        return f"{'(' if dist!=0 else ''}{parentflag1[0]}{list2codev(exp[1],indent=0,scope=scope) if not isinstance(exp[1],str) or not attr_match(exp[1]) else exp[1]}{parentflag1[1]}{' '*dist}{arith_trans[exp[0]]}{' '*dist}{parentflag2[0]}{list2codev(exp[2],indent=0,scope=scope) if not isinstance(exp[2],str) or not attr_match(exp[2]) else exp[2]}{parentflag2[1]}{')' if dist!=0 else ''}"

    elif special_letter_match(exp[0]):
        if len(exp) < 2:
            raise SyntaxError("Arguments must be larger 2: " + exp)
        if len(exp) == 2:
            return f"{'L' if exp[0] == 'l' else exp[0]}{exp[1] if isinstance(exp[1], str) and special_letter_match(exp[1]) else list2codev(exp[1])}"
        elif exp[0] == "s":
            return f"{exp[0]} {' '.join([list2codev(x) for x in exp[1:]])}"
        elif exp[0] == "l":
            return f"L{' '.join([list2codev(x) for x in exp[1:]])}"
        else:
            raise SyntaxError("Not a known case for single letter expression" + exp)
    else:
        if len(exp) == 1:
            return list2codev(exp[0], scope=scope)
        else:
            return list2codev(["command"] + exp, scope=scope, indent=indent)
            # raise SyntaxError("Cannot parse expr: " + str(exp_input))

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


# def expand_macro(program_input):
#     program = copy(program_input)
#     codev_parse_input = compile(r"codev.parseinput(.*)")
#     # (codev.parseinput func_name (s svar "[sk]"))
#     if len(codev_parse_input.findall(program)) > 0:
#         parse_inputs = findall(
#             r'(?:"[\w\s]+")|(?:\w+)', codev_parse_input.findall(program)[0]
#         )
#         if bool((len(parse_inputs) - 1) % 3):
#             raise SyntaxError("Parse Inputs error")
#         parse_func_name = parse_inputs[0].replace('"', "")
#         parse_inputs = [parse_inputs[1:][x::3] for x in range(3)]
#         parse_inputs[2] = [f"""{x.replace('"', "")}""" for x in parse_inputs[2]]
#         print(parse_func_name)
#         print(parse_inputs)
#         program = codev_parse_input.sub(
#             list2codev(
#                 liseq_to_list(
#                     '(rfd "")'
#                     "(setd buf.emp.find (var parsebufinput))"
#                     "(setd buf.emp.find (var parsebufsyntax))"
#                     "(setd (buf del) (b (var parsebufsyntax)))"
#                     "(setd (buf put (b (var parsebufsyntax)) (il+1) (j 1)) "
#                     f""""syntax: {parse_func_name} {' '.join([f'[{x}]' for x in parse_inputs[2]])}"""
#                     '<----- uses text qualifiers entered in any order")'
#                     "(setd (buf put (b (var parsebufsyntax)) (il+1) (j 1)) "
#                     '"      - or - ")'
#                     "(setd (buf put (b (var parsebufsyntax)) (il+1) (j 1)) "
#                     f""""syntax: {parse_func_name} {' '.join([f'{x}' for x in parse_inputs[2]])}"""
#                     '<----- uses numeric inputs in this order only ")'
#                     "(setd (buf del) (b (var parsebufinput)))"
#                     f"(for (i 1 {str(len(parse_inputs) - 2)})"
#                     "(setd (buf put (b (var parsebufinput)) (il+1)) (nth (var i) rfstr)))"
#                     "(require `cv_macro:ParseInputs (var parsebufinput))"
#                     "(for"
#                     "(i 1 (database buf.lst (b (var parsebufinput))))"
#                     "(set (str parseinput) (database buf.str (b (var parsebufinput)) (i (var i)) (j 1)))"
#                     "(set (str parsequalifier) (database buf.str (b (var parsebufinput)) (i (var i)) (j 2)))"
#                     "(set (num parsevalue) (call str_to_num "
#                     " (database buf.str (b (var parsebufinput)) (i (var i)) (j 3))))"
#                     "(if"
#                     '(or (eq (call upcase (var parseinput)) "H") (eq (call upcase (var parseinput)) "HELP"))'
#                     f"({macro_dict_raw['codev.get_out']} (out y) (setd (buf lis nol) (b (var parsebufsyntax)))"
#                     " (out (var __codev_orig_out)) (goto __codev_end))"
#                     + "".join(
#                         [
#                             rf"""((eq (var parsequalifier) "{x.upper().replace('"','')}"))"""
#                             f"(set (num {y}) (var parsevalue))"
#                             for x, y in zip(parse_inputs[0], parse_inputs[1])
#                         ]
#                     )
#                     + '(eq (var parsequalifier) "IsNum")'
#                     + "(if"
#                     + "".join(
#                         [
#                             rf"""((eq (var i) {(str(i+1))}))"""
#                             f"(set (num {x}) (var parsevalue))"
#                             for i, x in enumerate(parse_inputs[1])
#                         ]
#                     )
#                     + ")"
#                     f"({macro_dict_raw['codev.get_out']}"
#                     '(set (num result) (call cverror "Unrecognized input" 0))'
#                     '(print (call concat "Invalid input: " (var parseinput)) )'
#                     "(out y)"
#                     "(setd (buf lis nol) (b (var parsebufsyntax)))"
#                     "(out (var __codev_orig_out))"
#                     "(goto __codev_end)"
#                     ")))"
#                 ),
#             ),
#             program,
#         )
#     return program


def move_def_to_top(program_input):
    program = copy(program_input)
    if findall("lbl __codev_end", program):
        program = sub("lbl __codev_end", f"lbl __codev_end\n{END_ACC}", program)
    else:
        program = (
            f"{program}\nlbl __codev_end\n{END_ACC}" if END_ACC != "" else f"{program}"
        )
    lclstr = compile(r"^\s*lcl\sstr.*", MULTILINE)
    lclnum = compile(r"^\s*lcl\snum.*", MULTILINE)
    gblstr = compile(r"^\s*gbl\sstr.*", MULTILINE)
    gblnum = compile(r"^\s*gbl\snum.*", MULTILINE)
    drofct = compile(r"^\s*dro\sfct.*", MULTILINE)
    rfdstate = compile(r"^\s*rfd.*", MULTILINE)
    # lclfctget = compile(r"(^\s*fct.*)", MULTILINE)
    # fct_local_get = lclfctget.findall(program)

    str_def = lclstr.findall(program)
    num_def = lclnum.findall(program)
    gstr_def = gblstr.findall(program)
    gnum_def = gblnum.findall(program)
    drofct_def = drofct.findall(program)
    rfdstate_def = rfdstate.findall(program)
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
    definitions += (
        f"gbl str {' '.join(set([y for x in gstr_def for y in x.split()[2:]]))}\n"
        if len(gstr_def) > 0
        else ""
    )
    definitions += (
        f"gbl num {' '.join(set([y for x in gnum_def for y in x.split()[2:]]))}\n"
        if len(gnum_def) > 0
        else ""
    )
    definitions += (
        f"dro fct {' '.join(set([y for x in drofct_def for y in x.split()[2:]]))}\n"
        if len(drofct_def) > 0
        else ""
    )
    program = rfdstate.sub("", program)
    if len(rfdstate_def) > 0:
        program = f"{rfdstate_def[0].strip()}\n{program}"

    if search("rfd.*", program.split("\n")[0]):
        first_line = program.split("\n")[0]
        program = sub(escape(first_line), "", program)
        definitions = first_line + "\n" + definitions
    program = f"""{definitions}{drofct.sub("",lclnum.sub("", lclstr.sub("", gblstr.sub("",gblnum.sub("",program)))))}"""
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
    ast = liseq_to_list(program)
    return move_def_to_top(list2codev(ast))
