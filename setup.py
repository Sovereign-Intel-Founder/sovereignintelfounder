from setuptools import setup, find_packages

setup(
    name="sovereign-core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=38.0.0",
    ],
)
