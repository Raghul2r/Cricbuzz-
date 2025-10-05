import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd  
from utils.player_db import PlayerStatsDB

                            #Streamlit UI 

st.set_page_config("Cricbuzz", layout="wide")
st.title("📝 CRUD Operations")
st.write("Perform Create, Read, Update, Delete operations.")

tabs = st.tabs(["🏆 Leaderboard", "👨‍💻 Manage Players"])

                            #Tab 1: Leaderboard

with tabs[0]:
    st.subheader("🏆 Top Run Scorers")
    db = PlayerStatsDB()
    players = db.fetch_all()

    if not players:
        st.info("No players found.")
    else:
        players_sorted = sorted(players, key=lambda x: x['runs'], reverse=True)

        table_headers = ["Sl. No", "Player Name", "Matches", "Innings", "Runs", "Average"]
        table_rows = [
            [i + 1, p["player_name"], p["matches"], p["innings"], p["runs"], p["average"]]
            for i, p in enumerate(players_sorted)
        ]

        df = pd.DataFrame(table_rows, columns=table_headers)
        st.dataframe(df, hide_index=True)
        
        top = players_sorted[0]
        st.success(f"🥇 {top['player_name']} is leading with {top['runs']} runs!")

    db.close()

                                #Tab 2: CRUD 

with tabs[1]:
    operation = st.radio("Select Operation", ["Create", "Read", "Update", "Delete"])
    db = PlayerStatsDB()

                                     #Create
    if operation == "Create":
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Name")
            matches = st.number_input("Matches", min_value=0)
            innings = st.number_input("Innings", min_value=0)
            runs = st.number_input("Runs", min_value=0, step=50)
            average = st.number_input("Average", min_value=0.0, step=0.1, format="%.2f")
            submit = st.form_submit_button("Add Player")
            if submit and name:
                new_id = db.get_next_id()
                db.add_player(new_id, name, matches, innings, runs, average)
                st.success(f"Player '{name}' added.")

                                    #Read
    elif operation == "Read":
        st.write("### All Players")
        players = db.fetch_all()

        if not players:
            st.info("No players found.")
        else:
            table_headers = ["Sl. No", "Player Name", "Matches", "Innings", "Runs", "Average"]
            table_rows = [
                [i + 1, p["player_name"], p["matches"], p["innings"], p["runs"], p["average"]]
                for i, p in enumerate(players)
            ]

            df = pd.DataFrame(table_rows, columns=table_headers)
            st.dataframe(df, hide_index=True)

                                   #Update
    elif operation == "Update":
        players = db.fetch_all()
        if not players:
            st.warning("No players to update.")
        else:
            player_options = {f"{p['player_id']} - {p['player_name']}": p for p in players}
            selected = st.selectbox("Select Player", list(player_options.keys()))
            player = player_options[selected]

            with st.form("update_form"):
                name = st.text_input("Name", value=player['player_name'])
                matches = st.number_input("Matches", value=player['matches'])
                innings = st.number_input("Innings", value=player['innings'])
                runs = st.number_input("Runs", value=player['runs'])
                average = st.number_input("Average", value=player['average'], format="%.2f")
                submit = st.form_submit_button("Update Player")
                if submit:
                    db.update_player(player['player_id'], name, matches, innings, runs, average)
                    st.success("Player updated.")

                                    #Delete
    elif operation == "Delete":
        players = db.fetch_all()
        if not players:
            st.warning("No players to delete.")
        else:
            player_options = {f"{p['player_id']} - {p['player_name']}": p for p in players}
            selected = st.selectbox("Select Player to Delete", list(player_options.keys()))
            player = player_options[selected]
            if st.button("Delete"):
                db.delete_player(player['player_id'])
                st.warning(f"Player '{player['player_name']}' deleted.")

    db.close()
