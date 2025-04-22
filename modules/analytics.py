import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from utils.i18n import get_text

def analytics_page(lang: str):
    st.title(get_text(lang, "analytics_title"))
    
    try:
        df = load_data(lang)
        if df.empty:
            st.warning(get_text(lang, "empty_db_warning"))
            return
    except Exception as e:
        st.error(get_text(lang, "critical_error").format(error=str(e)))
        return

    filtered_df = configure_filters(lang, df)
    show_kpis(lang, filtered_df)
    generate_spatial_section(lang, filtered_df)
    generate_temporal_section(lang, filtered_df)
    generate_effectiveness_section(lang, filtered_df)
    setup_download(lang, filtered_df)
    show_body_part_ranking(lang, filtered_df)

def load_data(lang: str):
    # Load data from GitHub
    url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
    df = pd.read_csv(url)
    
    # Rename columns
    df = df.rename(columns={
        'jornada': 'Round',
        'fecha': 'Date',          # Antes: 'Fecha'
        'rival': 'Opponent',      # Antes: 'Rival'
        'condición': 'Condition', # Antes: 'Condición'
        'periodo': 'Period',      # Antes: 'Periodo'
        'minuto': 'Minute',       # Antes: 'Minuto'
        'acción': 'Action',       # Antes: 'Acción'
        'equipo': 'Team',         # Antes: 'Equipo'
        'ejecutor': 'Executor',   # Antes: 'Ejecutor'
        'zona_saque': 'StartZone',# Antes: 'Zona Saque'
        'zona_remate': 'EndZone', # Antes: 'Zona Remate'
        'gol': 'Goal',            # Antes: 'Gol'
        'resultado': 'Result',    # Antes: 'Resultado'
        'parte_cuerpo': 'BodyPart'# Antes: 'Parte Cuerpo'
    })
    
    # Date processing
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    
    # Translate key values
    df['Goal'] = df['Goal'].map({'Sí': get_text(lang, 'yes'), 'No': get_text(lang, 'no')})
    
    # Action mapping
    action_translation = {
        'Córner': 'corner',
        'Tiro libre': 'free_kick',
        'Lateral': 'throw_in',
        'Penal': 'penalty',
        'Centro': 'cross',
        'Remate': 'shot'
    }
    df['Action'] = df['Action'].map(action_translation).apply(lambda x: get_text(lang, x))
    
    # Validation
    required_columns = ['Round', 'Opponent', 'Period', 'Minute', 'Action', 'Team', 'Date']
    if not all(col in df.columns for col in required_columns):
        return pd.DataFrame()
    
    return df.dropna(subset=['StartZone', 'EndZone', 'Executor'])

def configure_filters(lang: str, df):
    with st.sidebar:
        st.header(get_text(lang, "advanced_filters"))
        
        # Date formatting
        df = df.sort_values('Date', ascending=False)
        df['Date_str'] = df['Date'].dt.strftime('%d %b')
        df['Match'] = df.apply(
            lambda x: f"{x['Date_str']} vs {x['Opponent']}", 
            axis=1
        )
        
        # Widget keys
        widget_keys = {
            'matches': f"{lang}_matches",
            'rounds': f"{lang}_rounds",
            'conditions': f"{lang}_conditions",
            'actions': f"{lang}_actions",
            'players': f"{lang}_players",
            'minutes': f"{lang}_minutes"
        }
        
        # Interactive filters
        selected_matches = st.multiselect(
            get_text(lang, "select_matches"),
            options=df['Match'].unique(),
            default=st.session_state.get(widget_keys['matches'], df['Match'].unique()),
            key=widget_keys['matches']
        )
        
        col1, col2 = st.columns(2)
        with col1:
            rounds = st.multiselect(
                get_text(lang, "round"),
                options=df['Round'].unique(),
                default=st.session_state.get(widget_keys['rounds'], df['Round'].unique()),
                key=widget_keys['rounds']
            )
        with col2:
            conditions = st.multiselect(
                get_text(lang, "condition"),
                options=df['Condition'].unique(),
                default=st.session_state.get(widget_keys['conditions'], df['Condition'].unique()),
                format_func=lambda x: get_text(lang, f"condition_{x}"),
                key=widget_keys['conditions']
            )

        col3, col4 = st.columns(2)
        with col3:
            actions = st.multiselect(
                get_text(lang, "actions"),
                options=df['Action'].unique(),
                default=st.session_state.get(widget_keys['actions'], df['Action'].unique()),
                key=widget_keys['actions']
            )
        with col4:
            players = st.multiselect(
                get_text(lang, "players"),
                options=df['Executor'].unique(),
                default=st.session_state.get(widget_keys['players'], df['Executor'].unique()),
                key=widget_keys['players']
            )

        min_min, max_min = int(df['Minute'].min()), int(df['Minute'].max())
        minute_range = st.slider(
            get_text(lang, "minutes"),
            min_min, max_min,
            value=st.session_state.get(widget_keys['minutes'], (min_min, max_min)),
            key=widget_keys['minutes']
        )
        
    return df[
        (df['Match'].isin(selected_matches)) &
        (df['Round'].isin(rounds)) &
        (df['Condition'].isin(conditions)) &
        (df['Action'].isin(actions)) &
        (df['Executor'].isin(players)) &
        (df['Minute'].between(*minute_range))
    ]

def show_kpis(lang: str, df):
    cols = st.columns(5)
    
    with cols[0]:
        st.metric(get_text(lang, "registered_actions"), df.shape[0])
    
    goals_for = df[(df['Goal'] == get_text(lang, 'yes')) & (df['Team'] == 'Cavalry FC')].shape[0]
    with cols[1]:
        st.metric(get_text(lang, "goals_for"), goals_for)
    
    goals_against = df[(df['Goal'] == get_text(lang, 'yes')) & (df['Team'] != 'Cavalry FC')].shape[0]
    with cols[2]:
        st.metric(get_text(lang, "goals_against"), goals_against)
    
    attack_eff = (goals_for / df.shape[0] * 100) if df.shape[0] > 0 else 0
    with cols[3]:
        st.metric(get_text(lang, "offensive_effectiveness"), f"{attack_eff:.1f}%")
    
    defense_eff = 100 - (goals_against / df.shape[0] * 100) if df.shape[0] > 0 else 0
    with cols[4]:
        st.metric(get_text(lang, "defensive_effectiveness"), f"{defense_eff:.1f}%")

def generate_spatial_section(lang: str, df):
    st.header(get_text(lang, "tactical_mapping"))
    col1, col2 = st.columns(2)
    
    with col1:
        generate_heatmap(lang, df, zone_type='start')
    with col2:
        generate_heatmap(lang, df, zone_type='end')

def generate_heatmap(lang: str, df, zone_type='start'):
    zone_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }
    
    coord_col = 'StartZone' if zone_type == 'start' else 'EndZone'
    
    temp_df = df.copy()
    temp_df[coord_col] = temp_df[coord_col].apply(
        lambda x: int(x) if str(x).isdigit() else x
    )
    coord_df = temp_df[coord_col].map(zone_coords).dropna().apply(pd.Series)
    
    if coord_df.empty:
        st.warning(get_text(lang, "no_data_warning").format(tipo=get_text(lang, zone_type)))
        return
    
    coord_df.columns = ['x', 'y']
    
    pitch = VerticalPitch(
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white',
        linewidth=1.2,
        half=True,
        goal_type='box'
    )
    
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch.draw(ax=ax)
    
    pitch.kdeplot(
        coord_df['x'], coord_df['y'],
        ax=ax,
        cmap='Greens' if zone_type == 'start' else 'Reds',
        levels=100,
        fill=True,
        alpha=0.75,
        bw_adjust=0.65,
        zorder=2
    )
    
    ax.set_title(get_text(lang, "density_title").format(tipo=get_text(lang, zone_type)), 
                fontsize=16, 
                pad=20,
                fontweight='bold')
    
    st.pyplot(fig)
    plt.close()

def generate_temporal_section(lang: str, df):
    st.header(get_text(lang, "temporal_evolution"))
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            df, 
            x='Round', 
            color='Period',
            title=get_text(lang, "actions_by_round"),
            labels={'count': get_text(lang, "actions")}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        fig = px.box(
            df, 
            x='Action', 
            y='Minute',
            color='Team', 
            title=get_text(lang, "time_distribution"),
            points="all"
        )
        st.plotly_chart(fig, use_container_width=True)

def generate_effectiveness_section(lang: str, df):
    st.header(get_text(lang, "effectiveness_section"))
    col1, col2 = st.columns(2)
    
    with col1:
        effectiveness_df = df.groupby('Executor').agg(
            Actions=('Executor', 'count'),
            Goals=('Goal', lambda x: (x == get_text(lang, 'yes')).sum())
        ).reset_index()

        fig = px.scatter(
            effectiveness_df, 
            x='Actions', 
            y='Goals',
            size='Goals', 
            color='Executor',
            title=get_text(lang, "actions_goals_relation")
        )
        fig.update_traces(marker=dict(line=dict(width=1, color='black')))
        fig.update_layout(plot_bgcolor='#F9F9F9', paper_bgcolor='#F9F9F9')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        sunburst_df = df.groupby(['Action', 'Result']).size().reset_index(name='Count')
        sunburst_df = sunburst_df[sunburst_df['Result'].notna()]

        total = sunburst_df['Count'].sum()
        sunburst_df['Percentage'] = sunburst_df['Count'] / total * 100

        action_df = sunburst_df.groupby('Action')['Count'].sum().reset_index()
        action_df['Result'] = get_text(lang, "total")
        action_df['Percentage'] = action_df['Count'] / total * 100

        combined_df = pd.concat([sunburst_df, action_df], ignore_index=True)
        combined_df['Percentage'] = combined_df['Percentage'].fillna(0)

        fig = px.sunburst(
            combined_df,
            path=['Action', 'Result'],
            values='Count',
            title=get_text(lang, "results_composition"),
            branchvalues='total',
            custom_data=['Count', 'Percentage']
        )
        fig.update_traces(
            hovertemplate=f'<b>%{{label}}</b><br>{get_text(lang, "quantity")}: %{{customdata[0]}}<br>{get_text(lang, "percentage")}: %{{customdata[1]:.1f}}%<extra></extra>'
        )
        st.plotly_chart(fig, use_container_width=True)

def show_body_part_ranking(lang: str, df):
    st.header(get_text(lang, "body_part_ranking"))
    
    # Define offensive actions
    OFFENSIVE_ACTIONS = [
        get_text(lang, "corner"),
        get_text(lang, "free_kick"),
        get_text(lang, "throw_in"),
        get_text(lang, "penalty"),
        get_text(lang, "cross"),
        get_text(lang, "shot")
    ]
    
    df['ActionType'] = df['Action'].apply(
        lambda x: get_text(lang, "offensive") if x in OFFENSIVE_ACTIONS else get_text(lang, "defensive")
    )

    color_map = {
        get_text(lang, "head"): '#00C2A0',
        get_text(lang, "leg"): '#FF5A5F',
        get_text(lang, "other"): '#4B4B4B'
    }

    for action_type in [get_text(lang, "offensive"), get_text(lang, "defensive")]:
        type_df = df[(df['ActionType'] == action_type) & (df['BodyPart'].notna())]
        ranking_df = type_df.groupby(['Executor', 'BodyPart']).size().reset_index(name='Count')
        
        total_players = ranking_df.groupby('Executor')['Count'].sum().sort_values(ascending=False)
        ranking_df['Executor'] = pd.Categorical(
            ranking_df['Executor'], 
            categories=total_players.index, 
            ordered=True
        )

        st.subheader(f"{'⚔️' if action_type == get_text(lang, "offensive") else '🛡️'} {action_type} {get_text(lang, "actions")}")

        fig = px.bar(
            ranking_df,
            x='Count',
            y='Executor',
            color='BodyPart',
            orientation='h',
            text='Count',
            title=get_text(lang, "players_actions_by_body").format(tipo=action_type),
            labels={'Count': get_text(lang, "actions"), 'Executor': get_text(lang, "player")},
            color_discrete_map=color_map,
            category_orders={'Executor': total_players.index.tolist()}
        )
        fig.update_layout(barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

def setup_download(lang: str, df):
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        get_text(lang, "export_data"),
        data=csv,
        file_name="tactical_analysis.csv",
        mime="text/csv",
        help=get_text(lang, "export_data_help")
    )

    # Footer
    st.markdown(
        """
        <hr style='margin-top: 40px; margin-bottom: 10px'>
        <div style='text-align: center; font-size: 14px; color: gray;'>
            <strong>Felipe Ormazabal</strong><br>Soccer Scout - Data Analyst
        </div>
        """,
        unsafe_allow_html=True
    )
