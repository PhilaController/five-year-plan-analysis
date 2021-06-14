from kedro.pipeline import Pipeline, node

from .nodes import get_economic_indicators


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=get_economic_indicators,
                inputs=["params:fresh_indicators"],
                outputs="economic_indicators",
                name="economic_indicators_node",
            ),
        ]
    )
