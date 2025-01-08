import json
from collections import defaultdict

# Load the JSON file
with open("PlayedGames-play-241211173201.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Access the "plays", "games", and "players" entries
plays = data.get("plays", [])
games = data.get("games", [])
players = data.get("players", [])

# Create a mapping from game "id" to "name"
id_to_game_info = {game["id"]: {"name": game["name"], "cooperative": game.get("cooperative", False)}
                   for game in games if "id" in game and "name" in game}
# Create a mapping from player "id" to "name"
id_to_player_name = {player["id"]: player["name"] for player in players if "id" in player and "name" in player}

# Initialize a dictionary to track wins and games played for each player and game
player_game_stats = defaultdict(lambda: {"wins": 0, "plays": 0})

# Process each play entry
for play in plays:
    game_id = play.get("gameRefId")
    player_scores = play.get("playerScores", [])

    for score in player_scores:
        player_id = score.get("playerRefId")
        winner = score.get("winner", False)

        if player_id is not None and game_id is not None:
            # Check if the game is cooperative and skip if it is
            if id_to_game_info.get(game_id, {}).get("cooperative", False):
                continue

            player_game_stats[(player_id, game_id)]["plays"] += 1
            if winner:
                player_game_stats[(player_id, game_id)]["wins"] += 1

# Calculate the win percentage for each player and game
player_top_games = defaultdict(list)

for (player_id, game_id), stats in player_game_stats.items():
    wins = stats["wins"]
    plays = stats["plays"]
    win_percentage = (wins / plays) * 100 if plays > 3 else 0
    player_name = id_to_player_name.get(player_id, f"Unknown Player (ID: {player_id})")
    game_info = id_to_game_info.get(game_id, {"name": f"Unknown Game (ID: {game_id})"})
    game_name = game_info["name"]
    player_top_games[player_name].append({
        "game": game_name,
        "win_percentage": win_percentage,
        "wins": wins,
        "plays": plays
    })

# Sort and pick top 3 games for each player
for player_name, games_info in player_top_games.items():
    # Sort the games by win percentage in descending order
    games_info.sort(key=lambda x: x["win_percentage"], reverse=True)
    # Keep only the top 3 games
    player_top_games[player_name] = games_info[:3]

# Display the results
for player_name, games_info in player_top_games.items():
    print(f"{player_name}'s Top 3 Games by Win Percentage:")
    for i, game_info in enumerate(games_info, start=1):
        print(f"  {i}. {game_info['game']} - {game_info['win_percentage']:.2f}% win rate "
              f"({game_info['wins']} wins out of {game_info['plays']} plays)")
    print()  # Add an empty line between players