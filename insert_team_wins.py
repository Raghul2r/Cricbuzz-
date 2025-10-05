import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from collections import defaultdict
from utils.db_connection import get_connection

def create_table_if_not_exists(cursor):
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='team_wins' AND xtype='U')
    BEGIN
        CREATE TABLE team_wins (
            team_name VARCHAR(100) PRIMARY KEY,
            total_wins INT
        )
    END
    """)

def insert_or_update_team(cursor, team_name, wins):
    cursor.execute("SELECT total_wins FROM team_wins WHERE team_name = ?", (team_name,))
    row = cursor.fetchone()
    if row:
        total = row[0] + wins
        cursor.execute("UPDATE team_wins SET total_wins = ? WHERE team_name = ?", (total, team_name))
    else:
        cursor.execute("INSERT INTO team_wins (team_name, total_wins) VALUES (?, ?)", (team_name, wins))

def fetch_and_store_wins(match_ids):
    conn = get_connection()
    cursor = conn.cursor()
    print("Connected to DB")

    create_table_if_not_exists(cursor)
    conn.commit()
    print("Table 'team_wins' ensured")

    headers = {
        "x-rapidapi-key": "b6482b00f5mshca37964edbdfda0p17a017jsnf608d41ea2c1",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    team_win_counter = defaultdict(int)

    for match_id in match_ids:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/overs"
        response = requests.get(url, headers=headers)
        data = response.json()

        # Extract winning team
        winning_team_name = None

        # Try using custstatus first
        cust_status = data.get("miniscore", {}).get("custstatus")
        if cust_status and "won" in cust_status:
            winning_team_name = cust_status.split(" won")[0].strip()
        else:
            # fallback: winningteamid -> matchheaders -> teamdetails
            winning_team_id = data.get("matchheaders", {}).get("winningteamid")
            teamdetails = data.get("matchheaders", {}).get("teamdetails", {})
            if winning_team_id and teamdetails:
                winning_team_name = teamdetails.get("batteamname") or teamdetails.get("bowlteamname")

        if winning_team_name:
            team_win_counter[winning_team_name] += 1

    # Insert/update DB
    for team, wins in team_win_counter.items():
        insert_or_update_team(cursor, team, wins)

    conn.commit()
    print("Done! Team wins stored:")
    for team, wins in sorted(team_win_counter.items(), key=lambda x: x[1], reverse=True):
        print(f"{team}: {wins} wins")

    conn.close()

if __name__ == "__main__":
    # Example: list of match IDs
    match_ids = [41881]  
    fetch_and_store_wins(match_ids)
