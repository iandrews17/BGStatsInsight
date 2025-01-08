from datetime import datetime
import pandas as pd
import json
from collections import defaultdict
from collections import Counter
import matplotlib.pyplot as plt

# Load JSON data into a DataFrame
with open("PlayedGames-play-241211173201.json", "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.json_normalize(data)
# Define the cutoff for "before 2024"
cutoff_date = 20240101

# Access the "plays", "games", and "players" entries
plays = data.get("plays", [])
games = data.get("games", [])
players = data.get("players", [])

# Initialize dictionaries to track wins and plays
player_game_stats_before = defaultdict(lambda: {"wins": 0, "plays": 0})
player_game_stats_total = defaultdict(lambda: {"wins": 0, "plays": 0})

# Create a mapping from game "id" to "name"
id_to_game_info = {game["id"]: {"name": game["name"], "cooperative": game.get("cooperative", False)}
                   for game in games if "id" in game and "name" in game}
# Create a mapping from player "id" to "name"
id_to_player_name = {player["id"]: player["name"] for player in players if "id" in player and "name" in player}

# Process each play entry
for play in plays:
    game_id = play.get("gameRefId")
    play_date = play.get("playDateYmd")
    player_scores = play.get("playerScores", [])

    for score in player_scores:
        player_id = score.get("playerRefId")
        winner = score.get("winner", False)

        if player_id is not None and game_id is not None:
            # Check if the game is cooperative and skip if it is
            if id_to_game_info.get(game_id, {}).get("cooperative", False):
                continue

            # Update overall stats
            total_stats = player_game_stats_total[(player_id, game_id)]
            total_stats["plays"] += 1
            if winner:
                total_stats["wins"] += 1

            # Update stats for before 2024
            if play_date and play_date < cutoff_date:
                before_stats = player_game_stats_before[(player_id, game_id)]
                before_stats["plays"] += 1
                if winner:
                    before_stats["wins"] += 1

# Compare win rates
win_rate_changes = defaultdict(list)
consistent_performance = defaultdict(lambda: {"low_win_rate": [], "high_win_rate": []})

for player_id, player_name in id_to_player_name.items():
    for game_id, game_info in id_to_game_info.items():
        game_name = game_info["name"]

        # Get stats for before 2024 and total
        stats_before = player_game_stats_before.get((player_id, game_id), {"wins": 0, "plays": 0})
        stats_total = player_game_stats_total.get((player_id, game_id), {"wins": 0, "plays": 0})

        wins_before, plays_before = stats_before["wins"], stats_before["plays"]
        wins_total, plays_total = stats_total["wins"], stats_total["plays"]

        # Filter out games not played before 2024
        if plays_before == 0 or plays_total < 3:
            continue

        # Calculate win rates
        win_rate_before = (wins_before / plays_before) * 100 if plays_before > 0 else 0
        win_rate_total = (wins_total / plays_total) * 100 if plays_total > 0 else 0

        # Calculate change in win rate
        change = win_rate_total - win_rate_before

        # Add to the result
        win_rate_changes[player_name].append({
            "game": game_name,
            "win_rate_before": win_rate_before,
            "win_rate_total": win_rate_total,
            "change": change,
            "plays_before": plays_before,
            "plays_total": plays_total
        })

        # Identify consistent performance
        if win_rate_total < 20:
            consistent_performance[player_name]["low_win_rate"].append(game_name)
        elif win_rate_total > 80:
            consistent_performance[player_name]["high_win_rate"].append(game_name)

# Display the results, sorted by biggest changes
for player_name, games_info in win_rate_changes.items():
    print(f"{player_name}'s Top 5 Win Rate Changes:")
    top_games = sorted(games_info, key=lambda x: abs(x["change"]), reverse=True)[:5]
    for game_info in top_games:
        print(f"  {game_info['game']}: {game_info['win_rate_before']:.2f}% -> {game_info['win_rate_total']:.2f}% "
              f"(Change: {game_info['change']:+.2f}%, Before Plays: {game_info['plays_before']}, Total Plays: {game_info['plays_total']})")
    print()  # Add an empty line between players

# Display consistent performance
for player_name, performance in consistent_performance.items():
    print(f"{player_name}'s Consistent Performance:")
    if performance["low_win_rate"]:
        print(f"  Low Win Rate (<20%): {', '.join(performance['low_win_rate'])}")
    if performance["high_win_rate"]:
        print(f"  High Win Rate (>80%): {', '.join(performance['high_win_rate'])}")
    print()
