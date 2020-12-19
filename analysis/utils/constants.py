import os

this_file = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(this_file, "../.."))
data_dir = os.path.join(project_root, "data")
stats_2020_path = os.path.join(data_dir, "stats_2020.csv")
stats_2021_path = os.path.join(data_dir, "projected_2021.csv")

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
