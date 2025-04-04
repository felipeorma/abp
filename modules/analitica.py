# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from utils.i18n import get_text

def analitica_page(lang: str):
    st.title(get_text(lang, "analytics_title"))
    
    try:
        df = cargar_datos(lang)
        if df.empty:
            st.warning(get_text(lang, "empty_db_warning"))
            return
    except Exception as e:
        st.error(get_text(lang, "critical_error").format(error=str(e)))
        return

    df_filtrado = configurar_filtros(lang, df)
    mostrar_kpis(lang, df_filtrado)
    generar_seccion_espacial(lang, df_filtrado)
    generar_seccion_temporal(lang, df_filtrado)
    generar_seccion_efectividad(lang, df_filtrado)
    configurar_descarga(lang, df_filtrado)
    mostrar_ranking_parte_cuerpo(lang, df_filtrado)

def cargar_datos(lang: str):
    url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
    df = pd.read_csv(url)
    
    # Traducción de valores del dataset
    df['Gol'] = df['Gol'].map({'Sí': get_text(lang, 'yes'), 'No': get_text(lang, 'no')})
    df['Acción'] = df['Acción'].apply(lambda x: get_text(lang, x.lower().replace(' ', '_')))
    
    # Procesamiento de fechas
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Fecha'])
    
    # Validación de estructura
    columnas_requeridas = ['Jornada', 'Rival', 'Periodo', 'Minuto', 'Acción', 'Equipo', 'Fecha']
    if not all(col in df.columns for col in columnas_requeridas):
        return pd.DataFrame()
    
    # Limpieza numérica
    df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
    return df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor'])

def configurar_filtros(lang: str, df):
    with st.sidebar:
        st.header(get_text(lang, "advanced_filters"))
        
        ABREVIACIONES = {
            "York United FC": get_text(lang, "YOR"),
            "Vancouver FC": get_text(lang, "VAN"),
            "Pacific FC": get_text(lang, "PAC"),
            "Atlético Ottawa": get_text(lang, "OTT"),
            "Forge FC": get_text(lang, "FOR"),
            "HFX Wanderers FC": get_text(lang, "HFX"),
            "Valour FC": get_text(lang, "VAL")
        }
        
        # Procesamiento de partidos
        df = df.sort_values('Fecha', ascending=False)
        df['Fecha_str'] = df['Fecha'].dt.strftime('%d %b')
        df['Rival_abr'] = df['Rival'].map(ABREVIACIONES).fillna(df['Rival'])
        df['Partido'] = df.apply(lambda x: f"{x['Fecha_str']} vs {x['Rival_abr']}", axis=1)
        
        # Selectores
        partidos_seleccionados = st.multiselect(
            get_text(lang, "select_matches"),
            options=df['Partido'].unique(),
            default=df['Partido'].unique()
        )
        
        col1, col2 = st.columns(2)
        with col1:
            jornadas = st.multiselect(
                get_text(lang, "round"),
                options=df['Jornada'].unique(),
                default=df['Jornada'].unique()
            )
        with col2:
            condiciones = st.multiselect(
                get_text(lang, "condition"),
                options=df['Condición'].unique(),
                default=df['Condición'].unique()
            )

        col3, col4 = st.columns(2)
        with col3:
            acciones = st.multiselect(
                get_text(lang, "actions"),
                options=df['Acción'].unique(),
                default=df['Acción'].unique()
            )
        with col4:
            jugadores = st.multiselect(
                get_text(lang, "players"),
                options=df['Ejecutor'].unique(),
                default=df['Ejecutor'].unique()
            )

        # Slider de minutos
        min_min, max_min = int(df['Minuto'].min()), int(df['Minuto'].max())
        rango_minutos = st.slider(
            get_text(lang, "minutes"),
            min_min, max_min,
            (min_min, max_min)
        )
        
    return df[
        (df['Partido'].isin(partidos_seleccionados)) &
        (df['Jornada'].isin(jornadas)) &
        (df['Condición'].isin(condiciones)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]

def mostrar_kpis(lang: str, df):
    cols = st.columns(5)
    
    with cols[0]:
        st.metric(get_text(lang, "registered_actions"), df.shape[0])
    
    goles_favor = df[(df['Gol'] == get_text(lang, 'yes')) & (df['Equipo'] == 'Cavalry FC')].shape[0]
    with cols[1]:
        st.metric(get_text(lang, "goals_for"), goles_favor)
    
    goles_contra = df[(df['Gol'] == get_text(lang, 'yes')) & (df['Equipo'] != 'Cavalry FC')].shape[0]
    with cols[2]:
        st.metric(get_text(lang, "goals_against"), goles_contra)
    
    eficacia = (goles_favor / df.shape[0] * 100) if df.shape[0] > 0 else 0
    with cols[3]:
        st.metric(get_text(lang, "offensive_effectiveness"), f"{eficacia:.1f}%")
    
    eficacia_def = 100 - (goles_contra / df.shape[0] * 100) if df.shape[0] > 0 else 0
    with cols[4]:
        st.metric(get_text(lang, "defensive_effectiveness"), f"{eficacia_def:.1f}%")

def generar_seccion_espacial(lang: str, df):
    st.header(get_text(lang, "tactical_mapping"))
    col1, col2 = st.columns(2)
    
    with col1:
        generar_mapa_calor(lang, df, tipo='saque')
    with col2:
        generar_mapa_calor(lang, df, tipo='remate')

def generar_mapa_calor(lang: str, df, tipo='saque'):
    zonas_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }
    
    coord_col = 'Zona Saque' if tipo == 'saque' else 'Zona Remate'
    
    df_temp = df.copy()
    df_temp[coord_col] = df_temp[coord_col].apply(
        lambda x: int(x) if str(x).isdigit() else x
    )
    df_coords = df_temp[coord_col].map(zonas_coords).dropna().apply(pd.Series)
    
    if df_coords.empty:
        st.warning(get_text(lang, "no_data_warning").format(tipo=get_text(lang, tipo)))
        return
    
    df_coords.columns = ['x', 'y']
    
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
        df_coords['x'], df_coords['y'],
        ax=ax,
        cmap='Greens' if tipo == 'saque' else 'Reds',
        levels=100,
        fill=True,
        alpha=0.75,
        bw_adjust=0.65,
        zorder=2
    )
    
    ax.set_title(get_text(lang, "density_title").format(tipo=get_text(lang, tipo)), 
                fontsize=16, 
                pad=20,
                fontweight='bold')
    
    st.pyplot(fig)
    plt.close()

def generar_seccion_temporal(lang: str, df):
    st.header(get_text(lang, "temporal_evolution"))
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            df, x='Jornada', color='Periodo',
            title=get_text(lang, "actions_by_round"),
            labels={'count': get_text(lang, "actions")}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        fig = px.box(
            df, x='Acción', y='Minuto',
            color='Equipo', 
            title=get_text(lang, "time_distribution"),
            points="all"
        )
        st.plotly_chart(fig, use_container_width=True)

def generar_seccion_efectividad(lang: str, df):
    st.header(get_text(lang, "effectiveness_section"))
    col1, col2 = st.columns(2)
    
    with col1:
        df_efectividad = df.groupby('Ejecutor').agg(
            Acciones=('Ejecutor', 'count'),
            Goles=('Gol', lambda x: (x == get_text(lang, 'yes')).sum())
        ).reset_index()

        fig = px.scatter(
            df_efectividad, 
            x='Acciones', y='Goles',
            size='Goles', color='Ejecutor',
            title=get_text(lang, "actions_goals_relation")
        )

        fig.update_traces(marker=dict(line=dict(width=1, color='black')))
        fig.update_layout(
            plot_bgcolor='#F9F9F9',
            paper_bgcolor='#F9F9F9'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df_sun = df.groupby(['Acción', 'Resultado']).size().reset_index(name='Cantidad')
        df_sun = df_sun[df_sun['Resultado'].notna()]

        total = df_sun['Cantidad'].sum()
        df_sun['Porcentaje'] = df_sun['Cantidad'] / total * 100

        df_accion = df_sun.groupby('Acción')['Cantidad'].sum().reset_index()
        df_accion['Resultado'] = get_text(lang, "total")
        df_accion['Porcentaje'] = df_accion['Cantidad'] / total * 100

        df_sunburst = pd.concat([df_sun, df_accion], ignore_index=True)
        df_sunburst['Porcentaje'] = df_sunburst['Porcentaje'].fillna(0)

        fig = px.sunburst(
            df_sunburst,
            path=['Acción', 'Resultado'],
            values='Cantidad',
            title=get_text(lang, "results_composition"),
            branchvalues='total',
            custom_data=['Cantidad', 'Porcentaje']
        )

        fig.update_traces(
            hovertemplate=f'<b>%{{label}}</b><br>{get_text(lang, "quantity")}: %{{customdata[0]}}<br>{get_text(lang, "percentage")}: %{{customdata[1]:.1f}}%<extra></extra>'
        )
        st.plotly_chart(fig, use_container_width=True)

def mostrar_ranking_parte_cuerpo(lang: str, df):
    st.header(get_text(lang, "body_part_ranking"))
    ACCIONES_OFENSIVAS = [get_text(lang, acc) for acc in 
                        ["corner", "free_kick", "throw_in", "penalty", "cross", "shot"]]
    
    df['Tipo Acción'] = df['Acción'].apply(
        lambda x: get_text(lang, "offensive") if x in ACCIONES_OFENSIVAS else get_text(lang, "defensive"))
    
    color_map = {
        get_text(lang, "head"): '#00C2A0',
        get_text(lang, "leg"): '#FF5A5F',
        get_text(lang, "other"): '#4B4B4B'
    }

    for tipo in [get_text(lang, "offensive"), get_text(lang, "defensive")]:
        df_tipo = df[(df['Tipo Acción'] == tipo) & (df['Parte Cuerpo'].notna())]
        df_ranking = df_tipo.groupby(['Ejecutor', 'Parte Cuerpo']).size().reset_index(name='Cantidad')
        
        total_jugadores = df_ranking.groupby('Ejecutor')['Cantidad'].sum().sort_values(ascending=False)
        df_ranking['Ejecutor'] = pd.Categorical(
            df_ranking['Ejecutor'], 
            categories=total_jugadores.index, 
            ordered=True
        )

        st.subheader(f"{'⚔️' if tipo == get_text(lang, "offensive") else '🛡️'} {tipo} {get_text(lang, "actions")}")

        fig = px.bar(
            df_ranking,
            x='Cantidad',
            y='Ejecutor',
            color='Parte Cuerpo',
            orientation='h',
            text='Cantidad',
            title=get_text(lang, "players_actions_by_body").format(tipo=tipo),
            labels={'Cantidad': get_text(lang, "actions"), 'Ejecutor': get_text(lang, "player")},
            color_discrete_map=color_map,
            category_orders={'Ejecutor': total_jugadores.index.tolist()}
        )
        fig.update_layout(barmode='stack')
        st.plotly_chart(fig, use_container_width=True)

def configurar_descarga(lang: str, df):
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        get_text(lang, "export_data"),
        data=csv,
        file_name="tactical_analysis.csv",
        mime="text/csv",
        help=get_text(lang, "export_data_help")
    )
