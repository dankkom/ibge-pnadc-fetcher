import argparse
from pathlib import Path

from ibge_pnadc_fetcher.fetcher import download_data, download_doc, get_ftp


def get_args():
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


def main():
    args = get_args()
    ftp = get_ftp()
    download_data(ftp, args.data_dir)
    download_doc(ftp, args.data_dir / "[doc]")


if __name__ == "__main__":
    main()
