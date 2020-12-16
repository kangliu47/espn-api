#%%
import sys
import os

script_path = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_path, "../.."))
sys.path.append(project_root)

import pandas as pd
from analysis.utils.constants import stats_2020_path, stats_2021_path
from analysis.player_rating import get_players_pool, get_player_ratings

stats_2021 = pd.read_csv(stats_2021_path).dropna()
stats_2020 = pd.read_csv(stats_2020_path).dropna()

data = stats_2020
players_pool = get_players_pool(n_teams=13, n_players=13, over_write=400)
player_ratings = get_player_ratings(data, players_pool=players_pool)

#%%



# %%

# * 1 - autocomplete input
# * 2 - percentage baseline slider
# * 3 - player pool size slider
# * 4 - stats dropdown (2020 or 2021)
# * 5 - category for color dropdown (PTS, STL etc)
# * 6 - add player name label
# * 7 - dataframe with selection

# %%
