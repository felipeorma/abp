import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from utils.i18n import get_text

def heatmaps_page(lang="es"):
    # Configurar CSS y título
    st.markdown("""
    <style>
        .player-card {
            transition: transform 0.2s;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .player-card:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .heatmap-img {
            border: 2px solid #e0e0e0;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🔥 " + get_text(lang, "heatmap_title"))

    # Cargar datos
    @st.cache_data
    def load_data():
        df = pd.read_csv("matches.csv")
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df["Team"] = df["Team"].apply(lambda x: "Cavalry" if str(x).lower().strip() == "cavalry" else "Opponent")
        return df
    
    df = load_data()

    # Filtros en el área principal
    with st.container():
        cols = st.columns(3)
        with cols[0]:
            team_filter = st.radio(
                get_text(lang, "show_players_from"),
                ["Cavalry", "Opponent"],
                horizontal=True
            )
        with cols[1]:
            player_filter = st.selectbox(
                get_text(lang, "select_player"),
                ["All"] + sorted(df["Player"].unique())
            )
        with cols[2]:
            date_filter = st.selectbox(
                get_text(lang, "select_date"),
                ["All"] + sorted(df["Date"].dt.strftime("%Y-%m-%d").unique())
            )

    # Aplicar filtros
    filtered_df = df[df["Team"] == team_filter]
    if player_filter != "All":
        filtered_df = filtered_df[filtered_df["Player"] == player_filter]
    if date_filter != "All":
        filtered_df = filtered_df[filtered_df["Date"].dt.strftime("%Y-%m-%d") == date_filter]

    # Mostrar jugadores
    st.subheader(get_text(lang, "players_list"))
    player_cols = st.columns(4)
    
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        with player_cols[idx % 4]:
            render_player_card(row, lang)

    # Manejar heatmaps
    if "selected_player" in st.session_state:
        render_heatmaps(st.session_state.selected_player, df, lang)

def render_player_card(row, lang):
    card = st.container()
    with card:
        try:
            response = requests.get(row["Photo"], headers={"User-Agent": "Mozilla/5.0"})
            img = Image.open(BytesIO(response.content))
            st.image(img, caption=row["Player"], width=120)
        except:
            st.error(get_text(lang, "image_error"))
        
        st.markdown(f"""
        <div class='player-card'>
            <h4>{row['Player']}</h4>
            <p><strong>{get_text(lang, 'position')}:</strong> {row['Position']}</p>
            <p><strong>{get_text(lang, 'team')}:</strong> {row['Team']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(get_text(lang, "view_heatmap") + f" {row['Player']}", key=f"heatmap_{row['Player']}"):
            st.session_state.selected_player = row["Player"]

def render_heatmaps(player, df, lang):
    st.divider()
    st.subheader(f"🔥 {get_text(lang, 'heatmaps_for')} {player}")
    
    player_data = df[df["Player"] == player].sort_values("Date", ascending=False)
    
    for _, match in player_data.iterrows():
        with st.expander(f"📅 {match['Date'].date()} vs {match['Cavalry/Opponent']}"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.write(f"**{get_text(lang, 'match_stats')}:**")
                stats = {
                    get_text(lang, 'minutes"): match["Minutes played"],
                    get_text(lang, 'goals"): match["Goals"],
                    get_text(lang, 'assists"): match["Assists"]
                }
                st.json(stats)
            
            with col2:
                try:
                    response = requests.get(match["heatmap"], headers={"User-Agent": "Mozilla/5.0"})
                    img = Image.open(BytesIO(response.content))
                    st.image(img, use_column_width=True, caption=get_text(lang, "heatmap"))
                except:
                    st.error(get_text(lang, "heatmap_error"))

