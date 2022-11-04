from liseq.util import liseq_to_list, list_depth
from io import StringIO
from contextlib import redirect_stdout


def _python_compiler(ast, compile=False, indent=0):
    depth = list_depth(ast)
    if len(ast) == 1:
        return _python_compiler(ast[0], compile=compile)
    if len(ast) == 0:
        return ""
    if compile:
        f = StringIO()
        with redirect_stdout(f):
            exec(_python_compiler(ast))
        return f.getvalue().strip()
    if depth > 1:
        return "\n".join([_python_compiler(x) for x in ast])
    if ast[0] in ("set", "let"):
        return f"{ast[1]} = {ast[2]}"
    elif ast[0] in ("print", "write"):
        return f"print({ast[1]})"
    else:
        return ""


def _codev_transpiler(ast, compile=False):
    depth = list_depth(ast)
    if len(ast) == 1:
        return _codev_transpiler(ast[0])
    if depth > 1 and type(ast[0]) != str:
        return "\n\n".join([_codev_transpiler(x) for x in ast])
    if ast[0] == "macro":
        return _python_compiler(ast[1:], compile=True)
    return str(ast)


def transpiler(code):
    ast = liseq_to_list(code)
    return _codev_transpiler(ast)


if __name__ == "__main__":
    print(transpiler("(macro ((num a) (set a 1) (print a)))"))
