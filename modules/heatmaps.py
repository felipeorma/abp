import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from utils.i18n import get_text  # Asegúrate de importar tu utilidad de traducción

def heatmaps_page(lang="es"):
    # Estilos CSS (sin cambios)
    st.markdown("""
        <style>
            /* Mantener los mismos estilos CSS */
        </style>
    """, unsafe_allow_html=True)

    st.title("⚽ Cavalry FC - Player Heatmap Match Dashboard")

    @st.cache_data
    def load_data():
        # Ajustar path si es necesario (ej: "../matches.csv")
        return pd.read_csv("matches.csv").pipe(process_data)
    
    def process_data(df):
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.sort_values("Date", ascending=False)
        df["Team"] = df["Team"].apply(
            lambda x: "Cavalry" if str(x).strip().lower() == "cavalry" else "Opponent")
        return df.fillna(0)

    df = load_data()
    df["Round"] = df["Round"].astype(str)

    # Contenedor para filtros en el área principal
    with st.container():
        st.subheader(get_text(lang, "filters_header"))
        
        cols = st.columns([2, 2, 2, 2, 2, 2])
        with cols[0]:
            team_view = st.radio(
                get_text(lang, "show_players_from"), 
                ["Cavalry", "Opponent"],
                index=0
            )
        with cols[1]:
            round_filter = st.selectbox(
                get_text(lang, "match_round"),
                ["All"] + sorted(df["Round"].unique().tolist())
            )
        with cols[2]:
            side_filter = st.selectbox(
                get_text(lang, "team_side"),
                ["All"] + sorted(df["Local/Visit"].astype(str).unique().tolist())
            )
        with cols[3]:
            opponent_filter = st.selectbox(
                get_text(lang, "opponent"),
                ["All"] + sorted(df["Cavalry/Opponent"].astype(str).unique().tolist())
            )
        with cols[4]:
            player_filter = st.selectbox(
                get_text(lang, "player"),
                ["All"] + sorted(df["Player"].astype(str).unique().tolist())
            )
        with cols[5]:
            date_filter = st.selectbox(
                get_text(lang, "match_date"),
                ["All"] + sorted(df["Date"].dt.date.astype(str).unique().tolist())
            )

    # Filtrado de datos (sin cambios)
    df_filtered = df[df["Player"].astype(str) != "0"].copy()
    # ... (resto del filtrado)

    # Sección de jugadores (sin cambios)
    st.subheader(get_text(lang, "players_header"))
    df_filtered = df_filtered.sort_values(by="Position", key=lambda x: x.apply(get_position_order))
    
    # Mostrar jugadores en columnas
    cols = st.columns(6)
    for idx, player_name in enumerate(players_list):
        with cols[idx % 6]:
            # Usar una tarjeta clickeable en lugar de botón
            if st.markdown(generate_player_card(player_data), unsafe_allow_html=True):
                st.session_state.selected_player = player_name

    # Manejo de heatmaps (sin cambios)
    if st.session_state.get("selected_player"):
        display_heatmaps(st.session_state.selected_player, df)

def generate_player_card(player_data):
    """Genera HTML para la tarjeta de jugador"""
    return f"""
    <div class='player-card' onclick="this.closest('.element-container').dispatchEvent(new CustomEvent('cardClick'))">
        <img src="{player_data['Photo']}" class="player-img">
        <div class='player-info'>
            <strong>{player_data['Player']}</strong><br>
            <span>{get_team_label(player_data)}</span><br>
            <span class='position-badge {get_position_group(player_data["Position"])}'>
                {player_data["Position"]}
            </span>
        </div>
    </div>
    """

def display_heatmaps(player_name, df):
    """Muestra los heatmaps del jugador seleccionado"""
    st.divider()
    st.markdown(f"## 🔥 Heatmaps - {player_name}")
    
    df_player = df[df["Player"] == player_name].sort_values("Date", ascending=False)
    
    for _, row in df_player.iterrows():
        with st.expander(f"🗓️ {row['Date'].date()} - Round {row['Round']}"):
            col1, col2 = st.columns([1, 3])
            with col1:
                display_match_stats(row)
            with col2:
                display_heatmap_image(row["heatmap"])

def display_match_stats(row):
    """Muestra las estadísticas del partido"""
    position = str(row.get("Position", "")).strip().upper()
    
    stats = {
        "Minutes": row['Minutes played'],
        "Position": position,
        "Opponent": row['Cavalry/Opponent']
    }
    
    if position == "GK":
        stats.update({
            "Saves": row['Saves'],
            "Goals Against": row['Goal Against']
        })
    else:
        stats.update({
            "Goals": row['Goals'],
            "Assists": row['Assists']
        })
    
    st.json(stats)

def display_heatmap_image(url):
    """Muestra el heatmap desde la URL"""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        st.image(image, use_column_width=True)
    except Exception as e:
        st.error(f"Error loading heatmap: {str(e)}")

# Footer internacionalizado
st.markdown(f"""
    ---
    <div class='footer'>
        {get_text(lang, "created_by")}<br>
        {get_text(lang, "footer_roles")}
    </div>
""", unsafe_allow_html=True)

