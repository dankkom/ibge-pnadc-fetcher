import setuptools

import pnadcpy

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pnadcpy",
    version=pnadcpy.__version__,
    author="Daniel K. Komesu",
    author_email="danielkomesu@gmail.com",
    description="A package to download IBGE's PNADC data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/DanKKom/pnadcpy/",
    py_modules=["pnadcpy"],
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
