"""Five Year Plan Analysis file for ensuring the package is executable.

The package can be run as `fyp-analysis` and `python -m fyp_analysis`.
"""
from pathlib import Path

from kedro.framework.project import configure_project

from . import cli


def main():
    """Command line tool for running the Five Year Plan analysis code."""
    cli.cli()
