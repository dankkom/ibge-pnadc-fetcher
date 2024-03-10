import datetime as dt
import zipfile
from pathlib import Path


def get_data_filename(data_file: dict) -> str:
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


def get_data_filepath(data_file: dict, data_dir: Path) -> Path:
    """Get the filepath for a data file."""
    filename = get_data_filename(data_file)
    dest_filepath = data_dir / f'{data_file["year"]}{data_file["quarter"]}' / filename
    return dest_filepath


def get_doc_filename(original_name: str, modified: dt.datetime, suffix: str) -> str:
    return f"{original_name}@{modified:%Y%m%d}.{suffix}"


def get_doc_filepath(file: dict, doc_dir: Path) -> Path:
    modified = file["datetime"]
    original_name, suffix = file["filename"].split(".")
    filename = get_doc_filename(original_name, modified, suffix)
    dest_filepath = doc_dir / filename
    return dest_filepath


def unzip_file(zip_file: Path, dest_dir: Path):
    """Unzip a file to a directory."""
    _, yearquarter, date = zip_file.stem.split("_")
    dest_filepath = dest_dir / f"pnadc_{yearquarter}_{date}.txt"
    with zipfile.ZipFile(zip_file, "r") as z:
        zfile = z.namelist()[0]
        z.extract(zfile, dest_dir)
        extracted_file = dest_dir / zfile
        extracted_file.rename(dest_filepath)


def get_latest_files(datadir: Path, extension="zip") -> list[Path]:
    """Get the latest files for each period from a directory."""
    latest_files = {}
    files = list(datadir.glob(f"**/pnadc_*.{extension}"))
    sorted_files = sorted(files, key=lambda f: f.stem.split("_")[-1])
    for file in sorted_files:
        _, yearquarter, _ = file.stem.split("_")
        latest_files[yearquarter] = file
    latest_files = list(latest_files.values())
    return latest_files
