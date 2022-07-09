"""PNADC-Downloader: Little script to download PNADC's microdata files."""

import ftplib
import logging
import os
import pathlib
import re
import zipfile
from typing import Union

import pandas as pd

__version__ = "0.2.0"


logger = logging.getLogger(__name__)

Filepath = Union[pathlib.Path, str, os.PathLike]

# FTP paths ===================================================================
FTP_HOST = "ftp.ibge.gov.br"
BASE_FTP_PATH = (
    "/Trabalho_e_Rendimento"
    "/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua"
    "/Trimestral"
    "/Microdados"
)
DOC_FTP_PATH = BASE_FTP_PATH + "/Documentacao"
DATA_FTP_PATH = BASE_FTP_PATH


def get_ftp(server: str = FTP_HOST) -> ftplib.FTP:
    logger.info(f"Getting FTP: {server}")
    ftp = ftplib.FTP(server)
    ftp.login()

    return ftp


def download_ftp_file(
    ftp: ftplib.FTP,
    ftp_filepath: str,
    dest_filepath: Filepath,
) -> None:
    with open(dest_filepath, "wb") as f:
        ftp.retrbinary("RETR " + ftp_filepath, f.write)


def extract_zip(filepath: Filepath, dest: Filepath) -> None:
    with zipfile.ZipFile(filepath) as zf:
        zf.extractall(dest)


def download_doc(
    ftp: ftplib.FTP,
    docdir: Filepath,
) -> None:
    if isinstance(docdir, str):
        docdir = pathlib.Path(docdir)
    if not docdir.exists():
        docdir.mkdir(parents=True)

    # Change current working directory to ftp_path
    ftp.cwd(DOC_FTP_PATH)

    files = ftp.nlst(DOC_FTP_PATH)
    for file in files:
        filename = file.split("/")[-1]
        filepath: pathlib.Path = docdir / filename
        logger.info(f"DOC: {file} --> {filepath}")
        download_ftp_file(ftp=ftp, ftp_filepath=file, dest_filepath=filepath)
        if filepath.suffix.lower().endswith(".zip"):
            extract_zip(filepath, docdir)
            filepath.unlink()


def download_data(
    ftp: ftplib.FTP,
    year: int,
    datadir: Filepath,
) -> None:
    if isinstance(datadir, str):
        datadir = pathlib.Path(datadir)
    if not datadir.exists():
        datadir.mkdir()

    # Change current working directory to ftp_path
    ftp.cwd(DATA_FTP_PATH)

    files = ftp.nlst(str(year))
    q = 1
    for file in files:
        filepath = datadir / f"{year}Q{q}.zip"
        logger.info(
            f"DATA: Year={year} Quarter={q} {file} --> {filepath}"
        )
        download_ftp_file(ftp=ftp, ftp_filepath=file, dest_filepath=filepath)
        q += 1


def _parse_sas_file_line(line: str) -> tuple[int, int, str, str]:
    try:
        desc = re.findall(r"/\*.*\*/", line)
        desc = desc[0].strip("*/ ")
        line = re.sub(r"/\*.*\*/", "", line)
        line = re.sub(" +", " ", line)
        line = line.strip().split(" ")
        start = int(line[0].strip("@"))
        name = line[1]
        dtype = "str" if "$" in line[2] else "float"
        width = int(line[2].strip(".$"))
        return (start, width, name, dtype, desc)
    except Exception as e:
        print(line)
        print(e)
        return (None, None, None, None, None)


def read_sas_file_dicio(filepath: Filepath) -> dict[str, list]:
    dicio = {
        "start": [],
        "width": [],
        "name": [],
        "dtype": [],
        "desc": [],
    }
    with open(filepath, "r") as f:
        for line in f:
            if not line.startswith("@"):
                continue
            start, width, name, dtype, desc = _parse_sas_file_line(line)
            dicio["start"].append(start)
            dicio["width"].append(width)
            dicio["name"].append(name)
            dicio["dtype"].append(dtype)
            dicio["desc"].append(desc)
    return dicio


def read_pnadc(
    filepath: Filepath,
    dicio: pd.DataFrame,
) -> pd.DataFrame:
    data = pd.read_fwf(
        filepath,
        compression="zip",
        widths=dicio["width"],
        names=dicio["name"],
        dtype={
            name: dtype for name, dtype in zip(dicio["name"], dicio["dtype"])
        },
        na_values=["", "NA", "."],
        decimal=".",
    )
    return data
