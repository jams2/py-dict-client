from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="py-dict-client",
    version="0.1.2",
    description="A client implementing the Dictionary Server Protocol (DICT)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jams2/py-dict-client",
    author="Joshua Munn",
    author_email="public@elysee-munn.family",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    keywords="dictionary language definition server client",
    package_dir={"dictionary_client": "dictionary_client"},
    packages=["dictionary_client"],
    python_requires=">=3",
)
