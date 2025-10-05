import sys
import os

# Add parent directory to sys.path so imports from 'utils' work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from utils.db_connection import get_connection

def create_teams_table(cursor):
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='teams' AND xtype='U')
    BEGIN
        CREATE TABLE teams (
            team_id INT PRIMARY KEY,
            team_name VARCHAR(100),
            team_short_name VARCHAR(10),
            image_id INT,
            country_name VARCHAR(100)
        )
    END
    """)

def insert_team(cursor, team):
    team_id = team.get("teamId") or team.get("id")
    if not team_id:  # Skip headers
        return False

    team_name = team.get("teamName")
    team_short_name = team.get("teamSName") or team.get("teamShortName")
    image_id = team.get("imageId")
    country_name = team.get("countryName")

    # Insert only if team_id is valid and not exists
    cursor.execute("SELECT 1 FROM teams WHERE team_id = ?", (team_id,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO teams (team_id, team_name, team_short_name, image_id, country_name)
            VALUES (?, ?, ?, ?, ?)
        """, (team_id, team_name, team_short_name, image_id, country_name))
        return True
    return False

def main():
    conn = get_connection()
    cursor = conn.cursor()
    print("Connected to DB")

    create_teams_table(cursor)
    conn.commit()
    print("Table 'teams' ensured")

    url = "https://cricbuzz-cricket.p.rapidapi.com/teams/v1/international"
    headers = {
        "x-rapidapi-key": "8c0c35c792mshed9335af88e88e1p1bef45jsna3f0d411dece",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    count = 0
    for team in data.get("list", []):  
        if insert_team(cursor, team):
            count += 1

    conn.commit()
    conn.close()
    print(f"Done! Inserted {count} teams.")

if __name__ == "__main__":
    main()
