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

    # ==== CORRECCIÓN 1: Validar TODAS las columnas críticas ====
    required_cols = ["Round", "Match", "PPDA", "PPDA 1st Half", "PPDA 2nd Half"]
    for df, year in [(df_2024, "2024"), (df_2025, "2025")]:
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Columna '{col}' no encontrada en {year}. Revisa el Excel.")
                return
            elif not pd.api.types.is_numeric_dtype(df[col]):
                st.error(f"Columna '{col}' en {year} no es numérica. Corrige el formato.")
                return

    # ==== CORRECCIÓN 2: Normalizar formato de "Round" ====
    for df in [df_2024, df_2025]:
        df["Round"] = df["Round"].str.replace(r"(\D)(\d)", r"\1 \2", regex=True).str.strip()  # Ej: "Round1" → "Round 1"

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

    # ==== CORRECCIÓN 3: Forzar mostrar todas las rondas disponibles ====
    st.markdown("### 🔙 Select from 2024 season")
    round_2024 = st.selectbox("Round (2024)", sorted(df_2024["Round"].unique(), key=lambda x: int(x.split()[-1])))
    matches_2024 = df_2024[df_2024["Round"] == round_2024]
    match_2024 = st.selectbox("Match (2024)", matches_2024["Match"].tolist())

    st.markdown("### 🔜 Select from current season (2025)")
    round_2025 = st.selectbox("Round (2025)", sorted(df_2025["Round"].unique(), key=lambda x: int(x.split()[-1])))
    matches_2025 = df_2025[df_2025["Round"] == round_2025]
    match_2025 = st.selectbox("Match (2025)", matches_2025["Match"].tolist())

    # ==== CORRECCIÓN 4: Extracción robusta con iloc ====
    try:
        val_2024 = matches_2024[matches_2024["Match"] == match_2024][selected_ppda_col].iloc[0]  # .iloc[0] en lugar de .values[0]
        val_2025 = matches_2025[matches_2025["Match"] == match_2025][selected_ppda_col].iloc[0]
        avg_2024 = df_2024[selected_ppda_col].mean()
    except IndexError:
        st.error("No se encontró el partido seleccionado. Verifica los datos.")
        return
    except Exception as e:
        st.error(f"Error crítico: {str(e)}")
        return

    # ==== CORRECCIÓN 5: Depuración en tiempo real ====
    st.write(f"DEBUG - Valor 2025 ({selected_ppda_col}):", val_2025)  # Verificar valor crudo

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
        x=["PPDA"], y=[val_2024], name=f"{match_2024} (2024)",
        text=[f"<b>{val_2024:.2f}</b>"], textposition='outside', marker_color="#C8102E"
    ))

    fig.add_trace(go.Bar(
        x=["PPDA"], y=[val_2025], name=f"{match_2025} (2025)",
        text=[f"<b>{val_2025:.2f}</b>"], textposition='outside', marker_color="#00843D"
    ))

    fig.add_trace(go.Bar(
        x=["PPDA"], y=[avg_2024], name="2024 Season Avg",
        text=[f"<b>{avg_2024:.2f}</b>"], textposition='outside', marker_color="#000000"
    ))

    fig.update_layout(
        barmode='group',
        title=dict(text=f"<b>PPDA Comparison by Round – {ppda_compare_option}</b>", x=0.5),
        yaxis_title="<b>PPDA</b>",
        template="simple_white",
        height=500,
        margin=dict(t=80, b=60),
        legend=dict(orientation="h", y=-0.25, x=0.5)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Rolling PPDA Comparison by Season ---
    st.markdown("### 🌟 Rolling PPDA Comparison – 2024 vs 2025")
    ppda_option = st.selectbox("Select Rolling PPDA Type", ["1st Half", "2nd Half", "Full Match (90 mins)"])
    col_selected = ppda_col_map[ppda_option]

    for df in [df_2024, df_2025]:
        df["Date"] = pd.to_datetime(df["Date"])

    df_2024_sorted = df_2024.sort_values("Date").copy()
    df_2024_sorted["Rolling"] = df_2024_sorted[col_selected].rolling(window=3, min_periods=1).mean()
    avg_2024 = df_2024_sorted[col_selected].mean()

    fig_rolling = go.Figure()
    fig_rolling.add_trace(go.Scatter(
        x=df_2024_sorted["Date"], y=df_2024_sorted["Rolling"], name="2024",
        mode='lines+markers', marker=dict(color="#C8102E"), line=dict(width=2),
        hovertemplate="<b>2024</b><br>PPDA: %{y:.2f}<br>Date: %{x|%b %d}"
    ))

    if len(df_2025) > 0:
        df_2025_sorted = df_2025.sort_values("Date").copy()
        df_2025_sorted["Rolling"] = df_2025_sorted[col_selected].rolling(window=3, min_periods=1).mean()
        avg_2025 = df_2025_sorted[col_selected].mean()

        fig_rolling.add_trace(go.Scatter(
            x=df_2025_sorted["Date"], y=df_2025_sorted["Rolling"], name="2025",
            mode='lines+markers', marker=dict(color="#00843D"), line=dict(width=2),
            hovertemplate="<b>2025</b><br>PPDA: %{y:.2f}<br>Date: %{x|%b %d}"
        ))

        fig_rolling.add_trace(go.Scatter(
            x=[df_2025_sorted["Date"].min(), df_2025_sorted["Date"].max()], y=[avg_2025, avg_2025],
            mode='lines', name="2025 Avg", line=dict(color="#00843D", dash="dot")
        ))

    fig_rolling.add_trace(go.Scatter(
        x=[df_2024_sorted["Date"].min(), df_2024_sorted["Date"].max()], y=[avg_2024, avg_2024],
        mode='lines', name="2024 Avg", line=dict(color="#C8102E", dash="dot")
    ))

    fig_rolling.update_layout(
        template="simple_white",
        height=550,
        xaxis_title="Date",
        yaxis_title=f"{ppda_option} – Rolling PPDA",
        title=dict(text=f"<b>Rolling PPDA over Time – {ppda_option}</b>", x=0.5),
        xaxis=dict(tickformat="%b %d", tickangle=-45),
        legend=dict(orientation="h", y=-0.25, x=0.5)
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
