import sys
import os

# Add parent directory to sys.path so imports from 'utils' work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from utils.db_connection import get_connection

def create_table_if_not_exists(cursor):
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='players' AND xtype='U')
    BEGIN
        CREATE TABLE players (
            player_id INT PRIMARY KEY,
            player_name VARCHAR(100),
            batting_style VARCHAR(50),
            bowling_style VARCHAR(50)
        )
    END
    """)

def insert_player_if_not_exists(cursor, player_id, name, batting, bowling):
    cursor.execute("SELECT 1 FROM players WHERE player_id = ?", (player_id,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO players (player_id, player_name, batting_style, bowling_style)
            VALUES (?, ?, ?, ?)
        """, (player_id, name, batting, bowling))

def main():
    conn = get_connection()
    cursor = conn.cursor()
    print("Connected to DB")

    # Ensure table exists
    create_table_if_not_exists(cursor)
    conn.commit()
    print("Table 'players' ensured")

    # Fetch data from Cricbuzz API
    url = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/2/players"
    headers = {
	"x-rapidapi-key": "b6482b00f5mshca37964edbdfda0p17a017jsnf608d41ea2c1",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}


    response = requests.get(url, headers=headers)
    data = response.json()

    players = data.get("player", [])
    count = 0

    for p in players:
        # Skip category headers like BATSMEN, ALL ROUNDER, etc.
        if "id" not in p:
            continue

        try:
            player_id = int(p["id"])
            name = p.get("name", "")
            batting = p.get("battingStyle", "")
            bowling = p.get("bowlingStyle", "")

            insert_player_if_not_exists(cursor, player_id, name, batting, bowling)
            count += 1
        except Exception as e:
            print(f"Error inserting {p.get('name')}: {e}")

    conn.commit()
    print(f"Done! Inserted {count} players.")

    conn.close()

if __name__ == "__main__":
    main()
