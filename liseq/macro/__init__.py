from pathlib import Path
from liseq.util import open_file, liseq_to_list

macro_dir = Path(__file__).parent


def rename_fig(x):
    return liseq_to_list(open_file(f"{macro_dir}/codev_rename_fig.liseq").format(**x))


macro_dict = {"codev.rename_fig": rename_fig}
