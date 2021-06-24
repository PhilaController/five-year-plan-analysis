"""Install the fyp_analysis package."""

from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent.absolute()

entry_point = "fyp-analysis = fyp_analysis.__main__:main"


setup(
    name="fyp_analysis",
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": [entry_point]},
    package_data={
        "fyp_analysis": [
            "fyp_analysis/pipelines/data_processing/indicators/sources/*json"
        ]
    },
    include_package_data=True,
)
