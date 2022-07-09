import argparse
from pathlib import Path

import ibge_pnadc_fetcher


def get_parser():
    parser = argparse.ArgumentParser(description="Fetch documentation from IBGE")
    parser.add_argument("--docdir", type=Path, help="Directory to save doc")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    docdir = args.docdir
    ftp = ibge_pnadc_fetcher.get_ftp()

    ibge_pnadc_fetcher.download_doc(ftp=ftp, docdir=docdir)


if __name__ == "__main__":
    main()
