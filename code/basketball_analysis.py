# basketball_analysis.py file: These are all the functions used in the final_dashboard.py file.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Path, PathPatch
import plotly.express as px
import plotly.graph_objects as go

def load_dataset():
    """
    Load the dataset from Google Drive with direct download
    Returns:
        pandas.DataFrame: The loaded dataset
    """
    file_id = "1qHqMKHwmO3QX0HGotAVVBrSPBEIVonlK"
    
    # Create direct download URL
    download_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    
    try:
        # Download the file directly
        df = pd.read_csv(download_url)
        return df
    except Exception as e:
        print(f"Error downloading the file: {e}")
        return None

CONFERENCE_TEAMS = {
    'SEC': [
        'Alabama', 'Arkansas', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 
        'LSU', 'Mississippi State', 'Missouri', 'Ole Miss', 'South Carolina', 
        'Tennessee', 'Texas A&M', 'Vanderbilt'
    ],
    'Big Ten': [
        'Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan', 'Michigan State',
        'Minnesota', 'Nebraska', 'Northwestern', 'Ohio State', 'Penn State',
        'Purdue', 'Rutgers', 'Wisconsin'
    ],
    'Big 12': [
        'BYU', 'Cincinnati', 'Baylor', 'Houston', 'Iowa State', 'Kansas',
        'Kansas State', 'Oklahoma', 'Oklahoma State', 'TCU', 'Texas',
        'Texas Tech', 'UCF', 'West Virginia'
    ],
    'ACC': [
        'Boston College', 'Clemson', 'Duke', 'Florida State', 'Georgia Tech',
        'Louisville', 'Miami FL', 'NC State', 'North Carolina', 'Pittsburgh',
        'Syracuse', 'Virginia', 'Virginia Tech', 'Wake Forest', 'Notre Dame'
    ]
}

def load_and_clean_data():
    """
    Load data from Google Drive and clean it
    Returns:
        pandas.DataFrame: Cleaned basketball data
    """
    # Load the data using the Google Drive loader
    df = load_dataset()
    
    if df is None:
        raise Exception("Failed to load dataset from Google Drive")
    
    # Create a copy to avoid modifying the original
    df = df.copy()

    return df

def calculate_wins_losses(df, team):
    """
    Helper function to calculate wins and losses for a team
    """
    final_scores = df.groupby('game_id').agg({
        'home': 'first',
        'away': 'first',
        'home_score': 'last',
        'away_score': 'last'
    }).dropna()
    
    home_wins = final_scores[
        (final_scores['home'] == team) & 
        (final_scores['home_score'] > final_scores['away_score'])
    ].shape[0]
    
    away_wins = final_scores[
        (final_scores['away'] == team) & 
        (final_scores['away_score'] > final_scores['home_score'])
    ].shape[0]
    
    games_played = len(df[df['shot_team'] == team]['game_id'].unique())
    return home_wins + away_wins, games_played - (home_wins + away_wins), games_played

def calculate_shooting_percentages(team_shots):
    """
    Helper function to calculate shooting percentages
    """
    fg_shots = team_shots[~team_shots['description'].str.contains('Free Throw', na=False)]
    fg_made = len(fg_shots[fg_shots['shot_outcome'] == 'made'])
    fg_total = len(fg_shots)
    fg_percentage = (fg_made / fg_total * 100) if fg_total > 0 else 0
    
    three_shots = team_shots[team_shots['three_pt'] == True]
    three_made = len(three_shots[three_shots['shot_outcome'] == 'made'])
    three_total = len(three_shots)
    three_percentage = (three_made / three_total * 100) if three_total > 0 else 0
    
    return fg_percentage, three_percentage

def get_team_stats(df, team):
    """
    Calculate comprehensive team statistics
    """
    team_shots = df[df['shot_team'] == team]
    total_wins, total_losses, games_played = calculate_wins_losses(df, team)
    fg_percentage, three_percentage = calculate_shooting_percentages(team_shots)
    
    return {
        'games_played': games_played,
        'wins': total_wins,
        'losses': total_losses,
        'fg_percentage': fg_percentage,
        'three_percentage': three_percentage
    }

def get_player_stats(df, team):
    """
    Calculate player statistics for a given team
    """
    team_shots = df[df['shot_team'] == team]
    
    player_stats = []
    for player in team_shots['shooter'].dropna().unique():
        player_shots = team_shots[team_shots['shooter'] == player]
        games_played = len(player_shots['game_id'].unique())
        
        # Calculate points
        total_points = sum(
            3 if shot['three_pt'] else 2 if not shot['free_throw'] else 1
            for _, shot in player_shots[player_shots['shot_outcome'] == 'made'].iterrows()
        )
        
        # Calculate percentages
        fg_pct, three_pct = calculate_shooting_percentages(player_shots)
        
        player_stats.append({
            'player': player,
            'total_points': total_points,
            'ppg': total_points / games_played if games_played > 0 else 0,
            'games_played': games_played,
            'fg_percentage': fg_pct,
            'three_percentage': three_pct
        })
    
    return pd.DataFrame(player_stats)

def create_player_performance_matrix(player_stats, team_name):
    """
    Create a scatter plot of player performance metrics
    """
    if player_stats.empty:
        return None
    
    fig = px.scatter(
        player_stats,
        x='fg_percentage',
        y='ppg',
        size='total_points',
        color='three_percentage',
        hover_name='player',
        title=f"{team_name} Player Performance Matrix",
        labels={
            'fg_percentage': 'Field Goal %',
            'ppg': 'Points per Game',
            'three_percentage': '3PT%'
        }
    )
    
    fig.update_layout(
        xaxis_title="Field Goal %",
        yaxis_title="Points per Game",
        height=400
    )
    
    return fig

def create_team_comparison_chart(team1_stats, team2_stats, team1_name, team2_name):
    """
    Create a bar chart comparing team statistics
    """
    categories = ['Win %', 'FG%', '3PT%']
    
    # Calculate win percentage for both teams
    team1_win_pct = (team1_stats['wins'] / team1_stats['games_played'] * 100) if team1_stats['games_played'] > 0 else 0
    team2_win_pct = (team2_stats['wins'] / team2_stats['games_played'] * 100) if team2_stats['games_played'] > 0 else 0
    
    team1_values = [
        team1_win_pct,
        team1_stats['fg_percentage'],
        team1_stats['three_percentage']
    ]
    
    team2_values = [
        team2_win_pct,
        team2_stats['fg_percentage'],
        team2_stats['three_percentage']
    ]
    
    fig = go.Figure(data=[
        go.Bar(
            name=team1_name, 
            x=categories, 
            y=team1_values,
            text=[f"{val:.1f}%" for val in team1_values],
            textposition='outside'
        ),
        go.Bar(
            name=team2_name, 
            x=categories, 
            y=team2_values,
            text=[f"{val:.1f}%" for val in team2_values],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Team Performance Comparison",
        yaxis_title="Percentage",
        barmode='group',
        yaxis={'range': [0, 100]},  # Set y-axis from 0 to 100
        height=500
    )
    
    return fig

def create_top_scorers_comparison(team1_players, team2_players, team1_name, team2_name):
    """
    Create a bar chart comparing top scorers from both teams
    """
    fig = go.Figure()
    
    # Add bars for team 1
    fig.add_trace(go.Bar(
        x=team1_players['player'],
        y=team1_players['ppg'],
        name=team1_name,
        marker_color='blue',
        text=team1_players['ppg'].round(1),  # Add text labels
        textposition='outside'  # Position labels outside the bars
    ))
    
    # Add bars for team 2
    fig.add_trace(go.Bar(
        x=team2_players['player'],
        y=team2_players['ppg'],
        name=team2_name,
        marker_color='red',
        text=team2_players['ppg'].round(1),  # Add text labels
        textposition='outside'  # Position labels outside the bars
    ))
    
    fig.update_layout(
        title="Top Scorers Comparison",
        xaxis_title="Player",
        yaxis_title="Points per Game",
        barmode='group',
        showlegend=True,
        height=500
    )
    
    return fig

def create_conference_standings(df, conference_teams):
    """
    Create a bar chart showing conference standings
    """
    team_stats = []
    
    for team in conference_teams:
        # Calculate wins and total games
        home_games = df[df['home'] == team]['game_id'].unique()
        away_games = df[df['away'] == team]['game_id'].unique()
        
        # Skip teams with no data
        if len(home_games) == 0 and len(away_games) == 0:
            continue
        
        # Find final scores for each game
        final_scores = df.groupby('game_id').agg({
            'home': 'first',
            'away': 'first',
            'home_score': 'last',
            'away_score': 'last'
        }).dropna()
        
        # Count wins
        home_wins = final_scores[
            (final_scores['home'] == team) & 
            (final_scores['home_score'] > final_scores['away_score'])
        ].shape[0]
        
        away_wins = final_scores[
            (final_scores['away'] == team) & 
            (final_scores['away_score'] > final_scores['home_score'])
        ].shape[0]
        
        total_games = len(set(home_games) | set(away_games))
        total_wins = home_wins + away_wins
        win_percentage = (total_wins / total_games * 100) if total_games > 0 else 0
        
        # Calculate team's FG%
        team_shots = df[df['shot_team'] == team]
        team_made = len(team_shots[team_shots['shot_outcome'] == 'made'])
        team_total = len(team_shots)
        fg_percentage = (team_made / team_total * 100) if team_total > 0 else 0
        
        team_stats.append({
            'Team': team,
            'Win Percentage': win_percentage,
            'FG Percentage': fg_percentage,
            'Wins': total_wins,
            'Total Games': total_games
        })
    
    # Create DataFrame and sort by win percentage (descending)
    stats_df = pd.DataFrame(team_stats)
    stats_df = stats_df.sort_values('Win Percentage', ascending=False)
    
    fig = go.Figure()
    
    # Add bars for Win % and FG %
    fig.add_trace(go.Bar(
        x=stats_df['Team'],
        y=stats_df['Win Percentage'],
        name='Win %',
        marker_color='green',
        text=stats_df['Win Percentage'].round(1),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        x=stats_df['Team'],
        y=stats_df['FG Percentage'],
        name='FG %',
        marker_color='blue',
        text=stats_df['FG Percentage'].round(1),
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Conference Team Performance",
        xaxis_title="Team",
        yaxis_title="Percentage",
        barmode='group',
        height=600,
        xaxis={'tickangle': 45},
        yaxis={'range': [0, 100]},
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    
    return fig

def create_three_point_vertices():
    """
    Create vertices for the three-point line.
    """
    angles = np.linspace(np.pi, 0, 100)
    three_x = 237.5 * np.cos(angles)
    three_y = 237.5 * np.sin(angles) + 0
    
    vertices = [(three_x[0], three_y[0])]
    vertices.extend(list(zip(three_x, three_y)))
    vertices.extend([(three_x[-1], three_y[-1])])
    
    return vertices

def draw_court(ax=None, color='black', lw=2):
    """
    Draw a basketball court.
    """
    if ax is None:
        ax = plt.gca()
    
    # Court boundaries
    ax.plot([-250, 250], [-47.5, -47.5], color=color, lw=lw)
    ax.plot([-250, 250], [422.5, 422.5], color=color, lw=lw)
    ax.plot([-250, -250], [-47.5, 422.5], color=color, lw=lw)
    ax.plot([250, 250], [-47.5, 422.5], color=color, lw=lw)
    
    # The paint
    ax.plot([-80, -80], [-47.5, 142.5], color=color, lw=lw)
    ax.plot([80, 80], [-47.5, 142.5], color=color, lw=lw)
    ax.plot([-80, 80], [142.5, 142.5], color=color, lw=lw)
    
    # Free throw circle
    free_throw = Circle((0, 142.5), radius=60, fill=False, color=color, lw=lw)
    ax.add_patch(free_throw)
    
    # Restricted area
    restricted = Circle((0, 0), radius=40, fill=False, color=color, lw=lw)
    ax.add_patch(restricted)
    
    # Three point line
    three_vertices = create_three_point_vertices()
    three_path = Path(three_vertices)
    three_patch = PathPatch(three_path, fill=False, color=color, lw=lw)
    ax.add_patch(three_patch)
    
    return ax

def get_zone_color(percentage):
    """
    Return color based on shooting percentage.
    """
    if percentage == 0:
        return 'lightgray'
    elif percentage <= 42:
        return '#ff4747'
    elif percentage <= 50:
        return '#f7f36d'
    elif percentage <= 60:
        return '#bff783'
    elif percentage <= 80:
        return '#76f562'
    else:
        return '#05fa05'

def process_shots_for_chart(df, name, is_team=True):
    """
    Process shot data for the court visualization
    """
    if is_team:
        shots = df[df['shot_team'] == name].copy()
    else:
        shots = df[df['shooter'] == name].copy()
    
    # Classify shots
    shots['shot_type'] = 'Mid-Range'  # Default
    shots.loc[shots['three_pt'] == True, 'shot_type'] = 'Three Point'
    shots.loc[shots['description'].str.contains('Layup', na=False), 'shot_type'] = 'Layup'
    
    return shots

def create_shot_chart(shot_data, name):
    """
    Create the shot chart visualization
    """
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    
    # Draw court
    draw_court(ax)
    
    # Calculate zone statistics
    shot_stats = {}
    for shot_type in ['Layup', 'Mid-Range', 'Three Point']:
        type_shots = shot_data[shot_data['shot_type'] == shot_type]
        made = len(type_shots[type_shots['shot_outcome'] == 'made'])
        total = len(type_shots)
        pct = (made / total * 100) if total > 0 else 0
        shot_stats[shot_type] = {'made': made, 'total': total, 'percentage': pct}
    
    # Add zone shading
    layup_circle = Circle((0, 0), 40, alpha=0.3, 
                         facecolor=get_zone_color(shot_stats['Layup']['percentage']))
    ax.add_patch(layup_circle)
    
    midrange_rect = Rectangle((-237.5, -47.5), 475, 285, alpha=0.3,
                            facecolor=get_zone_color(shot_stats['Mid-Range']['percentage']))
    ax.add_patch(midrange_rect)
    
    three_vertices = create_three_point_vertices()
    three_path = Path(three_vertices)
    three_patch = PathPatch(three_path, 
                          facecolor=get_zone_color(shot_stats['Three Point']['percentage']),
                          alpha=0.3)
    ax.add_patch(three_patch)
    
    # Add text labels for each zone
    text_positions = {
        'Layup': (0, 20),
        'Mid-Range': (0, 100),
        'Three Point': (0, 262.5)
    }
    
    for shot_type, pos in text_positions.items():
        stats = shot_stats[shot_type]
        ax.text(
            pos[0], pos[1],
            f'{shot_type}\n{stats["percentage"]:.1f}%\n({stats["made"]}/{stats["total"]})',
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=10,
            fontweight='bold',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
    
    ax.set_xlim(-250, 250)
    ax.set_ylim(-47.5, 422.5)
    ax.axis('off')
    plt.title(f"Shot Chart - {name}", pad=20, fontsize=14)
    
    return fig

def create_shot_analysis(shot_data, team_name):
    """
    Create shot type distribution chart
    """
    shot_types = []
    
    for _, shot in shot_data.iterrows():
        if 'Free Throw' in str(shot['description']):
            shot_type = 'Free Throw'
        elif shot['three_pt']:
            shot_type = '3-Point'
        else:
            shot_type = '2-Point'
        shot_types.append(shot_type)
    
    shot_data['shot_type'] = shot_types
    shot_type_counts = pd.DataFrame(shot_data['shot_type'].value_counts()).reset_index()
    shot_type_counts.columns = ['Shot Type', 'Count']
    
    return px.pie(
        shot_type_counts,
        values='Count',
        names='Shot Type',
        title=f"Shot Type Distribution for {team_name}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

