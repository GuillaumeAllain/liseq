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


macro_dict = {
    "codev.rename_fig": rename_fig,
    "codev.startup": startup,
    "codev.get_out": get_out,
    "codev.get_ver": get_ver,
    "codev.export": export,
    "codev.outbuf": outbuf,
}

macro_dict_raw = {
    "codev.get_out": open_file(f"{macro_dir}/codev_get_out.liseq"),
}
