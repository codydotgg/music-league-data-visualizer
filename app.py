import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Music League Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a unique aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Dela+Gothic+One&family=DM+Sans:wght@400;500;700&display=swap');
    
    :root {
        --accent-coral: #FF6B6B;
        --accent-mint: #4ECDC4;
        --accent-gold: #FFE66D;
        --accent-purple: #A855F7;
        --dark-bg: #0F0F1A;
        --card-bg: #1A1A2E;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0F0F1A 0%, #1A1A2E 50%, #16213E 100%);
    }
    
    h1, h2, h3 {
        font-family: 'Dela Gothic One', cursive !important;
    }
    
    .main-title {
        font-family: 'Dela Gothic One', cursive;
        font-size: 3.5rem;
        background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 50%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0;
        text-shadow: 0 0 40px rgba(255, 107, 107, 0.3);
    }
    
    .subtitle {
        font-family: 'DM Sans', sans-serif;
        color: #888;
        text-align: center;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #1A1A2E 0%, #16213E 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .metric-value {
        font-family: 'Dela Gothic One', cursive;
        font-size: 2.5rem;
        color: #4ECDC4;
    }
    
    .metric-label {
        font-family: 'DM Sans', sans-serif;
        color: #888;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .round-card {
        background: linear-gradient(145deg, rgba(168, 85, 247, 0.1) 0%, rgba(78, 205, 196, 0.1) 100%);
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .song-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4ECDC4;
        transition: all 0.3s ease;
    }
    
    .song-card:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateX(5px);
    }
    
    .winner-badge {
        background: linear-gradient(135deg, #FFE66D 0%, #FF6B6B 100%);
        color: #000;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
    }
    
    .comment-bubble {
        background: rgba(78, 205, 196, 0.1);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-left: 3px solid #4ECDC4;
        font-style: italic;
        color: #ccc;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 16px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 12px 24px;
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #A855F7 0%, #4ECDC4 100%) !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'Dela Gothic One', cursive;
        font-size: 2rem;
    }
    
    .stSelectbox > div > div {
        background: rgba(26, 26, 46, 0.8);
        border-radius: 12px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213E 0%, #0F0F1A 100%);
    }
    
    section[data-testid="stSidebar"] .stMarkdown h1 {
        font-size: 1.5rem;
        color: #4ECDC4;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and process all CSV data"""
    competitors = pd.read_csv("competitors.csv")
    rounds = pd.read_csv("rounds.csv")
    submissions = pd.read_csv("submissions.csv")
    votes = pd.read_csv("votes.csv")
    
    # Convert dates
    rounds['Created'] = pd.to_datetime(rounds['Created'])
    submissions['Created'] = pd.to_datetime(submissions['Created'])
    votes['Created'] = pd.to_datetime(votes['Created'])
    
    return competitors, rounds, submissions, votes


def get_leaderboard(competitors, submissions, votes):
    """Calculate overall leaderboard"""
    # Sum points for each submission
    song_points = votes.groupby('Spotify URI')['Points Assigned'].sum().reset_index()
    song_points.columns = ['Spotify URI', 'Total Points']
    
    # Merge with submissions to get submitter
    submissions_with_points = submissions.merge(song_points, on='Spotify URI', how='left')
    submissions_with_points['Total Points'] = submissions_with_points['Total Points'].fillna(0)
    
    # Sum by submitter
    leaderboard = submissions_with_points.groupby('Submitter ID').agg({
        'Total Points': 'sum',
        'Spotify URI': 'count'
    }).reset_index()
    leaderboard.columns = ['ID', 'Total Points', 'Songs Submitted']
    
    # Merge with competitor names
    leaderboard = leaderboard.merge(competitors, on='ID')
    leaderboard = leaderboard.sort_values('Total Points', ascending=False).reset_index(drop=True)
    leaderboard['Rank'] = range(1, len(leaderboard) + 1)
    
    return leaderboard


def get_song_standings(submissions, votes, competitors):
    """Get standings for songs in a round"""
    song_points = votes.groupby('Spotify URI').agg({
        'Points Assigned': ['sum', 'mean', 'count'],
        'Comment': lambda x: [c for c in x if pd.notna(c) and str(c).strip()]
    }).reset_index()
    song_points.columns = ['Spotify URI', 'Total Points', 'Avg Points', 'Vote Count', 'Comments']
    
    result = submissions.merge(song_points, on='Spotify URI', how='left')
    result = result.merge(competitors.rename(columns={'ID': 'Submitter ID'}), on='Submitter ID')
    result = result.sort_values('Total Points', ascending=False).reset_index(drop=True)
    
    return result


def get_voting_patterns(votes, competitors):
    """Analyze voting patterns between competitors"""
    votes_with_names = votes.merge(
        competitors.rename(columns={'ID': 'Voter ID', 'Name': 'Voter Name'}),
        on='Voter ID'
    )
    
    # Calculate average vote given
    avg_given = votes_with_names.groupby('Voter Name')['Points Assigned'].mean().reset_index()
    avg_given.columns = ['Name', 'Avg Points Given']
    
    # Calculate vote distribution
    vote_dist = votes_with_names.groupby('Voter Name')['Points Assigned'].agg(['mean', 'std', 'min', 'max']).reset_index()
    
    return avg_given, vote_dist, votes_with_names


# Load data
competitors, rounds, submissions, votes = load_data()

# Header
st.markdown('<h1 class="main-title">🎵 Music League</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Track the competition, discover trends, flex your taste</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    
    # Round selector
    round_options = rounds['Name'].tolist()
    if len(round_options) > 1:
        selected_round = st.selectbox("Select Round", round_options)
        round_data = rounds[rounds['Name'] == selected_round].iloc[0]
    else:
        selected_round = round_options[0]
        round_data = rounds.iloc[0]
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("## 📊 Quick Stats")
    st.metric("Competitors", len(competitors))
    st.metric("Total Rounds", len(rounds))
    st.metric("Total Submissions", len(submissions))
    st.metric("Total Votes Cast", len(votes))
    
    st.markdown("---")
    
    # Playlist link
    if pd.notna(round_data['Playlist URL']):
        st.markdown(f"### 🎧 [Open Playlist]({round_data['Playlist URL']})")

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Leaderboard", 
    "🎵 Round Results", 
    "📈 Voting Analytics",
    "👤 Player Profiles",
    "💬 Best Comments"
])

# Tab 1: Leaderboard
with tab1:
    st.markdown("## 🏆 Overall Standings")
    
    leaderboard = get_leaderboard(competitors, submissions, votes)
    
    # Top 3 podium
    if len(leaderboard) >= 3:
        cols = st.columns([1, 1.2, 1])
        
        with cols[0]:
            second = leaderboard.iloc[1]
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem 1rem; background: linear-gradient(145deg, rgba(192, 192, 192, 0.1) 0%, rgba(192, 192, 192, 0.05) 100%); border-radius: 20px; border: 2px solid rgba(192, 192, 192, 0.3);">
                <div style="font-size: 3rem;">🥈</div>
                <div style="font-family: 'Dela Gothic One', cursive; font-size: 1.5rem; color: #C0C0C0;">{second['Name']}</div>
                <div style="font-size: 2rem; font-weight: bold; color: #4ECDC4;">{int(second['Total Points'])} pts</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            first = leaderboard.iloc[0]
            st.markdown(f"""
            <div style="text-align: center; padding: 2.5rem 1rem; background: linear-gradient(145deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 215, 0, 0.05) 100%); border-radius: 20px; border: 2px solid rgba(255, 215, 0, 0.4); transform: scale(1.05);">
                <div style="font-size: 4rem;">👑</div>
                <div style="font-family: 'Dela Gothic One', cursive; font-size: 1.8rem; color: #FFD700;">{first['Name']}</div>
                <div style="font-size: 2.5rem; font-weight: bold; color: #FFE66D;">{int(first['Total Points'])} pts</div>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[2]:
            third = leaderboard.iloc[2]
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem 1rem; background: linear-gradient(145deg, rgba(205, 127, 50, 0.1) 0%, rgba(205, 127, 50, 0.05) 100%); border-radius: 20px; border: 2px solid rgba(205, 127, 50, 0.3);">
                <div style="font-size: 3rem;">🥉</div>
                <div style="font-family: 'Dela Gothic One', cursive; font-size: 1.5rem; color: #CD7F32;">{third['Name']}</div>
                <div style="font-size: 2rem; font-weight: bold; color: #4ECDC4;">{int(third['Total Points'])} pts</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Full leaderboard chart
    fig = go.Figure()
    
    colors = ['#FFD700' if i == 0 else '#C0C0C0' if i == 1 else '#CD7F32' if i == 2 else '#4ECDC4' 
              for i in range(len(leaderboard))]
    
    fig.add_trace(go.Bar(
        x=leaderboard['Total Points'],
        y=leaderboard['Name'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.2)', width=1)
        ),
        text=leaderboard['Total Points'].astype(int),
        textposition='outside',
        textfont=dict(color='white', size=14)
    ))
    
    fig.update_layout(
        title=dict(text='Points by Player', font=dict(size=20, color='white')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=False, autorange='reversed'),
        height=max(400, len(leaderboard) * 40),
        margin=dict(l=20, r=100, t=60, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Tab 2: Round Results
with tab2:
    st.markdown(f"## {round_data['Name']}")
    st.markdown(f"*{round_data['Description']}*")
    
    round_submissions = submissions[submissions['Round ID'] == round_data['ID']]
    round_votes = votes[votes['Round ID'] == round_data['ID']]
    
    song_standings = get_song_standings(round_submissions, round_votes, competitors)
    
    # Winner highlight
    if len(song_standings) > 0:
        winner = song_standings.iloc[0]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 107, 107, 0.1) 100%); 
                    border-radius: 20px; padding: 2rem; margin: 1rem 0; border: 2px solid rgba(255, 215, 0, 0.3);">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <span style="font-size: 3rem;">🏆</span>
                <div>
                    <span class="winner-badge">ROUND WINNER</span>
                    <h3 style="margin: 0.5rem 0; color: #FFE66D;">{winner['Title']}</h3>
                    <p style="margin: 0; color: #ccc;">{winner['Artist(s)']} • Submitted by <strong>{winner['Name']}</strong></p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.5rem; color: #4ECDC4;">{int(winner['Total Points'])} points</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # All songs ranking
    st.markdown("### 📊 Full Results")
    
    for idx, row in song_standings.iterrows():
        rank = idx + 1
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
        points = int(row['Total Points']) if pd.notna(row['Total Points']) else 0
        
        color = '#FFD700' if rank == 1 else '#C0C0C0' if rank == 2 else '#CD7F32' if rank == 3 else '#4ECDC4'
        
        with st.container():
            st.markdown(f"""
            <div class="song-card" style="border-left-color: {color};">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                    <div style="flex: 1;">
                        <span style="font-size: 1.5rem; margin-right: 0.5rem;">{medal}</span>
                        <strong style="font-size: 1.1rem; color: white;">{row['Title']}</strong>
                        <br><span style="color: #888;">{row['Artist(s)']}</span>
                        <br><span style="color: #A855F7;">Submitted by {row['Name']}</span>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.8rem; font-weight: bold; color: {color};">{points}</div>
                        <div style="color: #888; font-size: 0.8rem;">points</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show comments if expanded
            comments = row.get('Comments', [])
            if isinstance(comments, list) and len(comments) > 0:
                with st.expander(f"💬 View {len(comments)} comments"):
                    for comment in comments:
                        if comment and str(comment).strip():
                            st.markdown(f'<div class="comment-bubble">"{comment}"</div>', unsafe_allow_html=True)

# Tab 3: Voting Analytics
with tab3:
    st.markdown("## 📈 Voting Analytics")
    
    avg_given, vote_dist, votes_with_names = get_voting_patterns(votes, competitors)
    
    # Generosity ranking
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 😇 Generosity Ranking")
        st.markdown("*Who gives the highest average votes?*")
        
        avg_sorted = avg_given.sort_values('Avg Points Given', ascending=False)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=avg_sorted['Avg Points Given'],
            y=avg_sorted['Name'],
            orientation='h',
            marker=dict(
                color=avg_sorted['Avg Points Given'],
                colorscale=[[0, '#FF6B6B'], [0.5, '#FFE66D'], [1, '#4ECDC4']],
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            text=avg_sorted['Avg Points Given'].round(2),
            textposition='outside',
            textfont=dict(color='white')
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Avg Points Given'),
            yaxis=dict(showgrid=False, autorange='reversed'),
            height=500,
            margin=dict(l=20, r=80, t=20, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Vote Distribution")
        st.markdown("*How do people spread their votes?*")
        
        # Create histogram of all votes
        fig = go.Figure()
        
        for name in votes_with_names['Voter Name'].unique()[:8]:  # Top 8 for readability
            voter_data = votes_with_names[votes_with_names['Voter Name'] == name]['Points Assigned']
            fig.add_trace(go.Violin(
                y=voter_data,
                name=name,
                box_visible=True,
                meanline_visible=True
            ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Points'),
            xaxis=dict(showgrid=False),
            height=500,
            showlegend=False,
            margin=dict(l=40, r=20, t=20, b=80)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Points given heatmap - who votes for whom
    st.markdown("### 🔥 Voting Relationships")
    st.markdown("*Who gives points to whom?*")
    
    # Create pivot table of voter -> submitter
    votes_merged = votes.merge(
        submissions[['Spotify URI', 'Submitter ID']], on='Spotify URI'
    ).merge(
        competitors.rename(columns={'ID': 'Voter ID', 'Name': 'Voter'}), on='Voter ID'
    ).merge(
        competitors.rename(columns={'ID': 'Submitter ID', 'Name': 'Submitter'}), on='Submitter ID'
    )
    
    pivot = votes_merged.pivot_table(
        values='Points Assigned',
        index='Voter',
        columns='Submitter',
        aggfunc='sum',
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[[0, '#FF6B6B'], [0.5, '#1A1A2E'], [1, '#4ECDC4']],
        zmid=0,
        text=pivot.values,
        texttemplate='%{text}',
        textfont=dict(size=10, color='white'),
        hoverongaps=False
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(title='Submitter', tickangle=45),
        yaxis=dict(title='Voter', autorange='reversed'),
        height=600,
        margin=dict(l=100, r=20, t=20, b=120)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Player Profiles
with tab4:
    st.markdown("## 👤 Player Profiles")
    
    selected_player = st.selectbox(
        "Select a player to view their profile",
        competitors['Name'].tolist()
    )
    
    player_id = competitors[competitors['Name'] == selected_player]['ID'].iloc[0]
    
    # Player's submissions
    player_submissions = submissions[submissions['Submitter ID'] == player_id]
    
    # Points received on their submissions
    player_song_uris = player_submissions['Spotify URI'].tolist()
    points_received = votes[votes['Spotify URI'].isin(player_song_uris)]
    total_points = points_received['Points Assigned'].sum()
    avg_points = points_received['Points Assigned'].mean() if len(points_received) > 0 else 0
    
    # Player's voting behavior
    player_votes = votes[votes['Voter ID'] == player_id]
    avg_vote_given = player_votes['Points Assigned'].mean() if len(player_votes) > 0 else 0
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Points", int(total_points))
    with col2:
        st.metric("Songs Submitted", len(player_submissions))
    with col3:
        st.metric("Avg Points/Song", f"{avg_points:.1f}")
    with col4:
        st.metric("Avg Vote Given", f"{avg_vote_given:.1f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 🎵 {selected_player}'s Submissions")
        
        for _, sub in player_submissions.iterrows():
            sub_votes = votes[votes['Spotify URI'] == sub['Spotify URI']]
            sub_points = sub_votes['Points Assigned'].sum()
            
            st.markdown(f"""
            <div class="song-card">
                <strong>{sub['Title']}</strong><br>
                <span style="color: #888;">{sub['Artist(s)']}</span><br>
                <span style="color: #4ECDC4; font-size: 1.2rem;">{int(sub_points)} pts</span>
            </div>
            """, unsafe_allow_html=True)
            
            if pd.notna(sub['Comment']) and str(sub['Comment']).strip():
                st.markdown(f"*\"{sub['Comment']}\"*")
    
    with col2:
        st.markdown(f"### 📊 Who Voted for {selected_player}?")
        
        if len(points_received) > 0:
            voter_breakdown = points_received.merge(
                competitors.rename(columns={'ID': 'Voter ID', 'Name': 'Voter'}),
                on='Voter ID'
            ).groupby('Voter')['Points Assigned'].sum().sort_values(ascending=True)
            
            colors = ['#FF6B6B' if v < 0 else '#4ECDC4' for v in voter_breakdown.values]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=voter_breakdown.values,
                y=voter_breakdown.index,
                orientation='h',
                marker=dict(color=colors)
            ))
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Points Given'),
                yaxis=dict(showgrid=False),
                height=400,
                margin=dict(l=20, r=20, t=20, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No votes received yet")

# Tab 5: Best Comments
with tab5:
    st.markdown("## 💬 Best Comments")
    st.markdown("*The hottest takes and spiciest opinions*")
    
    # Get all comments with context
    comments_df = votes[votes['Comment'].notna() & (votes['Comment'].str.strip() != '')].copy()
    comments_df = comments_df.merge(
        submissions[['Spotify URI', 'Title', 'Artist(s)']], on='Spotify URI'
    ).merge(
        competitors.rename(columns={'ID': 'Voter ID', 'Name': 'Voter'}), on='Voter ID'
    )
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        point_filter = st.selectbox(
            "Filter by vote type",
            ["All Comments", "Positive Votes (love)", "Negative Votes (shade)", "Max Points (5 pts)", "Min Points (negative)"]
        )
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Recent", "Highest Points", "Lowest Points"]
        )
    
    # Apply filters
    filtered = comments_df.copy()
    if point_filter == "Positive Votes (love)":
        filtered = filtered[filtered['Points Assigned'] > 0]
    elif point_filter == "Negative Votes (shade)":
        filtered = filtered[filtered['Points Assigned'] < 0]
    elif point_filter == "Max Points (5 pts)":
        filtered = filtered[filtered['Points Assigned'] == 5]
    elif point_filter == "Min Points (negative)":
        filtered = filtered[filtered['Points Assigned'] < 0]
    
    # Sort
    if sort_by == "Most Recent":
        filtered = filtered.sort_values('Created', ascending=False)
    elif sort_by == "Highest Points":
        filtered = filtered.sort_values('Points Assigned', ascending=False)
    else:
        filtered = filtered.sort_values('Points Assigned', ascending=True)
    
    # Display comments
    for _, row in filtered.head(30).iterrows():
        points = int(row['Points Assigned'])
        emoji = "❤️" if points >= 4 else "👍" if points > 0 else "👎" if points > -3 else "💀"
        color = "#4ECDC4" if points > 0 else "#FF6B6B"
        
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border-radius: 16px; padding: 1.25rem; margin: 0.75rem 0; border-left: 4px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.5rem;">
                <div style="flex: 1;">
                    <span style="font-size: 1.5rem;">{emoji}</span>
                    <strong style="color: #A855F7;">{row['Voter']}</strong>
                    <span style="color: #888;"> on </span>
                    <strong style="color: white;">{row['Title']}</strong>
                    <span style="color: #888;"> by {row['Artist(s)']}</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: bold; color: {color};">{points:+d}</div>
            </div>
            <p style="margin: 0.75rem 0 0 0; color: #ddd; font-style: italic;">"{row['Comment']}"</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>Built for music lovers who take friendly competition very seriously 🎵</p>
</div>
""", unsafe_allow_html=True)

