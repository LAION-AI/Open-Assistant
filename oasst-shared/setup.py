# setup.py for the shared python modules

from distutils.core import setup

from setuptools import find_namespace_packages

setup(
    name="oasst-shared",
    version="1.0",
    packages=find_namespace_packages(),
    author="OASST Team",
    install_requires=[
        "pydantic==1.9.1",
        "aiohttp==3.8.3",
        "aiohttp[speedups]",
    ],
)
