from typing import Tuple

import matplotlib as mpl
import pandas as pd
from loguru import logger
from matplotlib import pyplot as plt
from phila_style.matplotlib import get_theme


def plot_forecast_results(
    forecast: pd.DataFrame,
    main_endog: str,
    figsize: Tuple[int, int] = (10, 6),
) -> mpl.figure.Figure:
    """
    Make some diagnostic plots based on the input forecast.

    Parameters
    ----------
    forecast
        The input forecast to plot
    main_endog
        The main endog column of interest that we are forecasting
    figsize, optional
        The figure size

    Returns
    -------
    The matplotlib figure
    """
    with plt.style.context(get_theme()):

        # Initialize the figure
        fig = plt.figure(constrained_layout=False, dpi=300, figsize=figsize)

        # Set up the grid
        nrows = 2
        ncols = len(forecast.columns)
        if ncols == 4:
            ncols = 2
            nrows += 1
        elif ncols == 5:
            ncols = 3
            nrows += 1
        gs = fig.add_gridspec(nrows=nrows, ncols=ncols, hspace=0.5, wspace=0.5)

        # Sum forecast over fiscal year
        Y = forecast.groupby(forecast.index.shift(2, freq="QS").year).sum()[main_endog]

        # Figure out current fiscal year
        PLAN_YEARS = 5
        current_fiscal_year = Y.index[-(PLAN_YEARS + 1)]

        # Plot fiscal year change
        ax = fig.add_subplot(gs[0, :])
        Y.plot(ax=ax, zorder=6)
        ax.axvline(x=current_fiscal_year, color="#cc3000", zorder=5)
        ax.set_xlim(1997)

        # Print out year-over-year change
        logger.info("Year-over-Year Change")
        logger.info((Y.diff() / Y.shift()).tail(n=7))

        # Plot quarterly forecasts
        for i, col in enumerate(forecast.columns):

            if len(forecast.columns) <= 3:
                ax = fig.add_subplot(gs[1, i])
            else:
                if i < ncols:
                    ax = fig.add_subplot(gs[1, i])
                else:
                    ax = fig.add_subplot(gs[2, i - ncols])

            # Plot
            forecast[col].plot(ax=ax, zorder=6, lw=1.5, rot=90)
            ax.axvline(
                x=f"{current_fiscal_year}-06-30", color="#cc3000", zorder=5, lw=1
            )
            ax.set_title(col, fontsize=10)

    return fig

    # def plot_forecast(
    #     self, *tax_bases, figsize=(6, 4), ax=None, start_year=2010, **kwargs
    # ):
    #     """Plot the forecast, comparing to the Mayor's projections"""

    #     # Comparison
    #     comparison = self.get_mayor_comparison(*tax_bases)

    #     # Put into millions
    #     for col in comparison:
    #         comparison[col] /= 1e6

    #     # Columns
    #     col = f"{self.name}Revenue"

    #     # Plot
    #     with plt.style.context(get_theme()):

    #         if ax is None:
    #             fig, ax = plt.subplots(figsize=figsize, **kwargs)
    #         else:
    #             fig = ax.figure

    #         colors = get_default_palette()
    #         kws = dict(
    #             lw=3,
    #             mew=2,
    #             alpha=0.9,
    #         )

    #         # Plot 2020 vertical line
    #         ax.axvline(x=2020, c=colors["dark-grey"], lw=3)

    #         # Plot historic
    #         color = colors["medium-grey"]
    #         comparison[col].loc[start_year:2020].plot(
    #             ax=ax,
    #             marker="o",
    #             color=color,
    #             mec=color,
    #             mfc="white",
    #             label="",
    #             **kws,
    #         )

    #         F = comparison.loc[2020:].copy()
    #         F[f"{col}Budget"] = F[f"{col}Budget"].fillna(F[col])

    #         # Plot Controller
    #         color = colors["blue"]
    #         F[col].plot(
    #             ax=ax,
    #             marker="o",
    #             color=color,
    #             mec=color,
    #             mfc="white",
    #             label="Per Controller",
    #             **kws,
    #         )

    #         # Plot Mayor
    #         color = colors["green"]
    #         F[f"{col}Budget"].plot(
    #             ax=ax,
    #             marker="o",
    #             color=color,
    #             mec=color,
    #             mfc="white",
    #             label="Per Five Year Plan",
    #             **kws,
    #         )

    #         ax.set_xlabel("Fiscal Year", fontsize=11)
    #         ax.set_yticklabels([f"${x:,.0f}M" for x in ax.get_yticks()], fontsize=11)
    #         ax.legend(
    #             loc="lower center",
    #             bbox_transform=ax.transAxes,
    #             bbox_to_anchor=(0.5, 1),
    #             ncol=2,
    #             fontsize=11,
    #         )

    # def plot_differences(
    #     self, *tax_bases, ax=None, figsize=(6, 4), cumulative=True, **kwargs
    # ):
    #     """Plot the differences between the forecast and the Mayor's projections"""

    #     # Comparison
    #     comparison = self.get_mayor_comparison(*tax_bases).dropna()

    #     # Put into millions
    #     for col in comparison:
    #         comparison[col] /= 1e6

    #     # Columns
    #     col = f"{self.name}Revenue"

    #     # Diff
    #     diff = comparison[col] - comparison[f"{col}Budget"]
    #     if cumulative:
    #         diff = diff.cumsum()

    #     # Plot
    #     with plt.style.context(get_theme()):

    #         if ax is None:
    #             fig, ax = plt.subplots(figsize=figsize, **kwargs)
    #         else:
    #             fig = ax.figure

    #         colors = get_default_palette()

    #         # Plot
    #         ax.axhline(y=0, color=colors["almost-black"], lw=3, zorder=11)
    #         diff.plot(kind="bar", color=colors["medium-grey"], zorder=10)

    #         ax.set_xlabel("Fiscal Year", fontsize=11)

    #         def format_label(x):
    #             if x >= 0:
    #                 return f"${x:,.0f}M"
    #             else:
    #                 return "\u2212" + f"${abs(x):,.0f}M"

    #         ax.set_yticklabels([format_label(x) for x in ax.get_yticks()], fontsize=11)

    #         for i, (yr, value) in enumerate(diff.iteritems()):
    #             va = "top" if value < 0 else "bottom"
    #             offset = -0.5 if value < 0.5 else 1
    #             ax.text(
    #                 i,
    #                 value + offset,
    #                 format_label(value),
    #                 ha="center",
    #                 va=va,
    #                 bbox=dict(facecolor="white", pad=0, alpha=0.5),
    #                 weight="bold",
    #                 fontsize=9,
    #             )

    #         if cumulative:
    #             title = "Cumulative Differences"
    #         else:
    #             title = "Differences by FY"
    #         ax.text(
    #             0.5,
    #             1.05,
    #             title,
    #             ha="center",
    #             va="bottom",
    #             fontsize=11,
    #             weight="bold",
    #             transform=ax.transAxes,
    #         )

    # def plot_summary(
    #     self,
    #     *tax_bases,
    #     figsize=(6, 5),
    #     start_year=2010,
    #     hspace=0.5,
    #     wspace=0.35,
    #     top=0.88,
    #     bottom=0.15,
    #     left=0.09,
    #     right=0.98,
    #     **gridspec_kws,
    # ):
    #     """Plot a summary comparison of the projection."""

    #     # Plot
    #     with plt.style.context(get_theme()):

    #         fig = plt.figure(constrained_layout=False, dpi=300, figsize=figsize)
    #         gs = fig.add_gridspec(
    #             nrows=2,
    #             ncols=2,
    #             hspace=hspace,
    #             wspace=wspace,
    #             top=top,
    #             left=left,
    #             right=right,
    #             bottom=bottom,
    #             **gridspec_kws,
    #         )

    #         ax = fig.add_subplot(gs[0, :])
    #         self.plot_forecast(*tax_bases, ax=ax, start_year=start_year)

    #         ax = fig.add_subplot(gs[1, 0])
    #         self.plot_differences(*tax_bases, ax=ax, cumulative=False)

    #         ax = fig.add_subplot(gs[1, 1])
    #         self.plot_differences(*tax_bases, ax=ax, cumulative=True)

    #         # Add a title
    #         FY = self.mayor_projections["fiscal_year"].astype(str).str.slice(-2)
    #         tag = f"Five Year Plan FY{FY.iloc[0]}-FY{FY.iloc[-1]}"
    #         title = f"{tag} Projection Comparison: {self.name}"
    #         fig.text(
    #             0.5, 0.99, title, fontsize=14, weight="bold", ha="center", va="top"
    #         )

    #     return fig
