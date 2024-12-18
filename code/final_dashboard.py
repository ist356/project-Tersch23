# final_dashboard.py will run a streamlit dashboard.

import streamlit as st
import pandas as pd
from basketball_analysis import (
    load_and_clean_data, 
    get_team_stats, 
    get_player_stats,
    CONFERENCE_TEAMS,
    create_player_performance_matrix,
    create_team_comparison_chart,
    create_top_scorers_comparison,
    create_conference_standings,
    process_shots_for_chart,
    create_shot_chart,
    create_shot_analysis
)

def render_team_analysis(df, selected_team):
    """
    Render the team analysis tab content
    """
    st.header(f"{selected_team} Analysis")
    
    team_stats = get_team_stats(df, selected_team)
    
    with st.expander("Team Statistics", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        metrics = [
            (col1, "Games Played", team_stats['games_played']),
            (col2, "Wins", team_stats['wins']),
            (col3, "Losses", team_stats['losses']),
            (col4, "FG%", f"{team_stats['fg_percentage']:.1f}%"),
            (col5, "3PT%", f"{team_stats['three_percentage']:.1f}%")
        ]
        for col, label, value in metrics:
            with col:
                st.metric(label, value)
    
    col1, col2 = st.columns(2)
    
    with col1:
        shot_data = df[df['shot_team'] == selected_team]
        fig = create_shot_analysis(shot_data, selected_team)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        player_stats = get_player_stats(df, selected_team)
        if not player_stats.empty:
            fig = create_player_performance_matrix(player_stats, selected_team)
            st.plotly_chart(fig, use_container_width=True)

def render_shot_charts(df, selected_team):
    """
    Render the shot charts section
    """
    st.subheader("Shot Charts")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Team Shot Chart")
        team_shots = process_shots_for_chart(df, selected_team, is_team=True)
        if len(team_shots) > 0:
            fig = create_shot_chart(team_shots, selected_team)
            st.pyplot(fig, use_container_width=True)
        else:
            st.warning("No shot data available for selected team.")
    
    with col2:
        st.subheader("Player Shot Chart")
        team_players = df[
            (df['shot_team'] == selected_team) & 
            (pd.notna(df['shot_outcome']))
        ]['shooter'].unique()
        
        if len(team_players) > 0:
            selected_player = st.selectbox(
                "Select Player",
                options=sorted(team_players),
                key="player_shot_chart"
            )
            
            player_shots = process_shots_for_chart(
                df[df['shot_team'] == selected_team],
                selected_player,
                is_team=False
            )
            
            if len(player_shots) > 0:
                made_shots = len(player_shots[player_shots['shot_outcome'] == 'made'])
                total_shots = len(player_shots)
                shot_percentage = (made_shots / total_shots * 100) if total_shots > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                metrics = [
                    (col1, "Total Shots", total_shots),
                    (col2, "Made Shots", made_shots),
                    (col3, "Shooting %", f"{shot_percentage:.1f}%")
                ]
                for col, label, value in metrics:
                    with col:
                        st.metric(label, value)
                
                fig = create_shot_chart(player_shots, f"{selected_player}")
                st.pyplot(fig, use_container_width=True)
            else:
                st.warning("No shot data available for selected player.")
        else:
            st.warning("No players with shot data found for selected team.")

def main():
    st.set_page_config(layout="wide", page_title="NCAA Basketball Analysis Final Project")
    st.title("Big 4 Conference Basketball Analysis")
    
    try:
        df = load_and_clean_data()
        if df is None:
            st.error("Failed to load the dataset. Please check your internet connection and try again.")
            return
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return

    with st.sidebar:
        st.header("Filters")
        selected_conference = st.selectbox(
            "Select Conference",
            options=['All'] + list(CONFERENCE_TEAMS.keys())
        )
        
        team_options = ([team for teams in CONFERENCE_TEAMS.values() for team in teams]
                       if selected_conference == 'All'
                       else CONFERENCE_TEAMS[selected_conference])
        
        selected_team = st.selectbox("Select Team", sorted(team_options))
    
    tab1, tab2, tab3 = st.tabs(["Team Analysis", "Team Comparison", "Conference Overview"])
    
    with tab1:
        render_team_analysis(df, selected_team)
        render_shot_charts(df, selected_team)
    
    with tab2:
        st.header("Team Comparison")
        col1, col2 = st.columns(2)
        with col1:
            team1 = st.selectbox("Select First Team", sorted(team_options), key='team1')
        with col2:
            team2 = st.selectbox("Select Second Team", 
                               [t for t in sorted(team_options) if t != team1],
                               key='team2')
        
        team1_stats = get_team_stats(df, team1)
        team2_stats = get_team_stats(df, team2)
        
        fig = create_team_comparison_chart(team1_stats, team2_stats, team1, team2)
        st.plotly_chart(fig, use_container_width=True)
        
        team1_players = get_player_stats(df, team1).nlargest(5, 'ppg')
        team2_players = get_player_stats(df, team2).nlargest(5, 'ppg')
        fig = create_top_scorers_comparison(team1_players, team2_players, team1, team2)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Conference Overview")
        selected_conf = st.selectbox(
            "Select Conference for Analysis",
            options=list(CONFERENCE_TEAMS.keys()),
            key='conf_overview'
        )
        
        fig = create_conference_standings(df, CONFERENCE_TEAMS[selected_conf])
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()