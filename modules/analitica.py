import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go

# Cargar datos desde CSV
df = pd.read_csv('master_abp.csv')

# Unificar valores de la columna 'Gol' para evitar inconsistencias ("SI" y "Sí" tratados igual)
df['Gol'] = df['Gol'].replace({'SI': 'Sí'})

# Preparar opciones únicas de fechas (ordenadas) para el filtro de fecha
# Se utiliza multiselect en forma de dropdown por claridad y compacidad
df['Fecha_dt'] = pd.to_datetime(df['Fecha'], format="%m/%d/%Y %H:%M")
unique_dates_sorted = df.sort_values('Fecha_dt')['Fecha'].unique().tolist()

# Colocar los filtros en la interfaz
filter_col1, filter_col2 = st.columns([4, 1])
with filter_col1:
    # Filtro de fechas como selectbox con multiselección
    selected_dates = st.multiselect("Fecha(s)", options=unique_dates_sorted, default=unique_dates_sorted)
with filter_col2:
    # Filtro de equipo como selección única (Cavalry FC o Rival)
    selected_team = st.selectbox("Equipo", ["Cavalry FC", "Rival"])

# Filtrar el DataFrame según las fechas seleccionadas
df_date = df[df['Fecha'].isin(selected_dates)]

# Calcular KPI: goles a favor y encajados (dinámico según equipo seleccionado)
# Goles a favor Cavalry = eventos de Cavalry FC con Gol "Sí"
gf_cav = len(df_date[(df_date['Equipo'] == 'Cavalry FC') & (df_date['Gol'] == 'Sí')])
# Goles a favor Rival = eventos del rival con Gol "Sí"
gf_opp = len(df_date[(df_date['Equipo'] == 'Rival') & (df_date['Gol'] == 'Sí')])
# Total de ABP ejecutados por Cavalry y por Rival en las fechas seleccionadas
total_cav = len(df_date[df_date['Equipo'] == 'Cavalry FC'])
total_opp = len(df_date[df_date['Equipo'] == 'Rival'])

# Determinar KPIs según equipo seleccionado (dinámica de goles encajados invertida según el caso)
if selected_team == "Cavalry FC":
    goles_favor = gf_cav
    goles_encajados = gf_opp  # Goles encajados de Cavalry = goles del Rival
    # Efectividad ofensiva: % de ABP de Cavalry que terminan en gol
    efectividad_ofensiva = (goles_favor / total_cav * 100) if total_cav > 0 else 0
    # Efectividad defensiva: % de ABP del rival en que NO encajan gol (100% si no encaja ninguno)
    efectividad_defensiva = ((1 - (gf_opp / total_opp)) * 100) if total_opp > 0 else 0
else:  # selected_team == "Rival"
    goles_favor = gf_opp  # Goles a favor del Rival = goles encajados por Cavalry
    goles_encajados = gf_cav  # Goles encajados del Rival = goles a favor de Cavalry
    efectividad_ofensiva = (goles_favor / total_opp * 100) if total_opp > 0 else 0
    efectividad_defensiva = ((1 - (gf_cav / total_cav)) * 100) if total_cav > 0 else 0

# Mostrar los KPIs principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Goles a favor", int(goles_favor))
col2.metric("Goles encajados", int(goles_encajados))
col3.metric("Efectividad ofensiva (%)", f"{efectividad_ofensiva:.1f}%")
col4.metric("Efectividad defensiva (%)", f"{efectividad_defensiva:.1f}%")

# Filtrar datos por equipo seleccionado para gráficos de detalle
filtered_team_df = df_date[df_date['Equipo'] == selected_team]

# Crear función para generar figura de cancha de fútbol con Plotly (fondo y líneas)
def create_field_figure(width=600, height=400):
    fig = go.Figure()
    # Configurar fondo verde (cancha) y ejes ocultos
    fig.update_layout(
        plot_bgcolor="#0B6623", paper_bgcolor="#0B6623",
        xaxis=dict(range=[0, 120], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, 80], showgrid=False, zeroline=False, visible=False),
        width=width, height=height, margin=dict(l=0, r=0, t=0, b=0)
    )
    # Dibujar líneas del campo (blancas) como shapes
    field_shapes = [
        # Perímetro del campo
        dict(type='rect', x0=0, y0=0, x1=120, y1=80, line=dict(color='white', width=2), layer='below', fillcolor='rgba(0,0,0,0)'),
        # Línea central
        dict(type='line', x0=60, x1=60, y0=0, y1=80, line=dict(color='white', width=2), layer='below'),
        # Círculo central
        dict(type='circle', x0=50, y0=30, x1=70, y1=50, line=dict(color='white', width=2), layer='below', fillcolor='rgba(0,0,0,0)'),
        # Área penal derecha
        dict(type='rect', x0=102, y0=18, x1=120, y1=62, line=dict(color='white', width=2), layer='below', fillcolor='rgba(0,0,0,0)'),
        # Área penal izquierda
        dict(type='rect', x0=0, y0=18, x1=18, y1=62, line=dict(color='white', width=2), layer='below', fillcolor='rgba(0,0,0,0)'),
        # Área chica derecha
        dict(type='rect', x0=114, y0=30, x1=120, y1=50, line=dict(color='white', width=2), layer='below', fillcolor='rgba(0,0,0,0)'),
        # Área chica izquierda
        dict(type='rect', x0=0, y0=30, x1=6, y1=50, line=dict(color='white', width=2), layer='below', fillcolor='rgba(0,0,0,0)'),
        # Punto penal derecha
        dict(type='circle', x0=107, y0=39, x1=109, y1=41, line=dict(color='white', width=2), layer='below', fillcolor='white'),
        # Punto penal izquierda
        dict(type='circle', x0=11, y0=39, x1=13, y1=41, line=dict(color='white', width=2), layer='below', fillcolor='white'),
        # Portería derecha
        dict(type='line', x0=120, x1=120, y0=36, y1=44, line=dict(color='white', width=4), layer='below'),
        # Portería izquierda
        dict(type='line', x0=0, x1=0, y0=36, y1=44, line=dict(color='white', width=4), layer='below')
    ]
    fig.update_layout(shapes=field_shapes)
    return fig

# Generar mapas de calor (saque y remate) si hay datos disponibles
if filtered_team_df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
else:
    # Filtrar datos para heatmap de saques excluyendo zona "Penal"
    df_heat_saque = filtered_team_df[filtered_team_df['Zona Saque'] != 'Penal']
    df_heat_remate = filtered_team_df  # incluye todos, incluso penales
    
    st.subheader("Mapas de calor de zonas de saque y remate")
    colA, colB = st.columns(2)
    with colA:
        st.caption("Mapa de calor – Zona de Saque (excluyendo penales)")
        fig_saque = create_field_figure(width=500, height=333)
        # Agregar heatmap de saques (si hay datos luego de excluir penales)
        if not df_heat_saque.empty:
            fig_saque.add_trace(go.Histogram2d(
                x=df_heat_saque['x_saque'], y=df_heat_saque['y_saque'],
                xbins=dict(start=0, end=120, size=5),  # bins de ~5 unidades
                ybins=dict(start=0, end=80, size=5),
                colorscale='YlOrRd', reversescale=False, showscale=False, opacity=0.7
            ))
        st.plotly_chart(fig_saque, use_container_width=True)
    with colB:
        st.caption("Mapa de calor – Zona de Remate")
        fig_remate = create_field_figure(width=500, height=333)
        if not df_heat_remate.empty:
            fig_remate.add_trace(go.Histogram2d(
                x=df_heat_remate['x_remate'], y=df_heat_remate['y_remate'],
                xbins=dict(start=0, end=120, size=5),
                ybins=dict(start=0, end=80, size=5),
                colorscale='YlOrRd', reversescale=False, showscale=False, opacity=0.7
            ))
        st.plotly_chart(fig_remate, use_container_width=True)

    # Análisis de contactos por parte del cuerpo (primer contacto principalmente)
    st.subheader("Análisis de contactos por parte del cuerpo")
    # Excluir entradas sin parte de cuerpo (NaN significa que no hubo contacto claro)
    part_df = filtered_team_df[filtered_team_df['Parte Cuerpo'].notna()]
    if part_df.empty:
        st.write("No se registró ningún contacto con el balón en estas acciones.")
    else:
        # Grafica de barras de la frecuencia de cada parte del cuerpo usada en el primer contacto
        part_counts_chart = alt.Chart(part_df).mark_bar(color='#327B9E').encode(
            x=alt.X('Parte Cuerpo:N', sort='-y', title='Parte del Cuerpo'),
            y=alt.Y('count():Q', title='Cantidad de contactos')
        )
        st.altair_chart(part_counts_chart, use_container_width=True)

    # Ranking de jugadores (por ABP ejecutados)
    st.subheader("Ranking de jugadores (ABP ejecutados)")
    # Contar cuántas acciones ejecutó cada jugador (columna 'Ejecutor')
    ranking_df = filtered_team_df['Ejecutor'].value_counts().reset_index()
    ranking_df.columns = ['Jugador', 'Conteo']
    if ranking_df.empty:
        st.write("No hay datos de jugadores para mostrar.")
    else:
        # Tomar top 5 jugadores con más ejecuciones
        top_players = ranking_df.head(5)
        # Definir color de barras (rojo para Cavalry, gris para Rival)
        bar_color = '#D62728' if selected_team == 'Cavalry FC' else '#7F7F7F'
        ranking_chart = alt.Chart(top_players).mark_bar(color=bar_color).encode(
            y=alt.Y('Jugador:N', sort='-x', title=None),
            x=alt.X('Conteo:Q', title='Cantidad de ABP ejecutados')
        )
        st.altair_chart(ranking_chart, use_container_width=True)
