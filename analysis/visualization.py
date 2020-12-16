import pandas as pd
import hvplot.pandas
import holoviews as hv
from holoviews import opts
from holoviews import dim

hv.extension("bokeh")


def plot_stats_distribution(data: pd.DataFrame, plot_cols: list) -> hv.Layout:
    hist_plots = {}
    for col in plot_cols:
        hist_plots[col] = data[col].hvplot.hist(normed=True) * data[col].hvplot.kde()
    stats_distribution = hv.Layout(list(hist_plots.values())).cols(1)
    return stats_distribution


def plot_player_ratings_scatter(
    player_ratings: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str = "overall",
    size_col: str = "overall",
    **plot_opts,
) -> hv.Overlay:
    scatter_base = (
        player_ratings.reset_index()
        .hvplot.scatter(x=x_col, y=y_col, c=color_col, hover_cols=["name", "overall"],)
        .opts(size=abs(dim(size_col)) * 2, **plot_opts,)
    )
    overlay = (
        scatter_base * hv.VLine(0).opts(color="gray") * hv.HLine(0).opts(color="gray")
    )
    return overlay
