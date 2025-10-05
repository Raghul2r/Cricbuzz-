import streamlit as st
import pandas as pd
from utils.db_connection import get_connection

def run_query(query: str):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="🏏 Cricket SQL Analytics", layout="wide")
st.title("🛠️ SQL Queries")
st.write("Execute and view SQL queries.")

questions_list = [
    "1. Find all players who represent India. Display their full name, playing role, batting style, and bowling style.",
    "2. Show all cricket matches that were played in the last few days. Include the match description, both team names, venue name with city, and the match date. Sort by most recent matches first.",
    "3. List the top 10 highest run scorers in ODI cricket. Show player name, total runs scored, batting average, and number of centuries. Display the highest run scorer first.",
    "4. Display all cricket venues that have a seating capacity of more than 30,000 spectators. Show venue name, city, country, and capacity. Order by largest capacity first.",
    "5. Calculate how many matches each team has won. Show team name and total number of wins. Display teams with the most wins first.",
    "6. Count how many players belong to each playing role (like Batsman, Bowler, All-rounder, Wicket-keeper). Show the role and count of players for each role.",
    "7. Find the highest individual batting score achieved in each cricket format (Test, ODI, T20I). Display the format and the highest score for that format.",
    "8. Show all cricket series that started in the year 2024. Include series name, host country, match type, start date, and total number of matches planned.",
    "9. Find all-rounder players who have scored more than 1000 runs AND taken more than 50 wickets in their career. Display player name, total runs, total wickets, and the cricket format.",
    "10. Get details of the last 20 completed matches. Show match description, both team names, winning team, victory margin, victory type (runs/wickets), and venue name. Display most recent matches first.",
    "11. Compare each player's performance across different cricket formats. For players who have played at least 2 different formats, show their total runs in Test cricket, ODI cricket, and T20I cricket, along with their overall batting average across all formats.",
    "12. Analyze each international team's performance when playing at home versus playing away. Determine whether each team played at home or away based on whether the venue country matches the team's country. Count wins for each team in both home and away conditions.",
    "13. Identify batting partnerships where two consecutive batsmen (batting positions next to each other) scored a combined total of 100 or more runs in the same innings. Show both player names, their combined partnership runs, and which innings it occurred in.",
    "14. Examine bowling performance at different venues. For bowlers who have played at least 3 matches at the same venue, calculate their average economy rate, total wickets taken, and number of matches played at each venue. Focus on bowlers who bowled at least 4 overs in each match.",
    "15. Identify players who perform exceptionally well in close matches. A close match is defined as one decided by less than 50 runs OR less than 5 wickets. For these close matches, calculate each player's average runs scored, total close matches played, and how many of those close matches their team won when they batted.",
    "16. Track how players' batting performance changes over different years. For matches since 2020, show each player's average runs per match and average strike rate for each year. Only include players who played at least 5 matches in that year.",
    "17. Investigate whether winning the toss gives teams an advantage in winning matches. Calculate what percentage of matches are won by the team that wins the toss, broken down by their toss decision (choosing to bat first or bowl first).",
    "18. Find the most economical bowlers in limited-overs cricket (ODI and T20 formats). Calculate each bowler's overall economy rate and total wickets taken. Only consider bowlers who have bowled in at least 10 matches and bowled at least 2 overs per match on average.",
    "19. Determine which batsmen are most consistent in their scoring. Calculate the average runs scored and the standard deviation of runs for each player. Only include players who have faced at least 10 balls per innings and played since 2022. A lower standard deviation indicates more consistent performance.",
    "20. Analyze how many matches each player has played in different cricket formats and their batting average in each format. Show the count of Test matches, ODI matches, and T20 matches for each player, along with their respective batting averages. Only include players who have played at least 20 total matches across all formats.",
    "21. Create a comprehensive performance ranking system for players. Combine their batting performance (runs scored, batting average, strike rate), bowling performance (wickets taken, bowling average, economy rate), and fielding performance (catches, stumpings) into a single weighted score. Rank the top performers in each cricket format.",
    "22. Build a head-to-head match prediction analysis between teams. For each pair of teams that have played at least 5 matches against each other in the last 3 years, calculate total matches played, wins for each team, average victory margin when each team wins, performance when batting first vs bowling first at different venues, and overall win percentage for each team in this head-to-head record.",
    "23. Analyze recent player form and momentum. For each player's last 10 batting performances, calculate average runs in their last 5 matches vs their last 10 matches, recent strike rate trends, number of scores above 50 in recent matches, and a consistency score based on standard deviation. Categorize players as 'Excellent Form', 'Good Form', 'Average Form', or 'Poor Form'.",
    "24. Study successful batting partnerships to identify the best player combinations. For pairs of players who have batted together as consecutive batsmen (positions differ by 1) in at least 5 partnerships, calculate their average partnership runs, count how many of their partnerships exceeded 50 runs, find their highest partnership score, calculate their success rate, and rank the most successful batting partnerships.",
    "25. Perform a time-series analysis of player performance evolution. Track how each player's batting performance changes over time by calculating quarterly averages for runs and strike rate, comparing each quarter's performance to the previous quarter, identifying whether performance is improving, declining, or stable, and determining overall career trajectory. Only analyze players with data spanning at least 6 quarters and a minimum of 3 matches per quarter."
]

selected_question = st.selectbox("Select a question:", questions_list)

def get_query(question: str) -> str:
    if question.startswith("1."):
        return "SELECT player_name, batting_style, bowling_style  FROM players"
    elif question.startswith("2."):
        return "SELECT match_desc, team1_name, team2_name, venue_name, city FROM recent_matches ORDER BY start_date DESC"
    elif question.startswith("3."): 
        return "SELECT TOP 10 player_name, runs AS total_runs, average AS batting_average, matches AS total_matches FROM top_scorers WHERE match_type = 'odi' ORDER BY runs DESC;"
    elif question.startswith("4."):
        return "SELECT ground, city, country, capacity FROM venues WHERE capacity > 10000 ORDER BY capacity DESC"
    elif question.startswith("5."):
        return ""
    elif question.startswith("6."):
        return ""
    elif question.startswith("7."):
        return "SELECT match_type, player_name,MAX(runs) AS highest_score FROM top_scorers GROUP BY match_type, player_name"
    elif question.startswith("8."):
        return ""
    elif question.startswith("9."):
        return ""
    elif question.startswith("10."):
        return "SELECT TOP 20 match_description, team1_name, team2_name, winning_team, victory_margin, victory_type, venue_name, city, result_status, start_date FROM recent_matches WHERE result_status LIKE '%won by%' ORDER BY start_date DESC"
    elif question.startswith("11."):
        return "SELECT player_name, SUM(CASE WHEN match_type='test' THEN runs ELSE 0 END) AS test_runs, SUM(CASE WHEN match_type='odi' THEN runs ELSE 0 END) AS odi_runs, SUM(CASE WHEN match_type='t20' THEN runs ELSE 0 END) AS t20i_runs, AVG(average) AS overall_average FROM top_scorers GROUP BY player_name HAVING COUNT(DISTINCT match_type) >= 2"
    elif question.startswith("12."):
        return ""
    elif question.startswith("13."):
        return ""
    elif question.startswith("14."):
        return ""
    elif question.startswith("15."):
        return ""
    elif question.startswith("16."):
        return ""
    elif question.startswith("17."):
        return ""
    elif question.startswith("18."):
        return ""
    elif question.startswith("19."):
        return ""
    elif question.startswith("20."):
        return ""
    elif question.startswith("21."):
        return ""
    elif question.startswith("22."):
        return ""
    elif question.startswith("23."):
        return ""
    elif question.startswith("24."):
        return ""
    elif question.startswith("25."):
        return ""
    else:
        return ""

if st.button("🚀 Execute Query"):
    query = get_query(selected_question)
    if not query:
        st.warning("⚠️ SQL query not defined for this question.")
    else:
        with st.spinner("Running query..."):
            results = run_query(query)
        if results.empty:
            st.warning("⚠️ No data found for this query.")
        else:
            st.success(f"✅ Query executed successfully! Found {len(results)} records.")
            results.insert(0, "Sl. No", range(1, len(results)+1))
            st.dataframe(results, hide_index=True, use_container_width=True)

