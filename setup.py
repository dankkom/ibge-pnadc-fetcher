import codecs
import os
import setuptools


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pnadcpy",
    version=get_version("pnadcpy.py"),
    author="Daniel K. Komesu",
    author_email="danielkomesu@gmail.com",
    description="A package to download IBGE's PNADC microdata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dankkom/pnadcpy",
    py_modules=["pnadcpy"],
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=[
        "pandas",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
