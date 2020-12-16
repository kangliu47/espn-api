import pandas as pd
from .utils.constants import stats_counts, shooting_counts


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


def add_overall_punt_one_category(
    player_ratings: pd.DataFrame, punt_cat: str = "PTS"
) -> pd.DataFrame:
    punt_col = punt_column_name(punt_cat)
    player_ratings[punt_col] = player_ratings["overall"] - player_ratings[punt_cat]
    return player_ratings


def punt_column_name(punt_cat: str) -> str:
    return f"PUNT_{punt_cat}"
