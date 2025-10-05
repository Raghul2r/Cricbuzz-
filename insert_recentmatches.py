import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import datetime
import requests
from collections import defaultdict
from utils.db_connection import get_connection

def create_recent_matches_table(cursor):
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='recent_matches' AND xtype='U')
    BEGIN
        CREATE TABLE recent_matches (
            match_id INT PRIMARY KEY,
            match_description VARCHAR(255),
            series_id INT,
            series_name VARCHAR(255),
            match_desc VARCHAR(255),
            match_format VARCHAR(50),
            start_date DATETIME NULL,
            team1_name VARCHAR(100),
            team2_name VARCHAR(100),
            winning_team VARCHAR(100),
            victory_margin VARCHAR(50),
            victory_type VARCHAR(50),
            venue_name VARCHAR(255),
            city VARCHAR(100),
            result_status VARCHAR(255)
        )
    END
    """)

def insert_match(cursor, match):
    try:
        match_info = match["matchInfo"]

        match_id = int(match_info.get("matchId", 0))
        series_id = int(match_info.get("seriesId", 0))
        series_name = match_info.get("seriesName", "")
        match_desc = match_info.get("matchDesc", "")
        match_format = match_info.get("matchFormat", "")

        start_ts = match_info.get("startDate")
        start_date = datetime.datetime.fromtimestamp(int(start_ts) / 1000) if start_ts else None

        team1_name = match_info.get("team1", {}).get("teamName", "")
        team2_name = match_info.get("team2", {}).get("teamName", "")

        venue = match_info.get("venueInfo", {})
        venue_name = venue.get("ground", "")
        city = venue.get("city", "")

        result_status = match_info.get("status", "")
        winning_team = ""
        victory_margin = ""
        victory_type = ""

        if "won" in result_status.lower():
            parts = result_status.split(" won by ")
            if len(parts) == 2:
                winning_team = parts[0].strip()
                margin_parts = parts[1].split(" ")
                if len(margin_parts) >= 2:
                    victory_margin = margin_parts[0]
                    victory_type = margin_parts[1]

        # Check if already inserted
        cursor.execute("SELECT 1 FROM recent_matches WHERE match_id = ?", (match_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO recent_matches (
                    match_id, match_description, series_id, series_name, match_desc, match_format,
                    start_date, team1_name, team2_name, winning_team, victory_margin, victory_type,
                    venue_name, city, result_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id, match_desc, series_id, series_name, match_desc, match_format,
                start_date, team1_name, team2_name, winning_team, victory_margin, victory_type,
                venue_name, city, result_status
            ))
    except Exception as e:
        print(f"Error inserting match {match.get('matchInfo', {}).get('matchId', 'unknown')}: {e}")

def main():
    conn = get_connection()
    cursor = conn.cursor()
    print("Connected to DB")

    create_recent_matches_table(cursor)
    conn.commit()
    print("Table 'recent_matches' ensured")

    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    headers = {
        "x-rapidapi-key": "b6482b00f5mshca37964edbdfda0p17a017jsnf608d41ea2c1",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    count = 0

    for type_match in data.get("typeMatches", []):
        for series in type_match.get("seriesMatches", []):
            series_wrapper = series.get("seriesAdWrapper", {})
            for match in series_wrapper.get("matches", []):
                insert_match(cursor, match)
                count += 1

    conn.commit()
    conn.close()
    print(f"Done! Inserted {count} matches into recent_matches table.")

if __name__ == "__main__":
    main()
