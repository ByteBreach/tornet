#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="tornet",
    version="2.2.1",
    description="Automate IP address changes using Tor",
    author="ByteBreach",
    author_email="",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "PyYAML>=5.4.1",
    ],
    entry_points={
        "console_scripts": [
            "tornet=tornet.tornet:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)
