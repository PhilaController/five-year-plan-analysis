from .carto import DataSourceCARTO
from .core import (
    ALLOWED_FREQ,
    ALLOWED_GEO,
    ALLOWED_SOURCES,
    DataSource,
    get_economic_indicators,
)
from .fred import DataSourceFRED
from .quandl import DataSourceQuandl
from .zillow import DataSourceZillow

# The names of the indicators
INDICATORS = sorted([d["name"] for cls in DataSource.REGISTRY for d in cls.SOURCES])
