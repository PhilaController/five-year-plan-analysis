"""Install the fyp_analysis package."""

from setuptools import find_packages, setup

entry_point = "fyp-analysis = fyp_analysis.__main__:main"


setup(
    name="fyp_analysis",
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": [entry_point]},
)
