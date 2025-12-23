#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_directory, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "TorNet - Advanced Tor Network Controller for IP Rotation and Anonymity"

setup(
    name="tornet",
    version="2.3.0",
    author="ByteBreach",
    author_email="mrfidal@proton.me",
    description="Advanced Tor Network Controller for IP Rotation and Anonymity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bytebreach/tornet",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: System :: Networking"
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.28.0",
        "stem>=1.8.0",
        "PySocks>=1.7.1",
        "pyyaml>=6.0",
        "schedule>=1.1.0"
    ],
    entry_points={
        "console_scripts": [
            "tornet=tornet.tornet:main",
        ],
    },
    include_package_data=True,
    keywords="tor, anonymity, proxy, security, privacy, networking",
    project_urls={
        "Bug Reports": "https://github.com/bytebreach/tornet/issues",
        "Source": "https://github.com/bytebreach/tornet"
    }
)
