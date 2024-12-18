# test_basketball_analysis.py will test the following functions:

import pytest
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import code.basketball_analysis as ba
from unittest.mock import patch

@pytest.fixture
def sample_data():
    """
    Create sample data for testing
    """
    return pd.DataFrame({
        'game_id': [1, 1, 2, 2],
        'home': ['Kentucky', 'Kentucky', 'Duke', 'Duke'],
        'away': ['Duke', 'Duke', 'Tennessee', 'Tennessee'],
        'home_score': [80, 80, 75, 75],
        'away_score': [75, 75, 70, 70],
        'shot_team': ['Kentucky', 'Kentucky', 'Duke', 'Duke'],
        'shooter': ['Player1', 'Player2', 'Player3', 'Player4'],
        'shot_outcome': ['made', 'made', 'made', 'made'],
        'three_pt': [True, False, True, False],
        'free_throw': [False, False, False, False],
        'description': ['Three Point Shot', 'Jump Shot', 'Three Point Shot', 'Jump Shot']
    })

@pytest.fixture(autouse=True)
def mpl_backend():
    """
    Configure matplotlib to use non-interactive backend for testing
    """
    plt.switch_backend('Agg')
    yield
    plt.close('all')

@pytest.fixture
def mock_load_dataset(sample_data):
    """
    Mock the load_dataset function to return sample data
    """
    with patch('code.data_loader.load_dataset', return_value=sample_data):
        yield

def test_calculate_wins_losses(sample_data):
    wins, losses, games = ba.calculate_wins_losses(sample_data, 'Kentucky')
    assert games == 1
    assert wins == 1
    assert losses == 0

def test_calculate_shooting_percentages(sample_data):
    team_shots = sample_data[sample_data['shot_team'] == 'Kentucky']
    fg_pct, three_pct = ba.calculate_shooting_percentages(team_shots)
    assert fg_pct == pytest.approx(100.0)
    assert three_pct == pytest.approx(100.0)

def test_get_team_stats(sample_data):
    stats = ba.get_team_stats(sample_data, 'Kentucky')
    assert stats['games_played'] == 1
    assert stats['wins'] == 1
    assert stats['losses'] == 0
    assert stats['fg_percentage'] == pytest.approx(100.0)
    assert stats['three_percentage'] == pytest.approx(100.0)

def test_get_player_stats(sample_data):
    stats_df = ba.get_player_stats(sample_data, 'Kentucky')
    assert len(stats_df) == 2 
    player1_stats = stats_df[stats_df['player'] == 'Player1'].iloc[0]
    assert player1_stats['total_points'] == 3
    assert player1_stats['games_played'] == 1

def test_process_shots_for_chart(sample_data):
    shots = ba.process_shots_for_chart(sample_data, 'Kentucky', is_team=True)
    assert len(shots) == 2
    assert 'shot_type' in shots.columns

def test_get_zone_color():
    assert ba.get_zone_color(0) == 'lightgray'
    assert ba.get_zone_color(42) == '#ff4747'
    assert ba.get_zone_color(50) == '#f7f36d'
    assert ba.get_zone_color(60) == '#bff783'
    assert ba.get_zone_color(80) == '#76f562'
    assert ba.get_zone_color(81) == '#05fa05'

def test_create_shot_chart(sample_data):
    shots = ba.process_shots_for_chart(sample_data, 'Kentucky', is_team=True)
    fig = ba.create_shot_chart(shots, 'Kentucky')
    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) > 0
    plt.close(fig)

def test_create_shot_analysis(sample_data):
    shot_data = sample_data[sample_data['shot_team'] == 'Kentucky']
    fig = ba.create_shot_analysis(shot_data, 'Kentucky')
    assert isinstance(fig, go.Figure)
    assert 'Shot Type Distribution for Kentucky' in fig.layout.title.text

def test_create_player_performance_matrix(sample_data):
    player_stats = ba.get_player_stats(sample_data, 'Kentucky')
    fig = ba.create_player_performance_matrix(player_stats, 'Kentucky')
    assert isinstance(fig, go.Figure)

def test_create_team_comparison_chart(sample_data):
    team1_stats = ba.get_team_stats(sample_data, 'Kentucky')
    team2_stats = ba.get_team_stats(sample_data, 'Duke')
    fig = ba.create_team_comparison_chart(team1_stats, team2_stats, 'Kentucky', 'Duke')
    assert isinstance(fig, go.Figure)

def test_create_conference_standings(sample_data):
    fig = ba.create_conference_standings(sample_data, ba.CONFERENCE_TEAMS['SEC'])
    assert isinstance(fig, go.Figure)

def test_create_three_point_vertices():
    vertices = ba.create_three_point_vertices()
    assert isinstance(vertices, list)
    assert len(vertices) > 0
    for vertex in vertices:
        assert isinstance(vertex, tuple)
        assert len(vertex) == 2

def test_draw_court():
    fig, ax = plt.subplots()
    result_ax = ba.draw_court(ax)
    assert result_ax is not None
    assert len(ax.patches) > 0
    assert len(ax.lines) > 0
    plt.close(fig)
