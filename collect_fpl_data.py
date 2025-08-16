import json
import os
from datetime import datetime
import requests

# Replace with your league ID
LEAGUE_ID = 123456  # <- change this to your league id

BASE_URL = "https://fantasy.premierleague.com/api"

def fetch_league_standings(league_id):
    url = f"{BASE_URL}/leagues-classic/{league_id}/standings/"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def fetch_team_history(entry_id):
    url = f"{BASE_URL}/entry/{entry_id}/history/"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def fetch_team_info(entry_id):
    url = f"{BASE_URL}/entry/{entry_id}/"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def collect_data():
    league = fetch_league_standings(LEAGUE_ID)
    standings = league["standings"]["results"]

    players = []

    for s in standings:
        entry_id = s["entry"]
        team_name = s["entry_name"]
        player_name = s["player_name"]

        history = fetch_team_history(entry_id)
        team_info = fetch_team_info(entry_id)

        gw_points = {h["event"]: h["points"] for h in history["current"]}

        players.append({
            "entry_id": entry_id,
            "team_name": team_name,
            "player_name": player_name,
            "points_per_gw": gw_points,
            "chips": history.get("chips", []),
            "overall_points": team_info["summary_overall_points"]
        })

    snapshot = {
        "league": {
            "id": LEAGUE_ID,
            "name": league["league"]["name"],
            "updated": datetime.utcnow().isoformat() + "Z"
        },
        "players": players
    }

    # Ensure /data exists
    os.makedirs("data", exist_ok=True)

    # Save snapshot as latest.json
    with open("data/latest.json", "w") as f:
        json.dump(snapshot, f, indent=2)


if __name__ == "__main__":
    collect_data()
