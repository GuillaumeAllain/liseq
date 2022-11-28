from pathlib import Path
from liseq.util import open_file, liseq_to_list

macro_dir = Path(__file__).parent


def rename_fig(x):
    return liseq_to_list(open_file(f"{macro_dir}/codev_rename_fig.liseq").format(**x))


def startup(x):
    return liseq_to_list(open_file(f"{macro_dir}/codev_startup.liseq").format(**x))


def get_out(x):
    return liseq_to_list(open_file(f"{macro_dir}/codev_get_out.liseq").format(**x))


def get_ver(x):
    return liseq_to_list(open_file(f"{macro_dir}/codev_get_ver.liseq").format(**x))


def export(x):
    arg_2_to_n = list(x.keys())
    arg_2_to_n.sort()
    arg_2_to_n = arg_2_to_n[1:]
    y = {"__codev_arg1": x["__codev_arg1"], "__codev_arg2": "__codev_arg2"}
    return_list = liseq_to_list(
        open_file(f"{macro_dir}/codev_export.liseq").format(**y)
    )
    return_list[0][return_list[0].index("__codev_arg2")] = [x[ii] for ii in arg_2_to_n]

    return return_list


def outbuf(x):
    arg_2_to_n = list(x.keys())
    arg_2_to_n.sort()
    arg_2_to_n = arg_2_to_n
    y = {"__codev_arg1": "__codev_arg1"}
    return_list = liseq_to_list(
        open_file(f"{macro_dir}/codev_outbuf.liseq").format(**y)
    )
    return_list[return_list.index("__codev_arg1")] = [x[ii] for ii in arg_2_to_n]
    return return_list


def templens(x):
    arg_2_to_n = list(x.keys())
    arg_2_to_n.sort()
    arg_2_to_n = arg_2_to_n
    y = {"__codev_arg1": "__codev_arg1"}
    return_list = liseq_to_list(
        open_file(f"{macro_dir}/codev_templens.liseq").format(**y)
    )
    return_list[return_list.index("__codev_arg1")] = [x[ii] for ii in arg_2_to_n]
    return return_list


def findbuf(x):
    if type(x["__codev_arg1"]) is list:
        x["__codev_arg1"] = f'({" ".join(x["__codev_arg1"])})'
    return liseq_to_list(open_file(f"{macro_dir}/codev_findbuf.liseq").format(**x))


def parseinputs(x):
    parse_inputs = list(x.keys())
    parse_inputs.sort()
    parse_inputs = [x[args] for args in parse_inputs[1:]]
    for args in parse_inputs:
        args[2] = args[2].replace("(", "").replace(")", "")
        args[2] = args[2].replace('"', "").replace('"', "")
        if len(args) != 4:
            args.append('""')
    parse_inputs = list(zip(*parse_inputs))
    parse_func_name = x["__codev_arg1"]

    return (
        liseq_to_list(
            f"(rfd {' '.join([x for x in parse_inputs[3]])})"
            "(codev.findbuf (var parsebufinput))"
            "(codev.findbuf (var parsebufsyntax))"
            "(setd (buf del) (b (var parsebufsyntax)))"
            "(setd (buf put (b (var parsebufsyntax)) (il+1) (j 1)) "
            f""""syntax: {parse_func_name} {' '.join([f'[{x}]' for x in parse_inputs[2]])}"""
            '<----- uses text qualifiers entered in any order")'
            "(setd (buf put (b (var parsebufsyntax)) (il+1) (j 1)) "
            '"      - or - ")'
            "(setd (buf put (b (var parsebufsyntax)) (il+1) (j 1)) "
            f""""syntax: {parse_func_name} {' '.join([f'{x}' for x in parse_inputs[2]])}"""
            '<----- uses numeric inputs in this order only ")'
            "(setd (buf del) (b (var parsebufinput)))"
            f"(for (i 1 {str(len(parse_inputs[0]))})"
            "(setd (buf put (b (var parsebufinput)) (il+1)) (nth (var i) rfstr)))"
            "(require `cv_macro:ParseInputs (var parsebufinput))"
            "(for"
            "(i 1 (database buf.lst (b (var parsebufinput))))"
            "(set (str parseinput) (database buf.str (b (var parsebufinput)) (i (var i)) (j 1)))"
            "(set (str parsequalifier) (database buf.str (b (var parsebufinput)) (i (var i)) (j 2)))"
            "(set (num parsevalue) (call str_to_num "
            " (database buf.str (b (var parsebufinput)) (i (var i)) (j 3))))"
            "(if"
            '(or (eq (call upcase (var parseinput)) "H") (eq (call upcase (var parseinput)) "HELP"))'
            f"({macro_dict_raw['codev.get_out']} (out y) (setd (buf lis nol) (b (var parsebufsyntax)))"
            " (out (var __codev_orig_out)) (goto __codev_end))"
            + "".join(
                [
                    rf"""((eq (var parsequalifier) "{x.upper().replace('"','')}"))"""
                    f"(set (num {y}) (var parsevalue))"
                    for x, y in zip(parse_inputs[0], parse_inputs[1])
                ]
            )
            + '(eq (var parsequalifier) "IsNum")'
            + "(if"
            + "".join(
                [
                    rf"""((eq (var i) {(str(i+1))}))"""
                    f"(set (num {x}) (var parsevalue))"
                    for i, x in enumerate(parse_inputs[1])
                ]
            )
            + ")"
            f"({macro_dict_raw['codev.get_out']}"
            '(set (num result) (call cverror "Unrecognized input" 0))'
            '(print (call concat "Invalid input: " (var parseinput)) )'
            "(out y)"
            "(setd (buf lis nol) (b (var parsebufsyntax)))"
            "(out (var __codev_orig_out))"
            "(goto __codev_end)"
            ")))"
        ),
    )


# salut
# [['s'], ['svar'], ['sk']]


macro_dict = {
    "codev.rename_fig": rename_fig,
    "codev.startup": startup,
    "codev.get_out": get_out,
    "codev.get_ver": get_ver,
    "codev.export": export,
    "codev.outbuf": outbuf,
    "codev.findbuf": findbuf,
    "buf.emp.find": findbuf,
    "codev.suppressoutput": lambda x: liseq_to_list(
        open_file(f"{macro_dir}/codev_suppressoutput.liseq")
    ),
    "codev.parseinputs": parseinputs,
    "codev.parseinput": parseinputs,
    "codev.templens": templens,
}

macro_dict_raw = {
    "codev.get_out": open_file(f"{macro_dir}/codev_get_out.liseq"),
}
