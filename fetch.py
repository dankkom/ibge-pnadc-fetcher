import argparse
from pathlib import Path

import pnadcpy


def get_parser():
    parser = argparse.ArgumentParser(description="Fetch data from IBGE")
    parser.add_argument("--year", type=int, help="Year to fetch")
    parser.add_argument("--datadir", type=Path, help="Directory to save data")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    year = args.year
    datadir = args.datadir
    ftp = pnadcpy.get_ftp()

    pnadcpy.download_data(ftp=ftp, year=year, datadir=datadir)


if __name__ == "__main__":
    main()
