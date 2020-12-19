#%%
import sys
import os

script_path = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_path, "../.."))
sys.path.append(project_root)

from espn_api.requests.espn_requests import EspnFantasyRequests
from analysis.utils.helpers import load_cookies, league_id

cookies = load_cookies(project_root=project_root)

# %%
my_league = EspnFantasyRequests(sport="nba", league_id=league_id, year=2021)

# %%
players =my_league.get_pro_players()
# %%