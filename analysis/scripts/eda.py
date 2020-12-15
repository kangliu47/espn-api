#%%
import sys
import os

script_path = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_path, "../.."))
sys.path.append(project_root)

import pandas as pd

stats_2021 = pd.read_csv(
    os.path.join(project_root, "data", "projected_2021.csv")
).dropna()
stats_2020 = pd.read_csv(os.path.join(project_root, "data", "stats_2020.csv")).dropna()

from analysis.utils.constants import (
    info_cols,
    stats_counts,
    shooting_counts,
    percentages,
)


def transform_column(one_stats: pd.Series) -> pd.Series:
    mean = one_stats.mean()
    std = one_stats.std()
    transformed = (one_stats - mean) / std
    return transformed


def transform_stats(count_type_stats: pd.DataFrame) -> pd.DataFrame:
    all_data = dict()
    for col in count_type_stats.columns:
        transformed_col = transform_column(count_type_stats[col])
        all_data[col] = transformed_col
    return pd.DataFrame(all_data, index=count_type_stats.index)


def get_percentage_rating(
    n_made: pd.Series, n_attempts: pd.Series, baseline: float
) -> pd.Series:
    result = n_attempts.copy()
    non_zero_attempts = n_attempts > 0
    result.loc[non_zero_attempts] = n_attempts.loc[non_zero_attempts] * (
        n_made.loc[non_zero_attempts] / n_attempts.loc[non_zero_attempts] - baseline
    )
    return result


def get_player_ratings(
    data: pd.DataFrame, players_pool: int, stats_counts: list = stats_counts
) -> pd.DataFrame:
    data_top = data.head(players_pool).set_index("name").fillna(0)
    # * calculate the shooting percentage
    mean_shooting_counts = data_top[shooting_counts].mean()
    field_goal_baseline = mean_shooting_counts["FGM"] / mean_shooting_counts["FGA"]
    free_throw_baseline = mean_shooting_counts["FTM"] / mean_shooting_counts["FTA"]
    data_top["FGR"] = get_percentage_rating(
        n_made=data_top["FGM"], n_attempts=data_top["FGA"], baseline=field_goal_baseline
    )
    data_top["FTR"] = get_percentage_rating(
        n_made=data_top["FTM"], n_attempts=data_top["FTA"], baseline=free_throw_baseline
    )
    normalized_data = transform_stats(data_top[stats_counts + ["FGR", "FTR"]])
    normalized_data["overall"] = normalized_data.sum(axis=1)
    return normalized_data.sort_values(by="overall", ascending=False)


def get_players_pool(
    n_teams: int = 13, n_players: int = 13, over_write: int = None
) -> int:
    if over_write is not None:
        players_pool = over_write
    else:
        players_pool = n_teams * n_players
    return players_pool


data = stats_2020
players_pool = get_players_pool(n_teams=13, n_players=13, over_write=400)
player_ratings = get_player_ratings(data, players_pool=players_pool)

# %%

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


#%%


def add_overall_punt_one_category(
    player_ratings: pd.DataFrame, punt_cat: str = "PTS"
) -> pd.DataFrame:
    punt_col = punt_column_name(punt_cat)
    player_ratings[punt_col] = player_ratings["overall"] - player_ratings[punt_cat]
    return player_ratings


def punt_column_name(punt_cat: str) -> str:
    return f"PUNT_{punt_cat}"


def plot_player_ratings_scatter(
    player_ratings: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str = "overall",
    size_col: str = "overall",
) -> hv.Scatter:
    scatter = (
        player_ratings.reset_index()
        .hvplot.scatter(x=x_col, y=y_col, c=color_col, hover_cols=["name", "overall"],)
        .opts(
            size=abs(dim(size_col)) * 2,
            title=f"total players {players_pool}",
            **plot_opts,
        )
    )
    return scatter


#%%


color_col = "overall"
size_col = "overall"
plot_opts = dict(width=800, height=800)
x_col = "FGR"
y_col = "FTR"

plot_player_ratings_scatter(player_ratings, x_col="BLK", y_col="STL")

# %%

# * 1 - autocomplete input
# * 2 - percentage baseline slider
# * 3 - player pool size slider
# * 4 - stats dropdown (2020 or 2021)
# * 5 - category for color dropdown (PTS, STL etc)
# * 6 - add player name label
# * 7 - dataframe with selection

# %%
