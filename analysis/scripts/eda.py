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

info_cols = [
    "name",
    "position",
    "pro_team",
]

stats_counts = [
    "PTS",
    "BLK",
    "STL",
    "AST",
    "REB",
    "3PTM",
]

shooting_counts = [
    "FGM",
    "FGA",
    "FTM",
    "FTA",
]
percentages = [
    "FG%",
    "FT%",
]


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


#%%

data = stats_2021

n_teams = 14
n_players = 13
players_pool = n_teams * n_players
players_pool = 400
data_top = data.head(players_pool).set_index("name").fillna(0)
mean_stats_counts = data_top[stats_counts].mean()
std_stats_counts = data_top[stats_counts].std()

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
normalized_data.sort_values(by="overall", ascending=False).head(50)

# * 1 - autocomplete input
# * 2 - percentage baseline slider
# * 3 - player pool size slider
# * 4 - stats dropdown (2020 or 2021)
# * 5 - category for color dropdown (PTS, STL etc)
# * 6 - add player name label
# * 7 - dataframe with selection

# %%

import hvplot.pandas
import holoviews as hv
from holoviews import opts
from holoviews import dim

hv.extension("bokeh")

punt_cat = "PTS"
punt_col = f"PUNT_{punt_cat}"
normalized_data[punt_col] = normalized_data["overall"] - normalized_data[punt_cat]

scatter = (
    normalized_data.reset_index()
    .hvplot.scatter(
        x="FGR",
        y="FTR",
        c=punt_col,
        hover_cols=["name", "overall", "pro_team", punt_col],
    )
    .opts(
        width=800,
        height=800,
        size=abs(dim(punt_col)) * 2,
        title=f"total players {players_pool}",
    )
)
scatter


#%%

hv.save(
    scatter, os.path.join(project_root, "data", f"{punt_col}_scatter_2021.html"),
)

# %%

hist_plots = {}
for col in stats_counts:
    hist_plots[col] = (
        data_top[col].hvplot.hist(normed=True) * data_top[col].hvplot.kde()
    )
stats_2020_distribution = hv.Layout(list(hist_plots.values())).cols(1)
hv.save(
    stats_2020_distribution,
    os.path.join(project_root, "data", "top_182_players_stats_distribution.html"),
)
# %%
