import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as reqs:
    requirements = reqs.read().split('\n')


setuptools.setup(
    name="pandjas",
    version="0.1.1",
    author="Storn White",
    author_email="storn@open-energy-engine.org",
    description="pandas wrapped by django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StornWhite/open-energy-engine",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)"
        "Operating System :: OS Independent",
    ],
)
