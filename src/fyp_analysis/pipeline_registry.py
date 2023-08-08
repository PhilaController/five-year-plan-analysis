"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from .pipelines import data_processing as dp
from .pipelines import forecast
from .pipelines import forecast_prep as fp


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipeline.

    Returns
    -------
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    data_processing_pipeline = dp.create_pipeline()
    forecast_prep_pipeline = fp.create_pipeline()
    forecast_pipeline = forecast.create_pipeline()

    return {
        "__default__": data_processing_pipeline
        + forecast_prep_pipeline
        + forecast_pipeline,
        "dp": data_processing_pipeline,
        "fp": forecast_prep_pipeline,
        "forecast": forecast_pipeline,
    }
