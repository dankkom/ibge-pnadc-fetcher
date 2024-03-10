import argparse
import zipfile
from pathlib import Path

from ibge_pnadc_fetcher import get_latest_files


def unzip_file(zip_file: Path, dest_dir: Path) -> None:
    # Parse file name
    _, yearquarter, date = zip_file.stem.split("_")
    dest_dir_ = dest_dir / yearquarter
    dest_dir_.mkdir(parents=True, exist_ok=True)
    dest_filepath = dest_dir_ / f"pnadc_{yearquarter}_{date}.txt"
    if dest_filepath.exists():
        print(dest_filepath, "already exists, skipping")
        return
    with zipfile.ZipFile(zip_file, "r") as z:
        zfile = z.namelist()[0]
        print("Extracting", zfile, "to", dest_dir)
        z.extract(zfile, dest_dir)
        extracted_file = dest_dir / zfile
        print("Renaming", extracted_file, "to", dest_filepath)
        extracted_file.rename(dest_filepath)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unzip PNADC data files",
    )
    parser.add_argument(
        "--data-dir",
        required=True,
        type=Path,
        help="Directory to save data",
    )
    parser.add_argument(
        "--dest-dir",
        required=True,
        type=Path,
        help="Directory to save unzipped files",
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    data_dir = args.data_dir
    dest_dir = args.dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    for zip_file in get_latest_files(data_dir, extension="zip"):
        print("Unzipping", zip_file, "to", dest_dir)
        unzip_file(zip_file, dest_dir)


if __name__ == "__main__":
    main()
