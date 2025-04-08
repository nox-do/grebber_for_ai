from setuptools import setup, find_packages

setup(
    name="grebber_for_ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pywin32==310",
        "toml==0.10.2",
        "gitpython==3.1.31",
    ],
) 