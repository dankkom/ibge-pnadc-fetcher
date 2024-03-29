"""PNADC-Downloader: Little script to download PNADC's microdata files."""

import datetime as dt
import ftplib
import logging
import re
import zipfile
from pathlib import Path
from typing import Any, Callable

from tqdm import tqdm

logger = logging.getLogger(__name__)

START_YEAR = 2012

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


def list_ftp_files(ftp: ftplib.FTP) -> list[dict]:
    """List all data files in the current directory."""
    files = []
    pwd = ftp.pwd()
    ftp.retrlines("LIST", files.append)

    files = [parse_file_line(line, pwd) for line in files]

    return files


def list_pnadc_data_files(ftp: ftplib.FTP) -> list:
    data_files = []
    current_year = dt.date.today().year
    for year in range(START_YEAR, current_year + 2):
        path = f"{DATA_FTP_PATH}/{year}"
        try:
            ftp.cwd(path)
            files = list_ftp_files(ftp)
        except ftplib.error_perm:
            break
        for file in files:
            year, quarter = parse_data_filename(file["filename"])
            file["year"] = year
            file["quarter"] = quarter
            _, file["extension"] = file["filename"].rsplit(".", maxsplit=1)
        data_files.extend(files)
    return data_files


def get_filename(data_file: dict) -> str:
    """Get the filename for a data file.

    The filename is composed by the following parts:
    - `pnadc`: the dataset's acronym
    - `YYYYQQ`: the year and quarter of the data
    - `YYYYMMDD`: the date of the file's last modification
    - `extension`: the file's extension

    Example: `pnadc_201204_20210101.zip` for a file from the 2nd quarter of 2012

    """
    stem = "_".join(
        [
            "pnadc",
            f"{data_file['year']}{data_file['quarter']:02d}",
            f"{data_file['datetime']:%Y%m%d}",
        ]
    )
    return f"{stem}.{data_file['extension']}"


def download_ftp_file(
    ftp: ftplib.FTP,
    ftp_filepath: str,
    dest_filepath: Path,
    **kwargs,
) -> None:
    """Download a file from FTP."""
    dest_filepath.parent.mkdir(parents=True, exist_ok=True)

    if "file_size" in kwargs:
        file_size = kwargs["file_size"]
    else:
        file_size = ftp.size(ftp_filepath)

    logger.info(f"Downloading {ftp_filepath} --> {dest_filepath}")

    progress = tqdm(
        desc=dest_filepath.name,
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
    callback: Callable[[Path], Any] = None,
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
        if callable(callback):
            callback(dest_filepath)


def download_data(
    ftp: ftplib.FTP,
    datadir: Path,
    callback: Callable[[Path], Any] = None,
):
    for data_file in list_pnadc_data_files(ftp):
        filename = get_filename(data_file)
        dest_filepath = datadir / str(data_file["year"]) / filename
        if dest_filepath.exists():
            logger.info(f"{dest_filepath} already exists")
            continue
        download_ftp_file(
            ftp=ftp,
            ftp_filepath=data_file["full_path"],
            dest_filepath=dest_filepath,
            file_size=data_file["size"],
        )
        if callable(callback):
            callback(dest_filepath)


def unzip_file(zip_file: Path, dest_dir: Path):
    """Unzip a file to a directory."""
    _, yearquarter, date = zip_file.stem.split("_")
    dest_filepath = dest_dir / f"pnadc_{yearquarter}_{date}.txt"
    with zipfile.ZipFile(zip_file, "r") as z:
        zfile = z.namelist()[0]
        z.extract(zfile, dest_dir)
        extracted_file = dest_dir / zfile
        extracted_file.rename(dest_filepath)


def get_latest_files(datadir: Path, extension="zip"):
    """Get the latest files for each period from a directory."""
    latest_files = {}
    files = list(datadir.glob(f"**/pnadc_*.{extension}"))
    sorted_files = sorted(files, key=lambda f: f.stem.split("_")[-1])
    for file in sorted_files:
        _, yearquarter, _ = file.stem.split("_")
        latest_files[yearquarter] = file
    latest_files = list(latest_files.values())
    return latest_files


def cli():
    def get_args():
        import argparse

        parser = argparse.ArgumentParser(
            description="Fetch PNADC data/doc from IBGE",
        )

        parser.add_argument(
            "--data-dir",
            required=True,
            type=Path,
            help="Directory to save data",
        )

        args = parser.parse_args()

        return args

    args = get_args()
    ftp = get_ftp()
    download_data(ftp, args.data_dir)
    download_doc(ftp, args.data_dir / "[doc]")


if __name__ == "__main__":
    cli()
