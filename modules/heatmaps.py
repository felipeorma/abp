import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from utils.i18n import get_text

def heatmaps_page(lang="es"):
    # Configuración inicial
    st.session_state.setdefault("selected_player", None)
    apply_custom_styles()
    
    # Título y carga de datos
    st.title("⚽ " + get_text(lang, "heatmap_title"))
    df = load_data()
    
    # Controles de filtrado
    filters = render_filters(df, lang)
    
    # Aplicar filtros
    filtered_df = apply_filters(df, filters)
    
    # Mostrar jugadores
    render_players(filtered_df, lang)
    
    # Mostrar heatmaps si hay selección
    if st.session_state.selected_player:
        render_heatmaps(st.session_state.selected_player, df, lang)

def apply_custom_styles():
    st.markdown("""
    <style>
        .player-card {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem;
            transition: transform 0.2s;
        }
        .player-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .player-img {
            border-radius: 50%;
            width: 100px;
            height: 100px;
            object-fit: cover;
        }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    @st.cache_data
    def fetch_data():
        df = pd.read_csv("matches.csv")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Team"] = df["Team"].apply(lambda x: "Cavalry" if str(x).lower().strip() == "cavalry" else "Opponent")
        return df.dropna(subset=["Player"])
    return fetch_data()

def render_filters(df, lang):
    cols = st.columns(3)
    filters = {}
    
    with cols[0]:
        filters["team"] = st.radio(
            get_text(lang, "team_filter"),
            ["Cavalry", "Opponent"]
        )
    
    with cols[1]:
        filters["player"] = st.selectbox(
            get_text(lang, "player_filter"),
            ["All"] + sorted(df["Player"].unique())
        )
    
    with cols[2]:
        filters["date"] = st.selectbox(
            get_text(lang, "date_filter"),
            ["All"] + sorted(df["Date"].dt.strftime("%Y-%m-%d").unique())
        )
    
    return filters

def apply_filters(df, filters):
    filtered = df[df["Team"] == filters["team"]]
    
    if filters["player"] != "All":
        filtered = filtered[filtered["Player"] == filters["player"]]
    
    if filters["date"] != "All":
        filtered = filtered[filtered["Date"].dt.strftime("%Y-%m-%d") == filters["date"]]
    
    return filtered

def render_players(df, lang):
    st.subheader(get_text(lang, "players_header"))
    cols = st.columns(4)
    
    for idx, (_, row) in enumerate(df.iterrows()):
        with cols[idx % 4]:
            render_player_card(row, lang)

def render_player_card(row, lang):
    card = st.container()
    with card:
        try:
            response = requests.get(row["Photo"], headers={"User-Agent": "Mozilla/5.0"})
            img = Image.open(BytesIO(response.content))
            st.image(img, use_column_width=True, caption=row["Player"])
        except:
            st.error(get_text(lang, "image_error"))
        
        st.markdown(f"""
        <div class='player-card'>
            <h4>{row['Player']}</h4>
            <p>Position: <strong>{row['Position']}</strong></p>
            <p>Team: {row['Team']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(get_text(lang, "view_heatmap") + f" {row['Player']}", key=f"btn_{row['Player']}"):
            st.session_state.selected_player = row["Player"]

def render_heatmaps(player, df, lang):
    st.subheader(f"🔥 {get_text(lang, 'heatmaps_for')} {player}")
    player_data = df[df["Player"] == player]
    
    for _, match in player_data.iterrows():
        with st.expander(f"🗓️ {match['Date'].date()} - {match['Cavalry/Opponent']}"):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.write(f"**{get_text(lang, 'stats')}:**")
                st.json({
                    "Minutes": match["Minutes played"],
                    "Goals": match["Goals"],
                    "Assists": match["Assists"]
                })
            
            with col2:
                try:
                    response = requests.get(match["heatmap"], headers={"User-Agent": "Mozilla/5.0"})
                    img = Image.open(BytesIO(response.content))
                    st.image(img, use_column_width=True)
                except:
                    st.error(get_text(lang, "heatmap_load_error"))
