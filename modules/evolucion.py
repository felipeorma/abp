import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def evolucion_page(lang):
    st.markdown("<h1 style='text-align: center;'>📈 PPDA Evolution by Round</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; color: gray;'>Analyze pressure intensity trends between past and current seasons</p>", unsafe_allow_html=True)

    # Load data
    try:
        df_2023 = pd.read_excel("Cavalry2023stats.xlsx")
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")
        return

    # Validate columns
    for df, year in [(df_2023, "2023"), (df_2024, "2024")]:
        for col in ["Round", "Match", "PPDA"]:
            if col not in df.columns:
                st.error(f"The {year} file must contain a '{col}' column.")
                return

    # --- KPI Benchmarks ---
    st.markdown("""
    <div style='background-color:#f5f5f5; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h4 style='margin-bottom: 10px;'>📊 <span style='color:#C8102E;'>2023 Season Averages</span></h4>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("xG", round(df_2023['xG'].mean(), 2) if 'xG' in df_2023.columns else "N/A")
    with col2:
        st.metric("PPDA", round(df_2023['PPDA'].mean(), 2))
    with col3:
        st.metric("Possession", f"{round(df_2023['Possession, %'].mean(), 1)}%" if 'Possession, %' in df_2023.columns else "N/A")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Select match from 2023 ---
    st.markdown("### 🔙 Select from 2023 season")
    round_2023 = st.selectbox("Round", sorted(df_2023["Round"].unique()))
    matches_2023 = df_2023[df_2023["Round"] == round_2023]
    match_2023 = st.selectbox("Match", matches_2023["Match"].tolist())

    # --- Select match from 2024 ---
    st.markdown("### 🔜 Select from current season (2024)")
    round_2024 = st.selectbox("Round ", sorted(df_2024["Round"].unique()))
    matches_2024 = df_2024[df_2024["Round"] == round_2024]
    match_2024 = st.selectbox("Match ", matches_2024["Match"].tolist())

    # --- Extract values ---
    val_2023 = matches_2023[matches_2023["Match"] == match_2023]["PPDA"].values[0]
    val_2024 = matches_2024[matches_2024["Match"] == match_2024]["PPDA"].values[0]
    avg_2023 = df_2023["PPDA"].mean()

    # --- Show comparison ---
    st.markdown("### 📍 PPDA Match Comparison")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{match_2023} (2023)", round(val_2023, 2))
    with col2:
        st.metric(f"{match_2024} (2024)", round(val_2024, 2))
    with col3:
        st.metric("Difference", f"{(val_2024 - val_2023):+.2f}")

    # --- Plotly bar chart with Cavalry FC colors ---
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[val_2023],
        name=f"{match_2023} (2023)",
        text=[f"<b>{val_2023:.2f}</b>"],
        textposition='outside',
        marker_color="#C8102E"  # Rojo
    ))

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[val_2024],
        name=f"{match_2024} (2024)",
        text=[f"<b>{val_2024:.2f}</b>"],
        textposition='outside',
        marker_color="#00843D"  # Verde
    ))

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[avg_2023],
        name="2023 Season Avg",
        text=[f"<b>{avg_2023:.2f}</b>"],
        textposition='outside',
        marker_color="#000000"  # Negro
    ))

    fig.update_layout(
        barmode='group',
        title=dict(
            text="<b>PPDA Comparison by Round</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        yaxis_title="<b>PPDA</b>",
        template="simple_white",
        height=500,
        margin=dict(t=80, b=60),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor='center'),
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- PPDA by Half + Rolling Average ---
    st.markdown("### 🧠 PPDA by Half vs Rolling Average")

    option = st.radio("Select view:", ["Both Halves", "1st Half Only", "2nd Half Only"], horizontal=True)

    tab1, tab2 = st.tabs(["🔙 2023 Season", "🔜 2024 Season"])

    with tab1:
        st.markdown("#### PPDA Comparison – 2023")

        val_1st = matches_2023[matches_2023["Match"] == match_2023]["PPDA 1st Half"].values[0]
        val_2nd = matches_2023[matches_2023["Match"] == match_2023]["PPDA 2nd Half"].values[0]
        val_full = matches_2023[matches_2023["Match"] == match_2023]["PPDA"].values[0]
        rolling_1st = df_2023[df_2023["Round"] <= round_2023]["PPDA 1st Half"].expanding().mean().iloc[-1]
        rolling_2nd = df_2023[df_2023["Round"] <= round_2023]["PPDA 2nd Half"].expanding().mean().iloc[-1]

        fig_2023 = go.Figure()

        if option != "2nd Half Only":
            fig_2023.add_trace(go.Bar(
                x=["1st Half"],
                y=[val_1st],
                name="Match Value",
                text=[f"<b>{val_1st:.2f}</b>"],
                textposition="outside",
                marker_color="#C8102E"
            ))
            fig_2023.add_trace(go.Bar(
                x=["1st Half"],
                y=[rolling_1st],
                name="Rolling Avg",
                text=[f"<b>{rolling_1st:.2f}</b>"],
                textposition="outside",
                marker_color="#6C6C6C"
            ))

        if option != "1st Half Only":
            fig_2023.add_trace(go.Bar(
                x=["2nd Half"],
                y=[val_2nd],
                name="Match Value",
                text=[f"<b>{val_2nd:.2f}</b>"],
                textposition="outside",
                marker_color="#00843D"
            ))
            fig_2023.add_trace(go.Bar(
                x=["2nd Half"],
                y=[rolling_2nd],
                name="Rolling Avg",
                text=[f"<b>{rolling_2nd:.2f}</b>"],
                textposition="outside",
                marker_color="#6C6C6C"
            ))

        fig_2023.update_layout(
            barmode='group',
            template='simple_white',
            height=400,
            yaxis_title='PPDA',
            title=dict(text=f"<b>{match_2023}</b> - PPDA by Half", x=0.5),
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor='center')
        )
        st.plotly_chart(fig_2023, use_container_width=True)

    with tab2:
        st.markdown("#### PPDA Comparison – 2024")

        val_1st = matches_2024[matches_2024["Match"] == match_2024]["PPDA 1st Half"].values[0]
        val_2nd = matches_2024[matches_2024["Match"] == match_2024]["PPDA 2nd Half"].values[0]
        val_full = matches_2024[matches_2024["Match"] == match_2024]["PPDA"].values[0]
        rolling_1st = df_2024[df_2024["Round"] <= round_2024]["PPDA 1st Half"].expanding().mean().iloc[-1]
        rolling_2nd = df_2024[df_2024["Round"] <= round_2024]["PPDA 2nd Half"].expanding().mean().iloc[-1]

        fig_2024 = go.Figure()

        if option != "2nd Half Only":
            fig_2024.add_trace(go.Bar(
                x=["1st Half"],
                y=[val_1st],
                name="Match Value",
                text=[f"<b>{val_1st:.2f}</b>"],
                textposition="outside",
                marker_color="#C8102E"
            ))
            fig_2024.add_trace(go.Bar(
                x=["1st Half"],
                y=[rolling_1st],
                name="Rolling Avg",
                text=[f"<b>{rolling_1st:.2f}</b>"],
                textposition="outside",
                marker_color="#6C6C6C"
            ))

        if option != "1st Half Only":
            fig_2024.add_trace(go.Bar(
                x=["2nd Half"],
                y=[val_2nd],
                name="Match Value",
                text=[f"<b>{val_2nd:.2f}</b>"],
                textposition="outside",
                marker_color="#00843D"
            ))
            fig_2024.add_trace(go.Bar(
                x=["2nd Half"],
                y=[rolling_2nd],
                name="Rolling Avg",
                text=[f"<b>{rolling_2nd:.2f}</b>"],
                textposition="outside",
                marker_color="#6C6C6C"
            ))

        fig_2024.update_layout(
            barmode='group',
            template='simple_white',
            height=400,
            yaxis_title='PPDA',
            title=dict(text=f"<b>{match_2024}</b> - PPDA by Half", x=0.5),
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor='center')
        )
        st.plotly_chart(fig_2024, use_container_width=True)
