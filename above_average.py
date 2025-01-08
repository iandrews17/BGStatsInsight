from datetime import datetime
import pandas as pd
import json
from collections import defaultdict
from collections import Counter
import matplotlib.pyplot as plt
import re

def evaluate_score(score):
    if not score:
        return 0
    # Check for expression-like scores and evaluate them
    if re.search(r'\d+[+\-*/]\d+', score):
        try:
            return eval(score)
        except Exception:
            return 0  # Fallback in case of evaluation errors
    return int(score)

# Load JSON data into a DataFrame
with open("PlayedGames-play-241211173201.json", "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.json_normalize(data)

# Access the "plays", "games", and "players" entries
plays = data.get("plays", [])
games = data.get("games", [])
players = data.get("players", [])

# Create a mapping from game "id" to "name"
id_to_game_info = {game["id"]: {"name": game["name"], "cooperative": game.get("cooperative", False)}
                   for game in games if "id" in game and "name" in game}

# Create a mapping from player "id" to "name"
id_to_player_name = {player["id"]: player["name"] for player in players if "id" in player and "name" in player}

# Track total scores and play counts for each player in each game
player_game_scores = defaultdict(lambda: {"total_score": 0, "play_count": 0})
player_score_diffs = defaultdict(lambda: {"total_diff": 0, "play_count": 0})

from collections import defaultdict

# Track score differences for each player in each game
player_score_diffs = defaultdict(lambda: {"total_diff": 0, "play_count": 0})

# Process each play
for play in plays:
    game_id = play.get("gameRefId")
    player_scores = play.get("playerScores", [])

    # Skip cooperative games
    if game_id and id_to_game_info.get(game_id, {}).get("cooperative", False):
        continue

    # Collect scores for this play
    scores = []
    for score in player_scores:
        player_id = score.get("playerRefId")
        if player_id is not None:
            # Handle multi-part scores like "3+20+5+31"
            player_score = evaluate_score(score.get("score"))

            scores.append((player_id, player_score))

    # Skip plays with fewer than 2 players
    if len(scores) < 2:
        continue

    # Calculate score differences
    total_scores = [s[1] for s in scores]
    for player_id, player_score in scores:
        # Average score of other players
        other_scores = [s for s in total_scores if s != player_score]
        if other_scores:
            avg_others_score = sum(other_scores) / len(other_scores)
            score_diff = player_score - avg_others_score

            # Update stats for this player and game
            player_score_diffs[(player_id, game_id)]["total_diff"] += score_diff
            player_score_diffs[(player_id, game_id)]["play_count"] += 1

# Calculate average score differences and group by player
player_top_diffs = defaultdict(list)

for (player_id, game_id), stats in player_score_diffs.items():
    total_diff = stats["total_diff"]
    play_count = stats["play_count"]

    if play_count > 3:
        avg_diff = total_diff / play_count
        game_name = id_to_game_info.get(game_id, {}).get("name", "Unknown Game")
        player_top_diffs[player_id].append((game_name, avg_diff))

# # Display the top 5 average score differences for each player
# print("Top 5 Average Score Differences for Each Player:")
# for player_id, game_diffs in player_top_diffs.items():
#     player_name = id_to_player_name.get(player_id, "Unknown Player")
#     print(f"\n{player_name}:")
#
#     # Sort by score difference and get the top 5
#     top_games = sorted(game_diffs, key=lambda x: x[1], reverse=True)[:5]
#     for game_name, avg_diff in top_games:
#         print(f"  {game_name}: Average Score Difference = {avg_diff:.2f}")


from collections import defaultdict
import math

# Track score differences and average others' scores for each player in each game
player_score_diffs = defaultdict(lambda: {"total_diff": 0, "total_others_score": 0, "play_count": 0})

# Process each play
for play in plays:
    game_id = play.get("gameRefId")
    player_scores = play.get("playerScores", [])

    # Skip cooperative games
    if game_id and id_to_game_info.get(game_id, {}).get("cooperative", False):
        continue

    # Collect scores for this play
    scores = []
    for score in player_scores:
        player_id = score.get("playerRefId")
        if player_id is not None:
            # Handle multi-part scores like "3+20+5+31"
            player_score = evaluate_score(score.get("score"))

            scores.append((player_id, player_score))

    # Skip plays with fewer than 2 players
    if len(scores) < 2:
        continue

    # Calculate score differences
    total_scores = [s[1] for s in scores]
    for player_id, player_score in scores:
        # Average score of other players
        other_scores = [s for s in total_scores if s != player_score]
        if other_scores:
            avg_others_score = sum(other_scores) / len(other_scores)
            score_diff = player_score - avg_others_score

            # Update stats for this player and game
            player_score_diffs[(player_id, game_id)]["total_diff"] += score_diff
            player_score_diffs[(player_id, game_id)]["total_others_score"] += avg_others_score
            player_score_diffs[(player_id, game_id)]["play_count"] += 1

# Calculate average score differences and group by player
player_top_diffs = defaultdict(list)

for (player_id, game_id), stats in player_score_diffs.items():
    total_diff = stats["total_diff"]
    total_others_score = stats["total_others_score"]
    play_count = stats["play_count"]

    if play_count > 3:
        avg_diff = total_diff / play_count
        avg_others_score = total_others_score / play_count
        game_name = id_to_game_info.get(game_id, {}).get("name", "Unknown Game")
        player_top_diffs[player_id].append((game_name, avg_diff, avg_others_score))

# Display the top 5 average score differences for each player
# print("Top 5 Average Score Differences for Each Player:")
# for player_id, game_diffs in player_top_diffs.items():
#     player_name = id_to_player_name.get(player_id, "Unknown Player")
#     print(f"\n{player_name}:")
#
#     # Sort by score difference and get the top 5
#     top_games = sorted(game_diffs, key=lambda x: x[1], reverse=True)[:10]
#     for game_name, avg_diff, avg_others_score in top_games:
#         print(f"  {game_name}: Average Score Difference = {avg_diff:.2f}, "
#               f"Average Others' Score = {avg_others_score:.2f}")

from collections import defaultdict
from scipy.stats import ttest_ind

# Initialize dictionaries to track scores
player_game_scores = defaultdict(list)
game_scores = defaultdict(list)
t_test_results = defaultdict(list)

# Gather scores for each game and player
for play in plays:
    game_id = play.get("gameRefId")
    player_scores = play.get("playerScores", [])

    # Skip cooperative games
    if game_id and id_to_game_info.get(game_id, {}).get("cooperative", False):
        continue

    # Collect scores
    for score in player_scores:

        player_id = score.get("playerRefId")
        if player_id is not None:
            player_score = evaluate_score(score.get("score"))
            if player_score == 0:
                continue
            player_game_scores[(player_id, game_id)].append(player_score)
            game_scores[game_id].append(player_score)

# Perform t-tests for each player and game
for (player_id, game_id), player_scores in player_game_scores.items():
    other_scores = [score for score in game_scores[game_id] if score not in player_scores]

    # Skip games where the player or others have insufficient plays
    if len(player_scores) < 3 or len(other_scores) < 3:
        continue

    # Perform t-test
    t_stat, p_value = ttest_ind(player_scores, other_scores, equal_var=False)

    # Store results
    player_name = id_to_player_name.get(player_id, "Unknown Player")
    game_name = id_to_game_info.get(game_id, {}).get("name", "Unknown Game")
    avg_player_score = sum(player_scores) / len(player_scores)
    avg_other_score = sum(other_scores) / len(other_scores)

    t_test_results[player_name].append({
        "game": game_name,
        "t_stat": t_stat,
        "p_value": p_value,
        "avg_player_score": avg_player_score,
        "avg_other_score": avg_other_score,
        "player_plays": len(player_scores),
        "other_plays": len(other_scores)
    })

# Display top 5 significant results per player
print("Top 5 Significant T-Test Results for Each Player:")
for player_name, games in t_test_results.items():
    print(f"\n{player_name}:")
    # Sort by absolute t-statistic to highlight most significant results
    top_games = sorted(games, key=lambda x: abs(x["t_stat"]), reverse=True)[:5]    for result in top_games:
        print(f"  {result['game']}:")
        print(f"    T-Statistic = {result['t_stat']:.2f}, P-Value = {result['p_value']:.4f}")
        print(f"    Avg Player Score = {result['avg_player_score']:.2f}, Avg Others Score = {result['avg_other_score']:.2f}")
        print(f"    Plays (Player: {result['player_plays']}, Others: {result['other_plays']})")
