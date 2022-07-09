import pnadcpy
from pathlib import Path
import argparse


def get_parser():
    parser = argparse.ArgumentParser(description="Fetch documentation from IBGE")
    parser.add_argument("--docdir", type=Path, help="Directory to save doc")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    docdir = args.docdir
    ftp = pnadcpy.get_ftp()

    pnadcpy.download_doc(ftp=ftp, docdir=docdir)


if __name__ == "__main__":
    main()
