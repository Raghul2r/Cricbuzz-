import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
# Add parent directory to sys.path so imports from 'utils' work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from utils.db_connection import get_connection

def create_team_matches_table(cursor):
    """Create the team_matches table if it doesn't already exist."""
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='team_matches' AND xtype='U')
    BEGIN
        CREATE TABLE team_matches (
            match_id BIGINT PRIMARY KEY,
            series_id BIGINT,
            series_name NVARCHAR(255),
            match_desc NVARCHAR(255),
            match_format NVARCHAR(50),
            start_date BIGINT,
            end_date BIGINT,
            state NVARCHAR(50),
            status NVARCHAR(255),
            team1_id INT,
            team1_name NVARCHAR(100),
            team1_sname NVARCHAR(50),
            team1_image INT,
            team2_id INT,
            team2_name NVARCHAR(100),
            team2_sname NVARCHAR(50),
            team2_image INT,
            venue_id INT,
            venue_ground NVARCHAR(255),
            venue_city NVARCHAR(100),
            venue_timezone NVARCHAR(10),
            series_start_dt BIGINT,
            series_end_dt BIGINT,
            is_time_announced BIT,
            team1_inngs1_runs INT,
            team1_inngs1_wickets INT,
            team1_inngs1_overs FLOAT,
            team1_inngs2_runs INT NULL,
            team1_inngs2_wickets INT NULL,
            team1_inngs2_overs FLOAT NULL,
            team2_inngs1_runs INT,
            team2_inngs1_wickets INT,
            team2_inngs1_overs FLOAT,
            team2_inngs2_runs INT NULL,
            team2_inngs2_wickets INT NULL,
            team2_inngs2_overs FLOAT NULL
        )
    END
    """)


def safe_int(value):
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def safe_float(value):
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def extract_innings(score_dict, key):
    """Extract innings stats safely."""
    inn = score_dict.get(key, {}) if isinstance(score_dict, dict) else {}
    return (
        safe_int(inn.get("runs")),
        safe_int(inn.get("wickets")),
        safe_float(inn.get("overs"))
    )


def insert_match(cursor, match):
    """Insert a single match into the database."""
    info = match.get("matchInfo", {})
    score = match.get("matchScore", {})

    t1_score1 = extract_innings(score.get("team1Score", {}), "inngs1")
    t1_score2 = extract_innings(score.get("team1Score", {}), "inngs2")
    t2_score1 = extract_innings(score.get("team2Score", {}), "inngs1")
    t2_score2 = extract_innings(score.get("team2Score", {}), "inngs2")

    values = (
        safe_int(info.get("matchId")),
        safe_int(info.get("seriesId")),
        str(info.get("seriesName") or ""),
        str(info.get("matchDesc") or ""),
        str(info.get("matchFormat") or ""),
        safe_int(info.get("startDate")),
        safe_int(info.get("endDate")),
        str(info.get("state") or ""),
        str(info.get("status") or ""),
        safe_int(info.get("team1", {}).get("teamId")),
        str(info.get("team1", {}).get("teamName") or ""),
        str(info.get("team1", {}).get("teamSName") or ""),
        safe_int(info.get("team1", {}).get("imageId")),
        safe_int(info.get("team2", {}).get("teamId")),
        str(info.get("team2", {}).get("teamName") or ""),
        str(info.get("team2", {}).get("teamSName") or ""),
        safe_int(info.get("team2", {}).get("imageId")),
        safe_int(info.get("venueInfo", {}).get("id")),
        str(info.get("venueInfo", {}).get("ground") or ""),
        str(info.get("venueInfo", {}).get("city") or ""),
        str(info.get("venueInfo", {}).get("timezone") or ""),
        safe_int(info.get("seriesStartDt")),
        safe_int(info.get("seriesEndDt")),
        int(info.get("isTimeAnnounced") or 0),
        t1_score1[0], t1_score1[1], t1_score1[2],
        t1_score2[0], t1_score2[1], t1_score2[2],
        t2_score1[0], t2_score1[1], t2_score1[2],
        t2_score2[0], t2_score2[1], t2_score2[2]
    )

    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM team_matches WHERE match_id = ?)
        INSERT INTO team_matches (
            match_id, series_id, series_name, match_desc, match_format,
            start_date, end_date, state, status,
            team1_id, team1_name, team1_sname, team1_image,
            team2_id, team2_name, team2_sname, team2_image,
            venue_id, venue_ground, venue_city, venue_timezone,
            series_start_dt, series_end_dt, is_time_announced,
            team1_inngs1_runs, team1_inngs1_wickets, team1_inngs1_overs,
            team1_inngs2_runs, team1_inngs2_wickets, team1_inngs2_overs,
            team2_inngs1_runs, team2_inngs1_wickets, team2_inngs1_overs,
            team2_inngs2_runs, team2_inngs2_wickets, team2_inngs2_overs
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, values)


def main():
    conn = get_connection()
    cursor = conn.cursor()
    print("✅ Connected to Database")

    create_team_matches_table(cursor)
    conn.commit()
    print("✅ Table 'team_matches' ensured")

    # Fetch team IDs
    cursor.execute("SELECT team_id FROM teams")
    teams = [row[0] for row in cursor.fetchall()]
    print(f"📊 Found {len(teams)} teams")

    headers = {
        "x-rapidapi-key": "8c0c35c792mshed9335af88e88e1p1bef45jsna3f0d411dece",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    total_inserted = 0

    for team_id in teams:
        print(f"➡️ Fetching matches for team_id={team_id}...")
        url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/results"

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"⚠️ Error fetching team {team_id}: {e}")
            continue

        team_matches = data.get("teamMatchesData", [])
        if not team_matches:
            print(f"ℹ️ No matches found for team {team_id}")
            continue

        for item in team_matches:
            match_map = item.get("matchDetailsMap", {})
            for match in match_map.get("match", []):
                try:
                    insert_match(cursor, match)
                    total_inserted += 1
                except Exception as e:
                    print(f"❌ Skipped match (error): {e}")
                    continue

        conn.commit()

    conn.close()
    print(f"🏁 Done! Inserted or updated {total_inserted} matches in 'team_matches' table.")


if __name__ == "__main__":
    main()
