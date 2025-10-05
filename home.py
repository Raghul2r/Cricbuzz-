import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠")

st.markdown("## 🏠 Welcome to Cricbuzz LiveStats")
st.write("Stay updated with live cricket matches, top player stats, and database-driven insights — all in one dashboard.")

st.markdown("### 🏏 Features Available:")
st.success("✔️ Live Match Scores with Real-Time Updates")
st.success("✔️ View Top Performing Players & Teams")
st.success("✔️ Run SQL Queries on Cricket Data")
st.success("✔️ Manage Player Data (Create, Read, Update, Delete)")

st.markdown("---")
st.markdown("### 📢 Latest Cricket News")

news = [
    "Virat Kohli becomes fastest to 13,000 ODI runs!",
    "India qualifies for the ICC World Cup Finals 2025.",
    "Australia announces squad for India tour next month.",
    "Babar Azam returns as captain ahead of Asia Cup.",
]

for item in news:
    st.info(f"📰 {item}")
