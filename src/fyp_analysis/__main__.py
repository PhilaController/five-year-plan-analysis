"""Five Year Plan Analysis file for ensuring the package is executable.

The package can be run as `fyp-analysis` and `python -m fyp_analysis`.
"""
from pathlib import Path

from kedro.framework.project import configure_project

from .cli import run


def main():
    """Run the fyp_analysis code."""
    configure_project(Path(__file__).parent.name)
    run()


if __name__ == "__main__":
    main()
