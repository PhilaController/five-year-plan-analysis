import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin
from sklearn.exceptions import NotFittedError
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer


def _drop_missing(df):
    return df.dropna(how="any", axis=1)


def _impute_missing(df, method="ffill"):
    """Impute missing values."""
    return df.fillna(method=method)


def _remove_incomplete_features(X):
    """Remove incomplete indicators based on first row"""
    # Remove NaNs
    first_row = X.iloc[0]
    allowed = first_row.index[first_row.notnull()]
    return X[allowed]


class TrimByMinYear(TransformerMixin):
    """Trim by the minimum year."""

    def __init__(self, min_year=1996):
        self.min_year = min_year
        super().__init__()

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.loc[str(self.min_year) :]

    def inverse_transform(self, X):
        return X


def get_selected_features(X, min_year):
    """Select features based on a minimum"""

    select_pipeline = make_pipeline(
        TrimByMinYear(min_year=min_year),
        FunctionTransformer(_remove_incomplete_features),
        FunctionTransformer(_impute_missing),
        FunctionTransformer(_drop_missing),
    )

    return select_pipeline.fit_transform(X)


class PreprocessPipeline(TransformerMixin):
    """Scale features for regression."""

    def __init__(self, guide):
        self.guide_ = guide
        self.columns_ = sorted(guide["variable"].unique())

    def fit(self, X, y=None):
        self.X0_ = X.asfreq("QS").copy()
        if not all(col in self.columns_ for col in X.columns):
            raise ValueError("There are unknown columns in input data")
        return self

    def transform(self, X):
        if not hasattr(self, "X0_"):
            raise NotFittedError(
                (
                    f"This {self.__class__.__name__} instance is not fitted yet. "
                    "Call 'fit' with appropriate arguments before using this estimator."
                )
            )

        out = X.copy().asfreq("QS")
        for col in out.columns:

            # feature
            feature = out.pop(col)
            newcol = col

            # Info for this column
            guide = self.guide_.query(f"variable == '{col}'").squeeze()

            # Take the log
            if guide["loggable"]:
                feature = np.log(feature)
                newcol = f"Ln.{newcol}"
            else:
                feature = feature / guide["norm"]

            # Diffs
            ndiffs = guide.ndiffs
            while ndiffs > 0:
                feature = feature.diff(periods=guide["periods"])
                newcol = f"D.{newcol}"
                ndiffs -= 1

            out[newcol] = feature

        return out.dropna()

    def inverse_transform(self, X):
        if not hasattr(self, "X0_"):
            raise NotFittedError(
                (
                    f"This {self.__class__.__name__} instance is not fitted yet. "
                    "Call 'fit' with appropriate arguments before using this estimator."
                )
            )

        # Return a copy
        out = X.copy().asfreq("QS")

        for col in out.columns:

            # Check columns
            newcol = col
            origcol = col.split(".")[-1]
            if origcol not in self.X0_.columns:
                raise ValueError(f"Unknown column: {col}")

            # Info for this column
            guide = self.guide_.query(f"variable == '{origcol}'").squeeze()

            # Get the feature
            feature0 = self.X0_[origcol].copy()
            feature = out.pop(col)

            # Log
            if guide["loggable"]:
                feature0 = np.log(feature0)
            else:
                feature0 /= guide["norm"]

            # Diffs
            ndiffs = guide.ndiffs
            while ndiffs > 0:

                # Merge
                M = pd.concat([feature0, feature], axis=1).dropna(how="all")

                # Diff the original data
                for i in range(0, ndiffs - 1):
                    M[origcol] = M[origcol].diff(periods=guide["periods"])

                # Require overlap between input and original data
                if M.notnull().all(axis=1).sum() == 0:
                    raise ValueError("No overlap between input and original datasets")

                # Determine start date
                start_date = M[col].dropna().index.min()

                M[col] = M[col].fillna(M[origcol])
                for dt in M.loc[start_date:].index:
                    shifted_index = dt - guide["periods"] * M.index.freq
                    M.loc[dt, col] = M.loc[dt, col] + M.loc[shifted_index, col]

                # Make a copy and trim to input index
                feature = M[col].copy()
                feature = feature.loc[X.index]

                # Update
                newcol = newcol[2:]
                ndiffs -= 1

            if newcol.startswith("Ln."):
                feature = np.exp(feature)
                newcol = newcol[3:]
            feature *= guide["norm"]

            out[newcol] = feature

        return out
