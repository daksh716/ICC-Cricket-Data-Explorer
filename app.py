import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(
    page_title="ICC Cricket Data Explorer",
    page_icon="🏏",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    font-size: 42px;
    font-weight: 700;
}

h2 {
    font-size: 28px;
    font-weight: 600;
}

h3 {
    font-size: 22px;
    font-weight: 600;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

[data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 700;
}

.stTextInput input {
    border-radius: 10px;
    padding: 12px;
}

.stButton button {
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
}
.hero {
    padding: 35px;
    border-radius: 18px;
    margin-bottom: 30px;
    text-align: center;
    background: linear-gradient(135deg, #0f172a, #1e3a8a);
}

.hero h1 {
    color: white;
    font-size: 42px;
    margin-bottom: 8px;
}

.hero p {
    color: #dbeafe;
    font-size: 18px;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🏏 ICC Cricket Data Explorer</h1>
    <p>Explore players, teams, tournaments and cricket statistics</p>
</div>
""", unsafe_allow_html=True)

odi_deliveries = pd.read_csv("data/raw/ball_by_ball_data.csv")
odi_matches = pd.read_csv("data/raw/match_info.csv")
t20_deliveries = pd.read_csv("data/raw/ball_by_ball_it20.csv")

st.success("Cricket datasets loaded successfully!")

col1, col2, col3 = st.columns(3)

col1.metric("ODI Matches", odi_matches["Match ID"].nunique())
col2.metric("ODI Deliveries", len(odi_deliveries))
col3.metric("T20I Matches", t20_deliveries["Match ID"].nunique())
st.subheader("📊 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("ODI Matches", odi_matches["Match ID"].nunique())
col2.metric("T20I Matches", t20_deliveries["Match ID"].nunique())
col3.metric("ODI Players", odi_deliveries["Batter"].nunique())
col4.metric("T20I Players", t20_deliveries["Batter"].nunique())

st.subheader("📈 Matches by Format")

format_data = pd.DataFrame({
    "Format": ["ODI", "T20I"],
    "Matches": [
        odi_matches["Match ID"].nunique(),
        t20_deliveries["Match ID"].nunique()
    ]
})

st.bar_chart(format_data.set_index("Format"))

st.sidebar.title("🏏 Cricket Explorer")

page = st.sidebar.radio(
    "Select Analysis",
    [
        "Overview",
        "Player Search",
        "Team Search",
        "Head-to-Head",
        "Tournament Search"
    ]
)
if page == "Player Search":
    st.header("🔎 Player Search")
player_name = st.text_input("Enter Player Name")

if player_name:

        odi_player = odi_deliveries[
            odi_deliveries["Batter"].str.contains(
                player_name, case=False, na=False
            )
        ]

        t20_player = t20_deliveries[
            t20_deliveries["Batter"].str.contains(
                player_name, case=False, na=False
            )
        ]

        if odi_player.empty and t20_player.empty:
            st.warning("Player not found.")

        if not odi_player.empty:

            player = odi_player["Batter"].value_counts().index[0]
            matches = odi_player["Match ID"].nunique()
            runs = odi_player["Runs by Batter"].sum()
            fours = (odi_player["Runs by Batter"] == 4).sum()
            sixes = (odi_player["Runs by Batter"] == 6).sum()

            highest_score = (
                odi_player.groupby("Match ID")["Runs by Batter"]
                .sum()
                .max()
            )

            st.subheader("ODI Player Profile")

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Player", player)
            col2.metric("Matches", matches)
            col3.metric("Runs", runs)
            col4.metric("Highest Score", highest_score)
            col5.metric("Fours", fours)
            balls = odi_player["Runs by Batter"].count()
            strike_rate = round((runs / balls) * 100, 2)

            st.metric("Strike Rate", strike_rate)            

            st.metric("Sixes", sixes)
            yearly_runs = (
                odi_player.merge(
                    odi_matches[["Match ID", "Season"]],
                    on="Match ID",
                    how="left"
                )
                .groupby("Season")["Runs by Batter"]
                .sum()
                .sort_index()
            )

            st.subheader("📈 ODI Year-wise Runs")

            st.line_chart(yearly_runs)            

        if not t20_player.empty:

            player = t20_player["Batter"].value_counts().index[0]
            matches = t20_player["Match ID"].nunique()
            runs = t20_player["Batter Runs"].sum()
            fours = (t20_player["Batter Runs"] == 4).sum()
            sixes = (t20_player["Batter Runs"] == 6).sum()

            highest_score = (
                t20_player.groupby("Match ID")["Batter Runs"]
                .sum()
                .max()
            )

            st.subheader("T20I Player Profile")

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Player", player)
            col2.metric("Matches", matches)
            col3.metric("Runs", runs)
            col4.metric("Highest Score", highest_score)
            col5.metric("Fours",fours)      
            balls = t20_player.groupby("Match ID")["Batter Balls Faced"].max().sum()
            strike_rate = round((runs / balls) * 100, 2)

            st.metric("Strike Rate", strike_rate)   
            yearly_runs = (
                t20_player.groupby("Date")["Batter Runs"]
                .sum()
            )

            yearly_runs.index = pd.to_datetime(yearly_runs.index).year

            yearly_runs = yearly_runs.groupby(level=0).sum().sort_index()

            st.subheader("📈 T20I Year-wise Runs")

            st.line_chart(yearly_runs) 
            comparison = pd.DataFrame({
                "Format": ["ODI", "T20I"],
                "Runs": [
                    odi_player["Runs by Batter"].sum(),
                    t20_player["Batter Runs"].sum()
                ]
            })

            st.subheader("📊 ODI vs T20I Runs")

            st.bar_chart(
                comparison.set_index("Format")
            )
            top_players = (
                t20_deliveries.groupby("Batter")["Batter Runs"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            st.subheader("🏏 Top 10 T20I Run Scorers")

            st.bar_chart(top_players)         

if page == "Team Search":

    st.header("🏏 Team Search")

    team_name = st.text_input("Enter Team Name")

    if team_name:

        odi_matches_team = odi_matches[
            (odi_matches["Team 1"].str.contains(team_name, case=False, na=False)) |
            (odi_matches["Team 2"].str.contains(team_name, case=False, na=False))
        ].copy()

        if odi_matches_team.empty:
            st.warning("Team not found.")

        else:

            team = pd.concat([
                odi_matches_team["Team 1"],
                odi_matches_team["Team 2"]
            ]).value_counts().index[0]

            matches = len(odi_matches_team)
            wins = (odi_matches_team["Winner"] == team).sum()

            losses = (
                (odi_matches_team["Winner"].notna()) &
                (odi_matches_team["Winner"] != team)
            ).sum()

            win_percentage = round(
                wins / matches * 100, 2
            )

            runs = odi_deliveries[
                odi_deliveries["Inning Team"] == team
            ]["Total Runs"].sum()

            st.subheader("ODI Team Profile")

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Team", team)
            col2.metric("Matches", matches)
            col3.metric("Wins", wins)
            col4.metric("Losses", losses)
            col5.metric("Win %", win_percentage)

            st.metric("Runs Scored", runs)  
            t20_team = t20_deliveries[
                (t20_deliveries["Bat First"].str.contains(team, case=False, na=False)) |
                (t20_deliveries["Bat Second"].str.contains(team, case=False, na=False))
            ].copy()

            if not t20_team.empty:

                t20_match_ids = t20_team["Match ID"].unique()
                t20_matches = len(t20_match_ids)

                t20_wins = (
                    t20_team.groupby("Match ID")["Winner"]
                    .first()
                    .str.contains(team, case=False, na=False)
                    .sum()
                )

                t20_losses = t20_matches - t20_wins

                t20_win_percentage = round(
                    t20_wins / t20_matches * 100, 2
                )

                t20_runs = t20_team[
                    t20_team["Bat First"].str.contains(
                        team, case=False, na=False
                    ) |
                    t20_team["Bat Second"].str.contains(
                        team, case=False, na=False
                    )
                ].groupby("Match ID")["Innings Runs"].max().sum()

                st.subheader("🏏 T20I Team Profile")

                col1, col2, col3, col4, col5 = st.columns(5)

                col1.metric("Matches", t20_matches)
                col2.metric("Wins", t20_wins)
                col3.metric("Losses", t20_losses)
                col4.metric("Win %", t20_win_percentage)
                col5.metric("Runs Scored", t20_runs) 
            st.subheader("📊 ODI Team Performance")

            performance = pd.DataFrame({
                "Result": ["Wins", "Losses"],
                "Matches": [wins, losses]
            })

            st.bar_chart(
                performance.set_index("Result")
            )

if page == "Head-to-Head":

    st.header("⚔️ Head-to-Head")

    team1 = st.text_input("Enter First Team")
    team2 = st.text_input("Enter Second Team")

    if team1 and team2:

        h2h = odi_matches[
            (
                (odi_matches["Team 1"].str.contains(team1, case=False, na=False)) &
                (odi_matches["Team 2"].str.contains(team2, case=False, na=False))
            ) |
            (
                (odi_matches["Team 1"].str.contains(team2, case=False, na=False)) &
                (odi_matches["Team 2"].str.contains(team1, case=False, na=False))
            )
        ].copy()

        if h2h.empty:
            st.warning("No head-to-head matches found.")

        else:

            actual_team1 = team1
            actual_team2 = team2

            matches = len(h2h)

            wins1 = (
                h2h["Winner"].str.contains(
                    actual_team1, case=False, na=False
                )
            ).sum()

            wins2 = (
                h2h["Winner"].str.contains(
                    actual_team2, case=False, na=False
                )
            ).sum()

            win_pct1 = round(wins1 / matches * 100, 2)
            win_pct2 = round(wins2 / matches * 100, 2)

            st.subheader(f"{actual_team1} vs {actual_team2}")

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric("Matches", matches)
            col2.metric(f"{actual_team1} Wins", wins1)
            col3.metric(f"{actual_team2} Wins", wins2)
            col4.metric(f"{actual_team1} Win %", win_pct1)
            col5.metric(f"{actual_team2} Win %", win_pct2)
            win_comparison = pd.DataFrame({
                "Team": [actual_team1, actual_team2],
                "Wins": [wins1, wins2]
            })

            st.subheader("📊 Head-to-Head Win Comparison")

            st.bar_chart(
                win_comparison.set_index("Team")
            )

            scores1 = odi_deliveries[
                odi_deliveries["Inning Team"].str.contains(
                    actual_team1, case=False, na=False
                )
            ]

            scores2 = odi_deliveries[
                odi_deliveries["Inning Team"].str.contains(
                    actual_team2, case=False, na=False
                )
            ]

            highest1 = scores1.groupby("Match ID")["Total Runs"].sum().max()
            lowest1 = scores1.groupby("Match ID")["Total Runs"].sum().min()

            highest2 = scores2.groupby("Match ID")["Total Runs"].sum().max()
            lowest2 = scores2.groupby("Match ID")["Total Runs"].sum().min()

            st.subheader("🏏 Team Scores")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(f"{actual_team1} Highest Score", highest1)
                st.metric(f"{actual_team1} Lowest Score", lowest1)

            with col2:
                st.metric(f"{actual_team2} Highest Score", highest2)
                st.metric(f"{actual_team2} Lowest Score", lowest2)
            t20_h2h = t20_deliveries[
                (
                    (t20_deliveries["Bat First"].str.contains(actual_team1, case=False, na=False)) &
                    (t20_deliveries["Bat Second"].str.contains(actual_team2, case=False, na=False))
                ) |
                (
                    (t20_deliveries["Bat First"].str.contains(actual_team2, case=False, na=False)) &
                    (t20_deliveries["Bat Second"].str.contains(actual_team1, case=False, na=False))
                )
            ].copy()

            if not t20_h2h.empty:

                t20_matches = t20_h2h["Match ID"].nunique()

                t20_match_results = (
                    t20_h2h.groupby("Match ID")["Winner"]
                    .first()
                )

                t20_wins1 = t20_match_results.str.contains(
                    actual_team1, case=False, na=False
                ).sum()

                t20_wins2 = t20_match_results.str.contains(
                    actual_team2, case=False, na=False
                ).sum()

                st.subheader("🏏 T20I Head-to-Head")

                col1, col2, col3 = st.columns(3)

                col1.metric("Matches", t20_matches)
                col2.metric(f"{actual_team1} Wins", t20_wins1)
                col3.metric(f"{actual_team2} Wins", t20_wins2)
if page == "Tournament Search":

    st.header("🏆 Tournament Search")

    tournament_name = st.text_input("Enter Tournament Name")

    if tournament_name:

        tournament = odi_matches[
            odi_matches["Event Name"].str.contains(
                tournament_name,
                case=False,
                na=False
            )
        ].copy()

        if tournament.empty:
            st.warning("Tournament not found.")

        else:

            matches = len(tournament)
            teams = pd.unique(
                tournament[["Team 1", "Team 2"]].values.ravel()
            )
            teams = [team for team in teams if pd.notna(team)]

            winners = tournament["Winner"].value_counts()

            st.subheader("🏆 Tournament Overview")

            col1, col2, col3 = st.columns(3)

            col1.metric("Matches", matches)
            col2.metric("Teams", len(teams))
            col3.metric("Top Winning Team", winners.index[0])

            st.subheader("📊 Matches by Team")

            team_matches = pd.concat([
                tournament["Team 1"],
                tournament["Team 2"]
            ]).value_counts()

            st.bar_chart(team_matches.head(10))

            st.subheader("🥇 Wins by Team")

            st.bar_chart(winners.head(10))
            tournament_ids = tournament["Match ID"].unique()

            tournament_deliveries = odi_deliveries[
                odi_deliveries["Match ID"].isin(tournament_ids)
            ]

            top_run_scorer = (
                tournament_deliveries.groupby("Batter")["Runs by Batter"]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            top_wicket_taker = (
                tournament_deliveries[
                    tournament_deliveries["Wicket Kind"].notna()
                ]
                .groupby("Bowler")["Wicket Kind"]
                .count()
                .sort_values(ascending=False)
                .head(10)
            )

            st.subheader("🏏 Top Run Scorers")

            st.bar_chart(top_run_scorer)

            st.subheader("🎯 Top Wicket Takers")

            st.bar_chart(top_wicket_taker)
            highest_score = (
                tournament_deliveries.groupby("Match ID")
                .apply(
                    lambda x: x.groupby("Batter")["Runs by Batter"].sum().max()
                )
                .max()
            )

            best_bowler = (
                tournament_deliveries[
                    tournament_deliveries["Wicket Kind"].notna()
                ]
                .groupby("Bowler")["Wicket Kind"]
                .count()
                .sort_values(ascending=False)
            )

            st.subheader("⭐ Tournament Highlights")

            col1, col2 = st.columns(2)

            col1.metric("Highest Individual Score", highest_score)
            col2.metric(
                "Best Wicket Taker",
                best_bowler.index[0] if not best_bowler.empty else "N/A"
            )