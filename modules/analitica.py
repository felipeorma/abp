import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from utils.i18n import get_text  # Asegúrate de tener este módulo de traducción

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
    # Cargar datos desde GitHub
    url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
    df = pd.read_csv(url)
    
    # Renombrar columnas según el CSV
    df = df.rename(columns={
        'jornada': 'Jornada',
        'fecha': 'Fecha',
        'rival': 'Rival',
        'condición': 'Condición',
        'periodo': 'Periodo',
        'minuto': 'Minuto',
        'acción': 'Acción',
        'equipo': 'Equipo',
        'ejecutor': 'Ejecutor',
        'zona_saque': 'Zona Saque',
        'zona_remate': 'Zona Remate',
        'gol': 'Gol',
        'resultado': 'Resultado',
        'parte_cuerpo': 'Parte Cuerpo'
    })
    
    # Procesamiento de fechas
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Fecha'])
    
    # Traducir valores clave
    df['Gol'] = df['Gol'].map({'Sí': get_text(lang, 'yes'), 'No': get_text(lang, 'no')})
    
    # Mapeo de acciones
    action_translation = {
        'Córner': 'corner',
        'Tiro libre': 'free_kick',
        'Lateral': 'throw_in',
        'Penal': 'penalty',
        'Centro': 'cross',
        'Remate': 'shot'
    }
    df['Acción'] = df['Acción'].map(action_translation).apply(lambda x: get_text(lang, x))
    
    # Validación final
    required_columns = ['Jornada', 'Rival', 'Periodo', 'Minuto', 'Acción', 'Equipo', 'Fecha']
    if not all(col in df.columns for col in required_columns):
        return pd.DataFrame()
    
    return df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor'])

def configurar_filtros(lang: str, df_original):
    with st.sidebar:
        st.header(get_text(lang, "advanced_filters"))
        
        # Procesar fechas para mostrar
        df = df_original.copy()
        df = df.sort_values('Fecha', ascending=False)
        df['Fecha_str'] = df['Fecha'].dt.strftime('%d %b')
        df['Partido'] = df.apply(
            lambda x: f"{x['Fecha_str']} vs {x['Rival']}", 
            axis=1
        )
        
        widget_keys = {
            'partidos': f"{lang}_partidos",
            'jornadas': f"{lang}_jornadas",
            'condiciones': f"{lang}_condiciones",
            'acciones': f"{lang}_acciones",
            'jugadores': f"{lang}_jugadores",
            'minutos': f"{lang}_minutos"
        }
        
        # 1. Filtro inicial: Todos los partidos
        partidos_disponibles = df['Partido'].unique()
        partidos_seleccionados = st.multiselect(
            get_text(lang, "select_matches"),
            options=partidos_disponibles,
            default=st.session_state.get(widget_keys['partidos'], partidos_disponibles),
            key=widget_keys['partidos']
        )
        df_filtrado = df[df['Partido'].isin(partidos_seleccionados)]
        
        # 2. Filtro de jornadas basado en partidos seleccionados
        jornadas_disponibles = df_filtrado['Jornada'].unique()
        jornadas_seleccionadas = st.multiselect(
            get_text(lang, "round"),
            options=jornadas_disponibles,
            default=st.session_state.get(widget_keys['jornadas'], jornadas_disponibles),
            key=widget_keys['jornadas']
        )
        df_filtrado = df_filtrado[df_filtrado['Jornada'].isin(jornadas_seleccionadas)]
        
        # 3. Filtro de condiciones basado en selecciones anteriores
        condiciones_disponibles = df_filtrado['Condición'].unique()
        condiciones_seleccionadas = st.multiselect(
            get_text(lang, "condition"),
            options=condiciones_disponibles,
            default=st.session_state.get(widget_keys['condiciones'], condiciones_disponibles),
            format_func=lambda x: get_text(lang, f"condition_{x}"),
            key=widget_keys['condiciones']
        )
        df_filtrado = df_filtrado[df_filtrado['Condición'].isin(condiciones_seleccionadas)]
        
        # 4. Filtro de acciones basado en selecciones anteriores
        acciones_disponibles = df_filtrado['Acción'].unique()
        acciones_seleccionadas = st.multiselect(
            get_text(lang, "actions"),
            options=acciones_disponibles,
            default=st.session_state.get(widget_keys['acciones'], acciones_disponibles),
            key=widget_keys['acciones']
        )
        df_filtrado = df_filtrado[df_filtrado['Acción'].isin(acciones_seleccionadas)]
        
        # 5. Filtro de jugadores basado en selecciones anteriores
        jugadores_disponibles = df_filtrado['Ejecutor'].unique()
        jugadores_seleccionados = st.multiselect(
            get_text(lang, "players"),
            options=jugadores_disponibles,
            default=st.session_state.get(widget_keys['jugadores'], jugadores_disponibles),
            key=widget_keys['jugadores']
        )
        df_filtrado = df_filtrado[df_filtrado['Ejecutor'].isin(jugadores_seleccionados)]
        
        # 6. Filtro de minutos basado en selecciones anteriores
        min_min = int(df_filtrado['Minuto'].min()) if not df_filtrado.empty else 0
        max_min = int(df_filtrado['Minuto'].max()) if not df_filtrado.empty else 0
        rango_minutos = st.slider(
            get_text(lang, "minutes"),
            min_min, max_min,
            value=st.session_state.get(widget_keys['minutos'], (min_min, max_min)),
            key=widget_keys['minutos']
        )
        df_filtrado = df_filtrado[df_filtrado['Minuto'].between(*rango_minutos)]
        
    return df_filtrado

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
            df, 
            x='Jornada', 
            color='Periodo',
            title=get_text(lang, "actions_by_round"),
            labels={'count': get_text(lang, "actions")}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        fig = px.box(
            df, 
            x='Acción', 
            y='Minuto',
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
            x='Acciones', 
            y='Goles',
            size='Goles', 
            color='Ejecutor',
            title=get_text(lang, "actions_goals_relation")
        )
        fig.update_traces(marker=dict(line=dict(width=1, color='black')))
        fig.update_layout(plot_bgcolor='#F9F9F9', paper_bgcolor='#F9F9F9')
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
    
    # Definir acciones ofensivas usando claves de traducción
    ACCIONES_OFENSIVAS = [
        get_text(lang, "corner"),
        get_text(lang, "free_kick"),
        get_text(lang, "throw_in"),
        get_text(lang, "penalty"),
        get_text(lang, "cross"),
        get_text(lang, "shot")
    ]
    
    df['Tipo Acción'] = df['Acción'].apply(
        lambda x: get_text(lang, "offensive") if x in ACCIONES_OFENSIVAS else get_text(lang, "defensive")
    )

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
        file_name="analisis_tactico.csv",
        mime="text/csv",
        help=get_text(lang, "export_data_help")
    )

    # --- Firma del footer ---
    st.markdown(
        """
        <hr style='margin-top: 40px; margin-bottom: 10px'>
        <div style='text-align: center; font-size: 14px; color: gray;'>
            <strong>Felipe Ormazabal</strong><br>Soccer Scout - Data Analyst
        </div>
        """,
        unsafe_allow_html=True
    )
