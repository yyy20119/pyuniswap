# -*- coding: utf-8 -*-
import setuptools
import pyuniswap

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pyuniswap",
    version=pyuniswap.__version__,
    author="yyy20119",
    author_email="1508974340@qq.com",
    description="An open source Python wrapper for Uniswap V2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yyy20119/pyuniswap",
    packages=setuptools.find_packages(),
    package_data={"pyuniswap": ["abi_files/*"]},
    install_requires=["web3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
