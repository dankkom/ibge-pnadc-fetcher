"""PNADC-Downloader: Little script to download PNADC's microdata files."""

import datetime as dt
import ftplib
import logging
import re
from pathlib import Path

import pandas as pd
from tqdm import tqdm

__version__ = "0.2.0"


logger = logging.getLogger(__name__)

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


def parse_data_filename(name):
    """Parse a filename to extract the year and quarter."""
    period_quarter, period_year = re.search(r"(\d{2})(20\d{2})", name).groups()
    return int(period_year), int(period_quarter)


def parse_file_line(line, pwd):
    _, _, _, _, size, month, day, year_or_hour, name = line.split()
    if ":" in year_or_hour:
        year = dt.date.today().year
        hour = year_or_hour
    else:
        year = year_or_hour
        hour = "00:00"
    datetime = dt.datetime.strptime(f"{year}{month}{day}{hour}", "%Y%b%d%H:%M")
    try:
        size = int(size)
    except ValueError:
        size = None
    parsed = {
        "datetime": datetime,
        "size": size,
        "filename": name,
        "full_path": pwd + "/" + name,
    }
    return parsed


def list_ftp_files(ftp: ftplib.FTP) -> list:
    """List all data files in the current directory."""
    files = []
    pwd = ftp.pwd()
    ftp.retrlines("LIST", files.append)

    files = [parse_file_line(line, pwd) for line in files]

    return files


def download_ftp_file(
    ftp: ftplib.FTP,
    ftp_filepath: str,
    dest_filepath: Path,
    **kwargs,
) -> None:
    """Download a file from FTP."""
    if not dest_filepath.parent.exists():
        dest_filepath.parent.mkdir(parents=True)

    if "file_size" in kwargs:
        file_size = kwargs["file_size"]
    else:
        file_size = ftp.size(ftp_filepath)

    logger.info(f"Downloading {ftp_filepath} --> {dest_filepath}")

    progress = tqdm(
        desc=ftp_filepath.rsplit("/", 1)[-1],
        total=file_size,
        unit="B",
        unit_scale=True,
    )

    with open(dest_filepath, "wb") as f:
        def write(data):
            nonlocal f, progress
            f.write(data)
            progress.update(len(data))
        ftp.retrbinary(f"RETR {ftp_filepath}", write)
    progress.close()


def download_doc(
    ftp: ftplib.FTP,
    docdir: Path,
) -> None:

    # Change current working directory to ftp_path
    ftp.cwd(DOC_FTP_PATH)

    files = list_ftp_files(ftp)
    for file in files:
        modified = file["datetime"]
        original_name, suffix = file["filename"].split(".")
        filename = f"{original_name}@{modified:%Y%m%d}.{suffix}"
        dest_filepath = docdir / filename
        if dest_filepath.exists():
            logger.info(f"{dest_filepath} already exists")
            continue
        download_ftp_file(
            ftp=ftp,
            ftp_filepath=file["full_path"],
            dest_filepath=dest_filepath,
        )


def download_data(
    ftp: ftplib.FTP,
    year: int,
    datadir: Path,
) -> None:

    # Change current working directory to ftp_path
    ftp.cwd(f"{DATA_FTP_PATH}/{year}")

    files = list_ftp_files(ftp)

    for file in files:
        modified = file["datetime"]
        y, q = parse_data_filename(file["filename"])
        _, suffix = file["filename"].split(".")
        dest_filename = f"pnadc_{y}{q}_{modified:%Y%m%d}.{suffix}"
        dest_filepath = datadir / f"{y}" / dest_filename
        if dest_filepath.exists():
            logger.info(f"{dest_filepath} already exists")
            continue
        download_ftp_file(
            ftp=ftp,
            ftp_filepath=file["full_path"],
            dest_filepath=dest_filepath,
            file_size=file["size"],
        )


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


def read_sas_file_dicio(filepath: Path) -> dict[str, list]:
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
    filepath: Path,
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
