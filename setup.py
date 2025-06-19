from setuptools import setup, find_packages

setup(
    name="gs1_gpc",
    version="0.3.3",
    packages=find_packages(exclude=["data", "data.*"]),
    install_requires=[
        "click>=8.0.0",
        "gpcc>=1.1.0",
    ],
    entry_points={
        'console_scripts': [
            'gpc=gs1_gpc.cli:cli',
        ],
    },
)