import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def evolucion_page(lang):
    st.markdown("<h1 style='text-align: center;'>📈 PPDA Evolution by Round</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; color: gray;'>Analyze pressure intensity trends between past and current seasons</p>", unsafe_allow_html=True)

    # Load data
    try:
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
        df_2025 = pd.read_excel("Cavalry2025stats.xlsx")
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")
        return

    # ========== CORRECCIONES CLAVE ==========
    # 1. Validación mejorada de columnas
    required_cols = {
        "Round": "categorical",
        "Match": "categorical",
        "PPDA": "numeric",
        "PPDA 1st Half": "numeric",
        "PPDA 2nd Half": "numeric"
    }

    for df, year in [(df_2024, "2024"), (df_2025, "2025")]:
        for col, dtype in required_cols.items():
            if col not in df.columns:
                st.error(f"Columna faltante: '{col}' en {year}.")
                return
            if dtype == "numeric" and not pd.api.types.is_numeric_dtype(df[col]):
                st.error(f"Error de formato: '{col}' en {year} debe contener números.")
                return

    # 2. Normalizar formato de rondas
    for df in [df_2024, df_2025]:
        df["Round"] = df["Round"].astype(str).str.replace(r"(\D)(\d)", r"\1 \2", regex=True).str.strip()

    # 3. Ordenamiento numérico de rondas
    def sort_rounds(rounds):
        def custom_key(round_str):
            try:
                # Extraer el último elemento y convertirlo a entero
                return int(round_str.split()[-1])
            except (ValueError, IndexError):
                # Si falla, devolver un número grande para ponerlo al final
                return float('inf')
        
        return sorted(rounds, key=custom_key)

    # --- KPI Benchmarks ---
    st.markdown("""
    <div style='background-color:#f5f5f5; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='margin-bottom: 10px;'>📊 <span style='color:#C8102E;'>2024 Season Averages</span></h4>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("xG", round(df_2024['xG'].mean(), 2) if 'xG' in df_2024.columns else "N/A")
    with col2:
        st.metric("PPDA", round(df_2024['PPDA'].mean(), 2))
    with col3:
        st.metric("Possession", f"{round(df_2024['Possession, %'].mean(), 1)}%" if 'Possession, %' in df_2024.columns else "N/A")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- PPDA filter: Half or Full ---
    st.markdown("### ⚙️ Choose PPDA Type to Compare")
    ppda_compare_option = st.selectbox("PPDA Type", ["Full Match (90 mins)", "1st Half", "2nd Half"])

    ppda_col_map = {
        "Full Match (90 mins)": "PPDA",
        "1st Half": "PPDA 1st Half",
        "2nd Half": "PPDA 2nd Half"
    }
    selected_ppda_col = ppda_col_map[ppda_compare_option]

    # --- Select match from 2024 ---
    st.markdown("### 🔙 Select from 2024 season")
    round_2024 = st.selectbox("Round (2024)", sort_rounds(df_2024["Round"].unique()))
    matches_2024 = df_2024[df_2024["Round"] == round_2024]
    match_2024 = st.selectbox("Match (2024)", matches_2024["Match"].tolist())

    # --- Select match from 2025 ---
    st.markdown("### 🔜 Select from current season (2025)")
    round_2025 = st.selectbox("Round (2025)", sort_rounds(df_2025["Round"].unique()))
    matches_2025 = df_2025[df_2025["Round"] == round_2025]
    match_2025 = st.selectbox("Match (2025)", matches_2025["Match"].tolist())

    # --- Extract values ---
    try:
        # 4. Extracción robusta con iloc
        val_2024 = matches_2024[matches_2024["Match"] == match_2024][selected_ppda_col].iloc[0]
        val_2025 = matches_2025[matches_2025["Match"] == match_2025][selected_ppda_col].iloc[0]
        avg_2024 = df_2024[selected_ppda_col].mean()
    except Exception as e:
        st.error(f"Error al extraer valores: {str(e)}")
        return

    # --- Show comparison ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{match_2024} (2024)", round(val_2024, 2))
    with col2:
        st.metric(f"{match_2025} (2025)", round(val_2025, 2))
    with col3:
        st.metric("Difference", f"{(val_2025 - val_2024):+.2f}")

    # --- Plotly bar chart ---
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[val_2024],
        name=f"{match_2024} (2024)",
        text=[f"<b>{val_2024:.2f}</b>"],
        textposition='outside',
        marker_color="#C8102E"
    ))

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[val_2025],
        name=f"{match_2025} (2025)",
        text=[f"<b>{val_2025:.2f}</b>"],
        textposition='outside',
        marker_color="#00843D"
    ))

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[avg_2024],
        name="2024 Season Avg",
        text=[f"<b>{avg_2024:.2f}</b>"],
        textposition='outside',
        marker_color="#000000"
    ))

    fig.update_layout(
        barmode='group',
        title=dict(
            text=f"<b>PPDA Comparison by Round – {ppda_compare_option}</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        yaxis_title="<b>PPDA</b>",
        template="simple_white",
        height=500,
        margin=dict(t=80, b=60),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor='center')
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Rolling PPDA Comparison by Season ---
    st.markdown("### 🌟 Rolling PPDA Comparison – 2024 vs 2025")
    ppda_option = st.selectbox("Select Rolling PPDA Type", ["1st Half", "2nd Half", "Full Match (90 mins)"])
    col_selected = ppda_col_map[ppda_option]
    
    # ==== CORRECCIÓN: Usar los valores reales, no la media móvil ====
    for df in [df_2024, df_2025]:
        df["Date"] = pd.to_datetime(df["Date"])
    
    df_2024_sorted = df_2024.sort_values("Date").copy()
    df_2024_sorted["Rolling"] = df_2024_sorted[col_selected]  # Valor real, no media
    avg_2024 = df_2024[col_selected].mean()
    
    fig_rolling = go.Figure()
    
    # Add 2024 trace
    fig_rolling.add_trace(go.Scatter(
        x=df_2024_sorted["Date"],
        y=df_2024_sorted["Rolling"],  # <-- Aquí se usan los valores directos
        mode='lines+markers',
        name="2024",
        marker=dict(symbol='circle', size=8, color="#C8102E"),
        line=dict(color="#C8102E", width=2),
        hovertemplate="<b>2024</b><br>PPDA: %{y:.2f}<br>Date: %{x|%b %d}"
    ))
    
    if len(df_2025) > 0:
        df_2025_sorted = df_2025.sort_values("Date").copy()
        df_2025_sorted["Rolling"] = df_2025_sorted[col_selected]  # <-- Valor real
        avg_2025 = df_2025_sorted[col_selected].mean()
    
        fig_rolling.add_trace(go.Scatter(
            x=df_2025_sorted["Date"],
            y=df_2025_sorted["Rolling"],  # <-- Sin media móvil
            mode='lines+markers',
            name="2025",
            marker=dict(symbol='square', size=8, color="#00843D"),
            line=dict(color="#00843D", width=2),
            hovertemplate="<b>2025</b><br>PPDA: %{y:.2f}<br>Date: %{x|%b %d}"
        ))

        fig_rolling.add_trace(go.Scatter(
            x=[df_2025_sorted["Date"].min(), df_2025_sorted["Date"].max()],
            y=[avg_2025, avg_2025],
            mode='lines',
            name="2025 Avg",
            line=dict(color="#00843D", width=1, dash="dot"),
            showlegend=True
        ))

    fig_rolling.add_trace(go.Scatter(
        x=[df_2024_sorted["Date"].min(), df_2024_sorted["Date"].max()],
        y=[avg_2024, avg_2024],
        mode='lines',
        name="2024 Avg",
        line=dict(color="#C8102E", width=1, dash="dot"),
        showlegend=True
    ))

    fig_rolling.update_layout(
        template="simple_white",
        height=550,
        xaxis_title="Date",
        yaxis_title=f"{ppda_option} – Rolling PPDA",
        title=dict(
            text=f"<b>Rolling PPDA over Time – {ppda_option}</b>",
            x=0.5,
            font=dict(size=20)
        ),
        xaxis=dict(
            tickformat="%b %d",
            tickangle=-45,
            showgrid=True,
            gridcolor='rgba(200,200,200,0.2)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.2)'
        ),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor='center')
    )

    st.plotly_chart(fig_rolling, use_container_width=True)

    # --- Footer signature ---
    st.markdown(
        """
        <hr style='margin-top: 40px; margin-bottom: 10px'>
        <div style='text-align: center; font-size: 14px; color: gray;'>
            <strong>Felipe Ormazabal</strong><br>Soccer Scout - Data Analyst
        </div>
        """,
        unsafe_allow_html=True
    )
