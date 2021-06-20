"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline

from .pipelines import data_processing as dp
from .pipelines import modeling as mod


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipeline.

    Returns
    -------
        A mapping from a pipeline name to a ``Pipeline`` object.
    """
    data_processing_pipeline = dp.create_pipeline()
    modeling_pipeline = mod.create_pipeline()

    return {
        "__default__": data_processing_pipeline + modeling_pipeline,
        "dp": data_processing_pipeline,
        "mod": modeling_pipeline,
    }
