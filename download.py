import os
import os.path as osp
import json

import pnadcpy


with open("configs/configs.json", "r") as f:
    configs = json.load(f)


ftp = pnadcpy.get_ftp(configs["ftp"]["server"])

pnadcpy.download_doc(ftp, configs["ftp"]["doc"], configs["doc"])

for year in range(2012, 2020):
    pnadcpy.download_data(
        ftp, configs["ftp"]["microdata"], year, configs["raw"])
