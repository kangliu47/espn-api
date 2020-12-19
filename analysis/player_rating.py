import pandas as pd
from .utils.constants import stats_counts, shooting_counts
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances


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


def get_similar_players(
    name: str,
    player_ratings: pd.DataFrame,
    score_method: str = "euclidean",
    feature_cols: list = ["PTS", "BLK", "STL", "AST", "REB", "3PTM", "FGR", "FTR"],
    n_players: int = 10,
) -> pd.DataFrame:

    function_and_sorting = {
        "cosine": (cosine_similarity, False),
        "euclidean": (euclidean_distances, True),
    }
    score_function, sort_ascending = function_and_sorting[score_method]
    one_player = player_ratings.loc[name, feature_cols].to_frame().T
    all_scores = score_function(X=one_player, Y=player_ratings[feature_cols])
    similar_players = player_ratings.copy()
    similar_players[score_method] = all_scores.reshape(-1, 1)
    return similar_players.sort_values(by=score_method, ascending=sort_ascending).head(
        n_players
    )


def get_expected_salary(
    player_ratings: pd.DataFrame,
    players_per_team: int = 13,
    n_teams: int = 13,
    one_dollar_rank: int = None,
):
    #! This method would not work for player_ratings calculated with only relevant players
    relevant_players = players_per_team * n_teams

    if one_dollar_rank is None:
        one_dollar_rank = relevant_players

    assert one_dollar_rank <= relevant_players
    num_one_dollar_guys = relevant_players - one_dollar_rank
    total_rating = player_ratings.head(one_dollar_rank)["overall"].sum()
    salary_factor = (n_teams * 200 - num_one_dollar_guys) / total_rating
    more_than_one_dollar = (
        salary_factor * player_ratings["overall"].iloc[:one_dollar_rank]
    )
    one_dollar_players = pd.Series(
        np.ones(shape=(player_ratings.iloc[one_dollar_rank:].shape[0])),
        index=player_ratings.index[one_dollar_rank:],
    )
    salary_expectation = pd.concat([more_than_one_dollar, one_dollar_players])
    return salary_expectation


def combine_player_data(
    data_2020: pd.DataFrame, data_2021: pd.DataFrame
) -> pd.DataFrame:
    missing_players = list(set(data_2020.index) - set(data_2021.index))
    data_2021["stats_type"] = "2021_projection"
    fill_with_2020 = data_2020.loc[missing_players]
    fill_with_2020["stats_type"] = "2020_stats"
    combined_data = pd.concat([data_2021, fill_with_2020])
    if "overall" in combined_data.columns:
        return combined_data.sort_values(by="overall", ascending=False)
    else:
        return combined_data
