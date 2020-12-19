#%%
import sys
import os

script_path = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_path, "../.."))
sys.path.append(project_root)
import pandas as pd
import hvplot.pandas
import holoviews as hv
from holoviews import opts

hv.extension("bokeh")
#%%


def get_best_left_overt(draft_kit: pd.DataFrame) -> pd.DataFrame:
    not_drafted = draft_kit["drafted_by"] == "free_agent"
    left_over = draft_kit[not_drafted]
    return left_over

draft_kit = pd.read_csv(
    os.path.join(project_root, "data", "draft_kit.csv"), index_col=0
)
best_left_over = get_best_left_overt(draft_kit)
total_money_spent = draft_kit.groupby("drafted_by").agg({"price": sum})
total_money_spent


# %%
# * 1 - richie
# * 2 - han
# * 3 - dunkers
# * 4 - htown
# * 5 - yang
# * 6 - tyson
# * 7 - nofux - mark
# * 8 - lottery - jiawen
# * 9 - tbbt
# * 10 - yihui
# * 11 - badger
# * 12 - ggb
# * 13 - madison
# * 14 - td

