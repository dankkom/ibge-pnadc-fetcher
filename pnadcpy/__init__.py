"""PNADC-Downloader
This little script set helps to download PNADC's microdata files.
"""


import pandas as pd

from .read_dicio import get_dicio


__version__ = "0.1"


def open_pnadc(file_path, dicio):
    data = pd.read_fwf(
        file_path,
        compression="zip",
        widths=dicio["width"],
        names=dicio["name"])
    return data
