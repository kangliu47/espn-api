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

# %%

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

# %%

data = stats_2020

n_teams = 14
n_players = 13

data_top = data.head(n_teams * n_players).set_index("name").fillna(0)

mean_stats_counts = data_top[stats_counts].mean()
std_stats_counts = data_top[stats_counts].std()

# %%


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


normalized_data = transform_stats(data_top[stats_counts])

# %%
normalized_data["overall"] = normalized_data.sum(axis=1)
normalized_data.sort_values(by="overall", ascending=False).head(50)
# %%

from sklearn.decomposition import PCA

pca = PCA(n_components=3)

pca_results = pca.fit_transform(normalized_data[stats_counts])

pca_dataframe = pd.DataFrame(
    data=pca_results, columns=["first", "second", "third"], index=normalized_data.index,
)

# %%
import hvplot.pandas
import holoviews as hv
from holoviews import opts

hv.extension("bokeh")

pca_dataframe["name"] = pca_dataframe.index
pca_dataframe.hvplot.scatter(
    x="first", y="second", hover_cols=["name", "first", "second"],
)

# %%
pca_components = pd.DataFrame(
    data=pca.components_, columns=stats_counts, index=["first", "second", "third"]
)
pca_components
# %%
hvplot.scatter_matrix(normalized_data[stats_counts])

# %%

hvplot.scatter_matrix(stats_2020[stats_counts + ["position"]], c="position")
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
