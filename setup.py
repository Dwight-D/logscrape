import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="logscrape-dwightd",
    version="0.0.1",
    author="Max Forsman",
    author_email="forsman.max@gmail.com",
    description="Utility for scraping log files for matching text patterns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dwight-d/logscrape",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL 3-0",
        "Operating System :: OS Independent",
    ],
)