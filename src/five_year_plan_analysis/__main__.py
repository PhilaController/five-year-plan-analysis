"""
Five Year Plan Analysis file for ensuring the package is executable
as `five-year-plan-analysis` and `python -m five_year_plan_analysis`
"""
from pathlib import Path

from kedro.framework.project import configure_project

from .cli import run


def main():
    configure_project(Path(__file__).parent.name)
    run()


if __name__ == "__main__":
    main()
