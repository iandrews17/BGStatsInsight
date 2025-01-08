import pandas as pd
import json
from collections import Counter
import matplotlib.pyplot as plt

# Load JSON data into a DataFrame
with open("PlayedGames-play-241211173201.json", "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.json_normalize(data)
# df = pd.DataFrame(data)

# Preview the data
print(df.head())

print(df.info())

# # Access the "plays" entry
# plays = data.get("plays", [])  # Default to an empty list if "plays" is missing
#
# # Extract all gameRefId values
# game_ref_ids = [entry["gameRefId"] for entry in plays if "gameRefId" in entry]
#
# # Count occurrences of each gameRefId
# game_ref_counts = Counter(game_ref_ids)
#
# # Print the results
# for game_id, count in game_ref_counts.items():
#     print(f"GameRefId {game_id}: {count} times")

# Access the "plays" and "games" entries
plays = data.get("plays", [])
games = data.get("games", [])

# Create a mapping from game "id" to "name"
id_to_name = {game["id"]: game["name"] for game in games if "id" in game and "name" in game}

# Extract all gameRefId values
game_ref_ids = [entry["gameRefId"] for entry in plays if "gameRefId" in entry]

# Count occurrences of each gameRefId
game_ref_counts = Counter(game_ref_ids)

# Replace gameRefId with game names using the mapping
output = {
    id_to_name.get(game_id, f"Unknown Game (ID: {game_id})"): count
    for game_id, count in game_ref_counts.items()
}

# Sort the output from greatest to least
sorted_output = sorted(output.items(), key=lambda x: x[1], reverse=True)[:10]

# Print the results
# for game_name, count in sorted_output:
#     print(f"{game_name}: {count} times")

# Separate the sorted names and counts for visualization
game_names = [item[0] for item in sorted_output]
game_counts = [item[1] for item in sorted_output]

# Create the bar chart
plt.figure(figsize=(10, 6))
plt.bar(game_names, game_counts, color='skyblue')

# Add labels and title
plt.xlabel('Game Names', fontsize=12)
plt.ylabel('Play Counts', fontsize=12)
plt.title('Number of Plays per Game', fontsize=16)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.tight_layout()

# Show the plot
plt.show()