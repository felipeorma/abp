import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mplsoccer import VerticalPitch
from PIL import Image

# Configuración inicial
st.set_page_config(layout="wide", page_icon="⚽", page_title="Advanced Set Piece Analytics")

# Cargar logo del equipo (reemplaza con tu logo)
logo = Image.open('team_logo.png')
st.sidebar.image(logo, use_column_width=True)

# Función para cargar datos
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(uploaded_file)
    
    # Limpieza y transformaciones
    df['xG'] = df['xG'].fillna(0)  # Si tienes datos de xG
    df['Eficiencia'] = df['Gol'].apply(lambda x: 1 if x == 'Sí' else 0)
    return df

# Sidebar de navegación
st.sidebar.title("Navegación")
app_mode = st.sidebar.radio("Seleccionar módulo", ["Registro Nuevo", "Advanced Analytics"])

# [Aquí iría tu código existente de registro cuando app_mode == "Registro Nuevo"]

# Sección de Análisis Avanzado
else:
    st.title("🔥 Advanced Set Piece Dashboard")
    uploaded_file = st.file_uploader("Cargar Master Data File", type=["csv", "xlsx"])
    
    if uploaded_file:
        df = load_data(uploaded_file)
        
        # ========== FILTROS AVANZADOS ==========
        with st.sidebar.expander("⚙️ PARÁMETROS DE ANÁLISIS", expanded=True):
            selected_season = st.multiselect("Temporada", options=df['Temporada'].unique())
            selected_opponent = st.multiselect("Oponente", options=df['Rival'].unique())
            selected_player = st.multiselect("Jugador", options=df['Ejecutor'].unique())
            action_type = st.multiselect("Tipo de Acción", options=df['Acción'].unique())
            min_minute, max_minute = st.slider("Rango de Minutos", 
                                              min_value=0, 
                                              max_value=120,
                                              value=(0, 120))
        
        # Aplicar filtros
        filtered_df = df.copy()
        filters = {
            'Temporada': selected_season,
            'Rival': selected_opponent,
            'Ejecutor': selected_player,
            'Acción': action_type
        }
        
        for col, values in filters.items():
            if values:
                filtered_df = filtered_df[filtered_df[col].isin(values)]
        
        filtered_df = filtered_df[(filtered_df['Minuto'] >= min_minute) & 
                                 (filtered_df['Minuto'] <= max_minute)]
        
        # ========== KPI HEADER ==========
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Acciones", len(filtered_df), help="Acciones de balón parado registradas")
        with col2:
            st.metric("Tasa de Conversión", 
                     f"{(len(filtered_df[filtered_df['Gol'] == 'Sí'])/len(filtered_df)*100 if len(filtered_df) > 0 else 0):.1f}%",
                     help="Porcentaje de acciones que terminan en gol")
        with col3:
            st.metric("xG Total", 
                     f"{filtered_df['xG'].sum():.2f}",
                     help="Expected Goals generados")
        with col4:
            st.metric("Eficiencia Estratégica", 
                     f"{(len(filtered_df[filtered_df['Strategic'] == 'Sí'])/len(filtered_df)*100 if len(filtered_df) > 0 else 0):.1f}%",
                     help="Porcentaje de jugadas estratégicas")
        
        # ========== TABS DE ANÁLISIS ==========
        tab1, tab2, tab3 = st.tabs(["📈 Overview", "👥 Player Analysis", "🆚 Team Analysis"])
        
        with tab1:
            # Gráfico de tendencias temporales
            time_df = filtered_df.groupby(['Jornada', 'Acción']).size().reset_index(name='Counts')
            fig1 = px.line(time_df, x='Jornada', y='Counts', color='Acción',
                          title="Evolución de Acciones por Tipo",
                          markers=True)
            st.plotly_chart(fig1, use_container_width=True)
            
            # Mapa de calor doble
            col1, col2 = st.columns(2)
            with col1:
                pitch = VerticalPitch(pitch_type='statsbomb', half=True)
                fig, ax = pitch.draw()
                try:
                    pitch.kdeplot(filtered_df['x_saque'], filtered_df['y_saque'], 
                                 ax=ax, cmap='Greens', levels=50, alpha=0.7)
                    st.pyplot(fig)
                except:
                    st.warning("Datos insuficientes para saques")
            
            with col2:
                pitch = VerticalPitch(pitch_type='statsbomb', half=True)
                fig, ax = pitch.draw()
                try:
                    pitch.kdeplot(filtered_df['x_remate'], filtered_df['y_remate'], 
                                 ax=ax, cmap='Reds', levels=50, alpha=0.7)
                    st.pyplot(fig)
                except:
                    st.warning("Datos insuficientes para remates")
        
        with tab2:
            # Rankings de jugadores
            st.subheader("🔝 Player Performance Rankings")
            
            if not filtered_df.empty:
                player_stats = filtered_df.groupby('Ejecutor').agg(
                    Total_Acciones=('Acción', 'count'),
                    Goles=('Gol', lambda x: sum(x == 'Sí')),
                    xG=('xG', 'sum'),
                    Eficiencia=('Eficiencia', 'mean')
                ).reset_index()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    fig = px.bar(player_stats.nlargest(5, 'Goles'), 
                                x='Ejecutor', y='Goles',
                                title="Top 5: Goles Directos",
                                color='Goles',
                                color_continuous_scale='greens')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(player_stats.nlargest(5, 'xG'), 
                                x='Ejecutor', y='xG',
                                title="Top 5: xG Generado",
                                color='xG',
                                color_continuous_scale='purples')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    fig = px.bar(player_stats[player_stats['Total_Acciones'] > 5].nlargest(5, 'Eficiencia'), 
                                x='Ejecutor', y='Eficiencia',
                                title="Top 5: Eficiencia (Gol/Acción)",
                                color='Eficiencia',
                                color_continuous_scale='blues')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos para mostrar rankings")
        
        with tab3:
            # Análisis comparativo vs oponentes
            st.subheader("📊 Team Performance Analysis")
            
            team_stats = filtered_df.groupby('Rival').agg(
                Total_Acciones=('Acción', 'count'),
                Goles_Recibidos=('Gol', lambda x: sum(x == 'Sí')),
                xG_Contra=('xG', 'sum'),
                Acciones_Estrategicas=('Strategic', lambda x: sum(x == 'Sí'))
            ).reset_index()
            
            # Radar chart de comparativa
            categories = ['Total_Acciones', 'Goles_Recibidos', 'xG_Contra', 'Acciones_Estrategicas']
            
            fig = go.Figure()
            
            for opponent in team_stats['Rival']:
                fig.add_trace(go.Scatterpolar(
                    r=team_stats[team_stats['Rival'] == opponent][categories].values[0],
                    theta=categories,
                    fill='toself',
                    name=opponent
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, team_stats[categories].values.max()]
                    )),
                showlegend=True,
                title="Comparativa por Oponente"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Heatmap de vulnerabilidades
            pivot_df = filtered_df.pivot_table(index='Rival', 
                                              columns='Zona Remate', 
                                              values='Gol', 
                                              aggfunc=lambda x: sum(x == 'Sí'))
            
            fig = px.imshow(pivot_df, 
                           labels=dict(x="Zona de Remate", y="Oponente", color="Goles"),
                           color_continuous_scale='YlOrRd',
                           title="Mapa de Vulnerabilidades Defensivas")
            st.plotly_chart(fig, use_container_width=True)
        
        # Sección de descarga
        st.sidebar.markdown("---")
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Exportar Dataset Filtrado", 
                                  csv, 
                                  "filtered_set_piece_data.csv", 
                                  "text/csv",
                                  help="Descargar datos actualmente filtrados en formato CSV")
    
    else:
        st.info("ℹ️ Carga tu archivo master_abp para comenzar el análisis")

# Estilos CSS personalizados
st.markdown("""
<style>
    .stMetric {border-left: 5px solid #2E86C1; padding: 15px!important;}
    header {visibility: hidden;}
    .stPlotlyChart {border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)