import requests
import json
import os
from datetime import datetime

# CONFIG
LEAGUE_ID = 98345  # 🔁 Replace with your actual mini-league ID
BASE_URL = "https://fantasy.premierleague.com/api"
DATA_DIR = "data"

def get_json(url):
    res = requests.get(url)
    res.raise_for_status()
    return res.json()

def fetch_bootstrap():
    data = get_json(f"{BASE_URL}/bootstrap-static/")
    print("Fetched events data:", data["events"])  # Add this line for debugging
    return data

def fetch_league_standings(league_id):
    return get_json(f"{BASE_URL}/leagues-classic/{league_id}/standings/")

def fetch_entry_history(entry_id):
    return get_json(f"{BASE_URL}/entry/{entry_id}/history/")

def fetch_entry_picks(entry_id, event_id):
    return get_json(f"{BASE_URL}/entry/{entry_id}/event/{event_id}/picks/")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    filename = os.path.join(DATA_DIR, f"snapshot_{timestamp}.json")

    # Load all base data
    bootstrap = fetch_bootstrap()
    elements = {p["id"]: p for p in bootstrap["elements"]}
    events = bootstrap["events"]
    element_types = {e["id"]: e["singular_name_short"] for e in bootstrap["element_types"]}

    # Get the latest gameweek (live data)
    gameweek = max(events, key=lambda x: x["id"])["id"]
    data_snapshot = {
        "timestamp": timestamp,
        "players": [],
        "gameweek": gameweek,
        "most_captained": {},
        "chips_used": {},
        "differentials": [],
    }

    captain_counter = {}
    chips_counter = {}
    total_gw_points = {}

    league = fetch_league_standings(LEAGUE_ID)
    standings = league["standings"]["results"]

    # Loop through each player in the standings
    for player in standings:
        entry_id = player["entry"]
        player_name = player["entry_name"]

        history = fetch_entry_history(entry_id)
        current = history["current"]
        picks = []

        # Per-gameweek points
        gw_points = {gw["event"]: gw["points"] for gw in current}
        total_gw_points[player_name] = gw_points

        # Picks and chips
        for gw in current:
            picks_data = fetch_entry_picks(entry_id, gw["event"])
            captain = picks_data["picks"][0]["element"]
            for p in picks_data["picks"]:
                if p["is_captain"]:
                    captain = p["element"]
            chip_used = picks_data.get("chip")

            # Count captain
            captain_name = elements[captain]["web_name"]
            captain_counter.setdefault(gw["event"], {})
            captain_counter[gw["event"]].setdefault(captain_name, 0)
            captain_counter[gw["event"]][captain_name] += 1

            # Count chip
            if chip_used:
                chips_counter.setdefault(chip_used, 0)
                chips_counter[chip_used] += 1

        data_snapshot["players"].append({
            "player_name": player_name,
            "entry_id": entry_id,
            "points_per_gw": gw_points,
        })

    # Process captains
    overall_captains = {}
    for gw, captains in captain_counter.items():
        most_captain = max(captains.items(), key=lambda x: x[1])
        data_snapshot["most_captained"][f"GW{gw}"] = most_captain
        for name, count in captains.items():
            overall_captains[name] = overall_captains.get(name, 0) + count
    data_snapshot["most_captained"]["overall"] = max(overall_captains.items(), key=lambda x: x[1])

    # Chips used
    data_snapshot["chips_used"] = chips_counter

    # Save data to JSON file
    with open(filename, "w") as f:
        json.dump(data_snapshot, f, indent=2)

    # NEW: also write/update a stable pointer
    with open(os.path.join(DATA_DIR, "latest.json"), "w") as f:
        json.dump(data_snapshot, f, indent=2)

    # after building overall_captains dict
    data_snapshot["captain_tally"] = overall_captains  # {player_web_name: count}

    print(f"Snapshot saved to {filename} and data/latest.json updated")

if __name__ == "__main__":
    main()

    # Also save as "latest.json" for the dashboard
    latest_file = os.path.join(DATA_DIR, "latest.json")
    with open(latest_file, "w") as f:
    json.dump(data_snapshot, f, indent=2)

print(f"Latest snapshot saved to {latest_file}")

