from pathlib import Path
from liseq.util import open_file, liseq_to_list

macro_dir = Path(__file__).parent


def rename_fig(x):
    return liseq_to_list(open_file(f"{macro_dir}/codev_rename_fig.liseq").format(**x))


def startup(x):
    return liseq_to_list(open_file(f"{macro_dir}/codev_startup.liseq").format(**x))


def get_out(x):
    return liseq_to_list(open_file(f"{macro_dir}/codev_get_out.liseq").format(**x))


def export(x):
    # print(str(x["__codev_arg2"]).replace())
    __codev_arg2 = x["__codev_arg2"]
    x["__codev_arg2"] = "__codev_arg2"
    return_list = liseq_to_list(
        open_file(f"{macro_dir}/codev_export.liseq").format(**x)
    )
    return_list[return_list.index("__codev_arg2")] = __codev_arg2

    return return_list


macro_dict = {
    "codev.rename_fig": rename_fig,
    "codev.startup": startup,
    "get_out": get_out,
    "codev.export": export,
}

macro_dict_raw = {
    "get_out": open_file(f"{macro_dir}/codev_get_out.liseq"),
}
