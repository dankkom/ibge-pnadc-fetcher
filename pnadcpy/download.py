import ftplib
import logging
import os


logger = logging.getLogger(__name__)


def _get_ftp(server):
    logger.info(f"Getting FTP: {server}")
    ftp = ftplib.FTP(server)
    ftp.login()

    return ftp


def _doc(ftp, ftp_path, docdir):
    if not os.path.exists(docdir):
        os.makedirs(docdir)

    # Change current working directory to ftp_path
    ftp.cwd(ftp_path)

    files = ftp.nlst(ftp_path)
    for file in files:
        filename = file.split("/")[-1]
        filename = os.path.join(docdir, filename)
        logger.info(f"DOC: {file} --> {filename}")
        with open(filename, "wb") as f:
            ftp.retrbinary("RETR " + file, f.write)


def _data(ftp, ftp_path, year, datadir):
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    # Change current working directory to ftp_path
    ftp.cwd(ftp_path)

    files = ftp.nlst(str(year))
    q = 1
    for file in files:
        filename = os.path.join(datadir, f"{year}Q{q}.zip")
        logger.info(
            f"DATA: Year={year} Quarter={q} {file} --> {filename}"
        )
        with open(filename, "wb") as f:
            ftp.retrbinary("RETR " + file, f.write)
        q += 1
