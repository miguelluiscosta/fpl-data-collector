import requests
import json

def fetch_league_data():
    league_id = 98345  # Replace with your actual league ID, e.g. 123456
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # Save to a JSON file locally (for example)
        with open("league_data.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Data fetched and saved.")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_league_data()
