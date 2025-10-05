import sys
import os

# Add parent directory to sys.path so imports from 'utils' work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from utils.db_connection import get_connection

def create_table_if_not_exists(cursor):
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='venues' AND xtype='U')
    BEGIN
        CREATE TABLE venues (
            venue_id INT PRIMARY KEY,
            ground VARCHAR(100),
            city VARCHAR(100),
            country VARCHAR(100),
            capacity INT
        )
    END
    """)

def insert_venue_if_not_exists(cursor, venue_id, ground, city, country, capacity):
    cursor.execute("SELECT 1 FROM venues WHERE venue_id = ?", (venue_id,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO venues (venue_id, ground, city, country, capacity)
            VALUES (?, ?, ?, ?, ?)
        """, (venue_id, ground, city, country, capacity))

def fetch_and_store_venues(series_id):
    conn = get_connection()
    cursor = conn.cursor()
    print("Connected to DB")

    # Ensure table exists
    create_table_if_not_exists(cursor)
    conn.commit()
    print("Table 'venues' ensured")

    # Hardcoded RapidAPI headers
    headers = {
        "x-rapidapi-key": "b6482b00f5mshca37964edbdfda0p17a017jsnf608d41ea2c1",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    # Step 1: Get all venues for the series
    series_url = f"https://cricbuzz-cricket.p.rapidapi.com/series/v1/{series_id}/venues"
    response = requests.get(series_url, headers=headers)
    series_data = response.json()

    venues = series_data.get("seriesVenue", [])
    if not venues:
        print("No venues found for this series!")
        conn.close()
        return
    
    count = 0

    # Step 2: Loop through all venues and get full details
    for v in venues:
        venue_id = v["id"]
        detail_url = f"https://cricbuzz-cricket.p.rapidapi.com/venues/v1/{venue_id}"
        detail_response = requests.get(detail_url, headers=headers)
        detail_data = detail_response.json()

        try:
            ground = detail_data.get("ground", "")
            city = detail_data.get("city", "")
            country = detail_data.get("country", "")
            cap_raw = detail_data.get("capacity", "0").replace(",", "").strip()
            capacity = int(cap_raw) if cap_raw.isdigit() else 0

            insert_venue_if_not_exists(cursor, venue_id, ground, city, country, capacity)
            count += 1

        except Exception as e:
            print(f"Error inserting venue {venue_id}: {e}")

    conn.commit()
    print(f"Done! Inserted {count} venues.")
    conn.close()

if __name__ == "__main__":
    # Example: Plunket Shield series_id = 3718
    fetch_and_store_venues(series_id=3718)
