import requests
import streamlit as st

# Streamlit UI Start 
st.set_page_config("🏏 Cricbuzz ", layout="wide")
# st.title("🏏 Cricbuzz Live Match Dashboard")
st.title("⚽ Live Matches")
st.write("Display current live matches here.")

# Cricbuzz API Endpoint
url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"

def fetch_live_matches():
    headers = {
	        "x-rapidapi-key": "9afe0e8d2amshd0215ac6934208fp1c8874jsnf0e2ee8a8a43",
	        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
        }

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        st.error(f"API Error {resp.status_code}: {resp.text}")
        return None
    return resp.json()

# Fetch Data
data = fetch_live_matches()
if not data or "typeMatches" not in data:
    st.warning("⚡ No live matches found")
    st.stop()

# Prepare match list
matches_list = []
labels = []

for type_match in data["typeMatches"]:
    for series in type_match.get("seriesMatches", []):
        matches = series.get("seriesAdWrapper", {}).get("matches", [])
        for match in matches:
            info = match.get("matchInfo", {})
            team1 = info.get("team1", {}).get("teamName", "Team 1")
            team2 = info.get("team2", {}).get("teamName", "Team 2")
            venue = info.get("venueInfo", {}).get("ground", "")
            city = info.get("venueInfo", {}).get("city", "")
            status = info.get("status", "")
            label = f"{team1} vs {team2} @ {venue}, {city} - {status}"
            labels.append(label)
            matches_list.append(match)

if not matches_list:
    st.warning("⚡ No live matches found")
    st.stop()

# Match Dropdown
selected_index = st.selectbox("🎯 Select a Match",range(len(labels)),format_func=lambda i: labels[i])

# Helper function to extract score
def get_score(team_score):
    if not team_score or "inngs1" not in team_score:
        return "-", "-", "-"
    inn = team_score.get("inngs1", {})
    return inn.get("runs", "-"), inn.get("wickets", "-"), inn.get("overs", "-")

# Display selected match
def display_match(match):
    info = match.get("matchInfo", {})
    score = match.get("matchScore", {})

    team1 = info.get("team1", {}).get("teamName", "Team 1")
    team2 = info.get("team2", {}).get("teamName", "Team 2")
    short1 = info.get("team1", {}).get("teamSName", "")
    short2 = info.get("team2", {}).get("teamSName", "")

    venue = info.get("venueInfo", {}).get("ground", "")
    city = info.get("venueInfo", {}).get("city", "")
    series_name = info.get("seriesName", "")
    match_format = info.get("matchFormat", "")
    desc = info.get("matchDesc", "")
    status = info.get("status", "")
    state = info.get("stateTitle", "")

    t1_runs, t1_wkts, t1_overs = get_score(score.get("team1Score"))
    t2_runs, t2_wkts, t2_overs = get_score(score.get("team2Score"))

    # Display match info
    st.markdown(f"### 🏏 {team1} vs {team2}")
    st.write(f"**Match:** {desc}")
    st.write(f"**Format:** {match_format}")
    st.write(f"**Venue:** {venue}, {city}")
    st.write(f"**Series:** {series_name}")
    st.write(f"**Status:** {status}")
    st.write(f"**State:** {state}")

    st.markdown("---")
    st.subheader("📊 Current Score")
    col1, col2 = st.columns(2)
    col1.metric(label=f"{team1} ({short1})", value=f"{t1_runs}/{t1_wkts}", delta=f"Overs: {t1_overs}")
    col2.metric(label=f"{team2} ({short2})", value=f"{t2_runs}/{t2_wkts}", delta=f"Overs: {t2_overs}")

# Show selected match
display_match(matches_list[selected_index])
