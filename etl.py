import functools
import json
import multiprocessing as mp
import os
import zipfile

import pnadcpy


def convert(dicio, datadir, filepath):
    print(filepath)
    data = pnadcpy.open_pnadc(filepath, dicio)
    new_path = os.path.join(
        datadir,
        os.path.basename(filepath)
    )
    new_path = new_path.replace(".zip", ".parquet")
    data.to_parquet(new_path)


if __name__ == "__main__":
    with open("configs/configs.json", "r") as f:
        configs = json.load(f)

    dicio_path = os.path.join(configs["doc"], "Dicionario_e_input.zip")
    with zipfile.ZipFile(dicio_path, "r") as zf:
        zf.extract("Input_PNADC_trimestral.txt")
    dicio = pnadcpy.get_dicio("Input_PNADC_trimestral.txt")

    run = functools.partial(convert, dicio, configs["datadir"])

    files = [file.path for file in os.scandir(configs["raw"])]

    with mp.Pool(4) as p:
        p.map(run, files)
