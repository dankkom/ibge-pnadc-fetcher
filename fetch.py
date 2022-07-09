import argparse
from pathlib import Path

import ibge_pnadc_fetcher


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
    ftp = ibge_pnadc_fetcher.get_ftp()

    ibge_pnadc_fetcher.download_data(ftp=ftp, year=year, datadir=datadir)


if __name__ == "__main__":
    main()
