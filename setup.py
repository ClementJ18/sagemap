from setuptools import setup, find_packages
import re

version = ""
with open("map_parser/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("version is not set")

readme = ""
with open("README.md") as f:
    readme = f.read()

setup(
    name="map_parser",
    version=version,
    url="https://github.com/ClementJ18/map_parser",
    packages=find_packages(include=["map_parser", "map_parser.*"]),
    description="A library for reading and writing .map files from SAGE engine games.",
    long_description_content_type="text/markdown",
    long_description=readme,
    python_requires='>=3.8',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
