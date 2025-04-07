import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

def heatmaps_page():
    # Configuración de página y estilos
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
            .filter-container {
                background-color: #ffffff;
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("⚽ Cavalry FC - Player Heatmap Match Dashboard")

    @st.cache_data
    def load_data():
        df = pd.read_csv("matches.csv")
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.sort_values("Date", ascending=False)
        df["Team"] = df["Team"].apply(lambda x: "Cavalry" if str(x).strip().lower() == "cavalry" else "Opponent")
        return df.fillna(0)

    df = load_data()
    df["Round"] = df["Round"].astype(str)

    # Filtros
    with st.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.header("🔎 Filters")
        
        cols = st.columns([2, 2, 2, 2, 2, 2])
        with cols[0]:
            team_view = st.radio("👥 Show Players From:", ["Cavalry", "Opponent"], index=0)
        with cols[1]:
            player_filter = st.selectbox("Player", ["All"] + sorted(df["Player"].astype(str).unique().tolist()))
        with cols[2]:
            round_filter = st.selectbox("Match Round", ["All"] + sorted(df["Round"].unique().tolist()))
        with cols[3]:
            side_filter = st.selectbox("Team Side", ["All"] + sorted(df["Local/Visit"].astype(str).unique().tolist()))
        with cols[4]:
            opponent_filter = st.selectbox("Opponent", ["All"] + sorted(df["Cavalry/Opponent"].astype(str).unique().tolist()))
        with cols[5]:
            date_filter = st.selectbox("Match Date", ["All"] + sorted(df["Date"].dt.date.astype(str).unique().tolist()))
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Aplicar filtros
    df_filtered = df[df["Player"].astype(str) != "0"].copy()
    df_filtered = df_filtered[df_filtered["Team"] == team_view]
    
    filter_config = [
        (round_filter, "Round"),
        (side_filter, "Local/Visit"),
        (opponent_filter, "Cavalry/Opponent"),
        (date_filter, "Date"),
        (player_filter, "Player")
    ]
    
    for value, col in filter_config:
        if value != "All":
            if col == "Date":
                df_filtered = df_filtered[df_filtered[col].dt.date.astype(str) == value]
            else:
                df_filtered = df_filtered[df_filtered[col] == value]

    # Mostrar jugadores
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

    st.subheader("🧍 Players")
    df_filtered = df_filtered.sort_values(by="Position", key=lambda x: x.apply(get_position_order))
    players_list = df_filtered["Player"].unique()
    
    cols = st.columns(6)
    for idx, player_name in enumerate(players_list):
        player_data = df_filtered[df_filtered["Player"] == player_name].iloc[0]
        with cols[idx % 6]:
            try:
                st.markdown("<div class='player-card'>", unsafe_allow_html=True)
                if player_data["Team"] == "Cavalry":
                    st.image(player_data["Photo"], width=70, use_column_width=False)
                pos_group = get_position_group(player_data["Position"])
                team_label = player_data['Team'] if player_data['Team'] == 'Cavalry' else f"Opponent ({player_data['Cavalry/Opponent']})"
                st.markdown(
                    f"<div class='player-info'>"
                    f"<strong>{player_name}</strong><br>"
                    f"<span>{team_label}</span><br>"
                    f"<span class='position-badge {pos_group}'>{player_data['Position']}</span>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"Image not found: {str(e)}")
                
            if st.button(f"Show Heatmaps - {player_name}", key=f"btn_{player_name}"):
                st.session_state.selected_player = player_name

    # Mostrar heatmaps
    if "selected_player" in st.session_state and st.session_state.selected_player:
        st.divider()
        st.markdown(f"## 🔥 Heatmaps - {st.session_state.selected_player}")
        df_player = df[df["Player"] == st.session_state.selected_player].sort_values("Date", ascending=False)
        
        for _, row in df_player.iterrows():
            with st.expander(f"Round {row['Round']} - {row['Date'].date()}"):
                col1, col2 = st.columns([1, 3])
                with col1:
                    position = str(row.get("Position", "")).strip().upper()
                    stats = {
                        "Minutes": row['Minutes played'],
                        "Goals": row.get('Goals', 'N/A'),
                        "Assists": row.get('Assists', 'N/A')
                    }
                    if position == "GK":
                        stats.update({
                            "Saves": row.get('Saves', 'N/A'),
                            "Goals Against": row.get('Goal Against', 'N/A')
                        })
                    st.json(stats)
                with col2:
                    try:
                        st.image(row["heatmap"], width=300)
                    except:
                        st.warning(f"Could not load heatmap for Round {row['Round']}")

    # Footer
    st.markdown("""
    ---
    <div class='footer'>
        Created by Felipe Ormazabal<br>
        Soccer Scout & Data Analyst
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    heatmaps_page()
