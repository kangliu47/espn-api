#%%
import sys
import os

script_path = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_path, "../.."))
sys.path.append(project_root)

import pandas as pd
from analysis.utils.constants import stats_2020_path, stats_2021_path
from analysis.player_rating import (
    get_players_pool,
    get_player_ratings,
    combine_player_data,
)

stats_2021 = pd.read_csv(stats_2021_path).dropna()
stats_2020 = pd.read_csv(stats_2020_path).dropna()

players_pool = get_players_pool(n_teams=13, n_players=13, over_write=400)
ratings_2021 = get_player_ratings(stats_2021, players_pool=players_pool)
ratings_2020 = get_player_ratings(stats_2020, players_pool=players_pool)
player_ratings = combine_player_data(data_2020=ratings_2020, data_2021=ratings_2021)

player_stats = combine_player_data(
    data_2020=stats_2020.set_index("name"), data_2021=stats_2021.set_index("name")
)

# %%
from analysis.player_rating import get_expected_salary, get_similar_players

name = "James Harden"
name = "Jayson Tatum"
name = "Chris Paul"
name = "Clint Capela"
get_similar_players(name, player_ratings=player_ratings, score_method="euclidean")


#%%
salary = get_expected_salary(player_ratings)
salary.head(20)


# %%
