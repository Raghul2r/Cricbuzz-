import streamlit as st
import requests

headers = {
	"x-rapidapi-key": "9afe0e8d2amshd0215ac6934208fp1c8874jsnf0e2ee8a8a43",
	"x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

def search_players(name):
    url = "https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search"
    params = {"plrN": name}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json().get("player", [])
    else:
        st.error(f"❌ Failed to search players. Status code: {response.status_code}")
        return []

def fetch_player_by_id(player_id):
    if not player_id:
        return None
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"❌ Failed to fetch player data. Status code: {response.status_code}")
        return None

def format_teams(team_str):
    if team_str:
        return "\n".join(f"- {team}" for team in team_str.split(", "))
    return "No teams available."

def render_recent_table(title, section_data):
    st.subheader(title)
    if section_data and "rows" in section_data:
        st.table([
            dict(zip(section_data['headers'], row['values']))
            for row in section_data['rows']
        ])
    else:
        st.write("No data available.")

#code starts here
st.set_page_config(page_title="🏏 Player Search & Stats", layout="wide")
st.title("📊 Top Stats")
st.write("Display top stats here.")

# Initialize session state
if "selected_player_id" not in st.session_state:
    st.session_state.selected_player_id = None

if "players" not in st.session_state:
    st.session_state.players = []

#starting point
search_name = st.text_input("🔍 Enter player name to search")
search_btn = st.button("Search")

if search_btn and search_name.strip():
    st.session_state.selected_player_id = None  
    players = search_players(search_name.strip())
    st.session_state.players = players  

    if players:
        st.subheader("🎯 Search Results")

        player_options = [
            f"{p.get('name')} | Team: {p.get('teamName', 'N/A')} | DOB: {p.get('dob', 'N/A')}"
            for p in players
        ]

        selected_player_option = st.selectbox("Select a player from the list", player_options)

        selected_index = player_options.index(selected_player_option)
        selected_player_id = players[selected_index].get("id")
        st.session_state.selected_player_id = selected_player_id

elif st.session_state.players:

    st.subheader("🎯 Search Results")
    player_options = [
        f"{p.get('name')} | Team: {p.get('teamName', 'N/A')} | DOB: {p.get('dob', 'N/A')}"
        for p in st.session_state.players
    ]
    selected_player_option = st.selectbox("Select a player from the list", player_options)
    selected_index = player_options.index(selected_player_option)
    selected_player_id = st.session_state.players[selected_index].get("id")
    st.session_state.selected_player_id = selected_player_id

if st.session_state.selected_player_id:
    player = fetch_player_by_id(st.session_state.selected_player_id)

    if player:
        st.markdown("---")
        st.header(f"📋 Player Profile: {player.get('name')}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📇 Basic Info")
            # if player.get("image"):
            #     st.image(player.get("image"), width=150)
            st.write(f"**Name:** {player.get('name')}")
            st.write(f"**Nickname:** {player.get('nickName')}")
            st.write(f"**Role:** {player.get('role')}")
            st.write(f"**Batting Style:** {player.get('bat')}")
            st.write(f"**Bowling Style:** {player.get('bowl')}")
            st.write(f"**Height:** {player.get('height')}")

        with col2:
            st.subheader("🎂 Personal Info")
            st.write(f"**Date of Birth:** {player.get('DoB')}")
            st.write(f"**Birthplace:** {player.get('birthPlace')}")
            st.write(f"**International Team:** {player.get('intlTeam')}")

        with col3:
            st.subheader("🏆 Teams Played For")
            st.markdown(format_teams(player.get("teams", "")))

        # Rankings
        st.subheader("📊 ICC Rankings")
        bat_rank = player.get("rankings", {}).get("bat", {})
        if bat_rank:
            st.write(f"**Test Rank:** {bat_rank.get('testRank')} (Best: {bat_rank.get('testBestRank')})")
            st.write(f"**ODI Best Rank:** {bat_rank.get('odiBestRank')}")
            st.write(f"**T20 Best Rank:** {bat_rank.get('t20BestRank')}")
        else:
            st.write("No ranking data available.")

        # Recent Performance
        render_recent_table("🟢 Recent Batting Performance", player.get("recentBatting"))
        render_recent_table("🔵 Recent Bowling Performance", player.get("recentBowling"))

        # Biography
        st.subheader("📝 Biography")
        st.markdown(player.get("bio", "").replace("<br/>", "\n\n"), unsafe_allow_html=True)