import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from utils.i18n import get_text  # Asegúrate de tener esta utilidad

def heatmaps_page(lang="es"):
    # Configuración de estilos y título
    st.markdown("""
    <style>
        .main { background-color: #f9f9f9; }
        .player-card {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0.5rem auto;
            padding: 0.5rem;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            width: 100%;
            text-align: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .player-card:hover {
            transform: scale(1.03);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .opponent-card {
            background-color: #f3f3f3 !important;
        }
        .player-img {
            border-radius: 50%;
            width: 70px;
            height: 70px;
            object-fit: cover;
            margin: auto;
        }
        .player-info {
            text-align: center;
            margin-top: 0.3rem;
            font-size: 0.8rem;
        }
        .position-badge {
            display: inline-block;
            padding: 0.25em 0.6em;
            font-size: 0.7em;
            font-weight: bold;
            border-radius: 0.5rem;
            color: white;
        }
        .GK { background-color: #28a745; }
        .DF { background-color: #007bff; }
        .DMF { background-color: #17a2b8; }
        .MF { background-color: #ffc107; color: black; }
        .FW { background-color: #dc3545; }
        .N_A { background-color: #6c757d; }
        .footer {
            margin-top: 3rem;
            padding: 1rem;
            text-align: center;
            font-size: 1rem;
            color: gray;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("⚽ " + get_text(lang, "heatmap_title"))

    # Carga de datos
    @st.cache_data
    def load_data():
        df = pd.read_csv("matches.csv")
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df["Team"] = df["Team"].apply(lambda x: "Cavalry" if str(x).strip().lower() == "cavalry" else "Opponent")
        return df.fillna(0)
    
    df = load_data()
    df["Round"] = df["Round"].astype(str)

    # Filtros en el área principal
    with st.container():
        cols = st.columns(5)
        with cols[0]:
            team_view = st.radio(get_text(lang, "show_players_from"), ["Cavalry", "Opponent"], index=0)
        with cols[1]:
            round_filter = st.selectbox(get_text(lang, "match_round"), ["All"] + sorted(df["Round"].unique().tolist()))
        with cols[2]:
            side_filter = st.selectbox(get_text(lang, "team_side"), ["All"] + sorted(df["Local/Visit"].astype(str).unique().tolist()))
        with cols[3]:
            opponent_filter = st.selectbox(get_text(lang, "opponent"), ["All"] + sorted(df["Cavalry/Opponent"].astype(str).unique().tolist()))
        with cols[4]:
            date_filter = st.selectbox(get_text(lang, "match_date"), ["All"] + sorted(df["Date"].dt.date.astype(str).unique().tolist()))

    # Aplicar filtros
    df_filtered = df[df["Player"].astype(str) != "0"].copy()
    df_filtered = df_filtered[df_filtered["Team"] == team_view]
    
    filter_mapping = [
        (round_filter, "Round"),
        (side_filter, "Local/Visit"),
        (opponent_filter, "Cavalry/Opponent"),
        (date_filter, "Date")
    ]
    
    for filter_value, column in filter_mapping:
        if filter_value != "All":
            if column == "Date":
                df_filtered = df_filtered[df_filtered[column].dt.date.astype(str) == filter_value]
            else:
                df_filtered = df_filtered[df_filtered[column] == filter_value]

    # Mostrar jugadores
    st.subheader(get_text(lang, "players_header"))
    df_filtered = df_filtered.sort_values(by="Position", key=lambda x: x.apply(get_position_order))
    players_list = df_filtered["Player"].unique()
    
    cols = st.columns(6)
    for idx, player_name in enumerate(players_list):
        player_data = df_filtered[df_filtered["Player"] == player_name].iloc[0]
        with cols[idx % 6]:
            try:
                st.markdown("<div class='player-card'>", unsafe_allow_html=True)
                if player_data["Team"] == "Cavalry":
                    response = requests.get(player_data["Photo"], headers={"User-Agent": "Mozilla/5.0"})
                    image = Image.open(BytesIO(response.content))
                    st.image(image, width=70, use_container_width=False)
                pos_group = get_position_group(player_data["Position"])
                team_label = player_data['Team'] if player_data['Team'] == 'Cavalry' else f"{get_text(lang, 'opponent')} ({player_data['Cavalry/Opponent']})"
                st.markdown(f"<div class='player-info'><strong>{player_name}</strong><br><span>{team_label}</span><br><span class='position-badge {pos_group}'>{player_data['Position']}</span></div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(get_text(lang, "image_error"))
            if st.button(f"{get_text(lang, 'show_heatmaps')} - {player_name}", key=f"btn_{player_name}"):
                st.session_state.selected_player = player_name

    # Mostrar heatmaps
    if "selected_player" in st.session_state and st.session_state.selected_player:
        st.divider()
        st.markdown(f"## 🔥 {get_text(lang, 'heatmaps_for')} {st.session_state.selected_player}")
        df_player = df[df["Player"] == st.session_state.selected_player].sort_values("Date", ascending=False)
        
        for _, row in df_player.iterrows():
            with st.expander(f"📅 {row['Date'].date()} - {row['Cavalry/Opponent']}"):
                col1, col2 = st.columns([1, 3])
                with col1:
                    position = str(row.get("Position", "")).strip().upper()
                    stats = {
                        get_text(lang, 'minutes"): row['Minutes played'],
                        get_text(lang, 'goals"): row['Goals'],
                        get_text(lang, 'assists"): row['Assists']
                    }
                    if position == "GK":
                        stats.update({
                            get_text(lang, 'saves"): row['Saves'],
                            get_text(lang, 'goals_against"): row['Goal Against']
                        })
                    st.json(stats)
                with col2:
                    try:
                        response = requests.get(row["heatmap"], headers={"User-Agent": "Mozilla/5.0"})
                        image = Image.open(BytesIO(response.content))
                        st.image(image, use_column_width=True)
                    except:
                        st.error(get_text(lang, "heatmap_error"))

    # Footer internacionalizado
    st.markdown(f"""
    ---
    <div class='footer'>
        {get_text(lang, "created_by")}<br>
        {get_text(lang, "footer_roles")}
    </div>
    """, unsafe_allow_html=True)

# Funciones de utilidad
def get_position_order(pos):
    pos = str(pos).upper()
    order = {
        "GK": 0,
        "DF": 1, "RB": 1, "LB": 1,
        "DMF": 2,
        "MF": 3, "AMF": 3, "CMF": 3,
        "RW": 4, "LW": 4,
        "FW": 5, "CF": 5
    }
    return order.get(pos, 99)

def get_position_group(pos):
    pos = str(pos).upper()
    if pos == "GK": return "GK"
    if pos == "DMF": return "DMF"
    if pos.startswith("D"): return "DF"
    if pos.startswith("M"): return "MF"
    if pos.startswith("F") or pos.endswith(("W", "CF")): return "FW"
    return "N_A"
