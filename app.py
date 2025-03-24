import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import StringIO

# Configuración global
st.set_page_config(
    layout="wide",
    page_icon="⚽",
    page_title="Set Piece Analytics Pro",
    initial_sidebar_state="expanded"
)

# =============================================
# PESTAÑA 1: REGISTRO Y HEATMAPS (COMPLETA)
# =============================================
def main_page():
    st.title("⚽ Registro y Heatmap de Balón Parado - Cavalry FC")
    
    # Inicializar sesión para almacenar datos
    if "registro" not in st.session_state:
        st.session_state.registro = []

    # ========== DATOS ORDENADOS ==========
    jugadores_cavalry = sorted([
        "Joseph Holliday", "Neven Fewster", "Callum Montgomery", "Bradley Kamdem",
        "Tom Field", "Eryk Kobza", "Michael Harms", "Fraser Aird", 
        "Mihail Gherasimencov", "Charlie Trafford", "Jesse Daley", "Sergio Camargo",
        "Jay Herdman", "Caniggia Elva", "Maël Henry", "Shamit Shome",
        "Diego Gutiérrez", "Niko Myroniuk", "Josh Belbin", "James McGlinchey",
        "Ali Musse", "Tobias Warschewski", "Nicolas Wähling", "Chanan Chanda",
        "Myer Bevan"
    ], key=lambda x: x.split()[-1]) + ["Marco Carducci"]

    equipos_cpl = sorted([
        "Atlético Ottawa", "Forge FC", "HFX Wanderers FC",
        "Pacific FC", "Valour FC", "Vancouver FC", "York United FC"
    ])

    zonas_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }

    # ========== FORMULARIO ==========
    with st.expander("📋 Registrar nueva acción", expanded=True):
        st.subheader("Contexto del Partido")
        col1, col2, col3 = st.columns(3)
        with col1:
            match_day = st.selectbox("Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
        with col2:
            oponente = st.selectbox("Rival", equipos_cpl)
        with col3:
            field = st.selectbox("Condición", ["Local", "Visitante"])

        st.subheader("Tiempo de Juego")
        col1, col2 = st.columns(2)
        with col1:
            periodo = st.selectbox("Periodo", ["1T", "2T"])
        with col2:
            minuto_opciones = [str(x) for x in (range(0,46) if periodo == "1T" else range(45,91))]
            if periodo == "1T":
                minuto_opciones += ["45+"]
            else:
                minuto_opciones += ["90+"]
            minuto_str = st.selectbox("Minuto", minuto_opciones)

        st.subheader("Tipo de Acción")
        col1, col2 = st.columns(2)
        with col1:
            tipo_accion = st.selectbox("Tipo de acción", ["Tiro libre", "Córner", "Lateral", "Penal"])
        with col2:
            equipo = st.selectbox("Equipo ejecutor", ["Cavalry FC", "Rival"])

        st.subheader("Detalles de Ejecución")
        st.image("https://github.com/felipeorma/abp/blob/main/MedioCampo_enumerado.JPG?raw=true",
                 use_column_width=True)
        
        if equipo == "Cavalry FC":
            ejecutor = st.selectbox("Jugador ejecutor", jugadores_cavalry)
        else:
            ejecutor = "Rival"

        if tipo_accion == "Penal":
            zona_saque = zona_remate = "Penal"
            primer_contacto = cuerpo1 = segundo_contacto = "N/A"
            st.info("Configuración automática para penales")
        else:
            col1, col2 = st.columns(2)
            with col1:
                zona_saque = st.selectbox("Zona de saque", 
                    [1, 2] if tipo_accion == "Córner" else [z for z in zonas_coords if z != "Penal"])
            with col2:
                zona_remate = st.selectbox("Zona de remate", [z for z in zonas_coords if z != "Penal"])
            
            opciones_contacto = jugadores_cavalry + ["Oponente"]
            primer_contacto = st.selectbox("Primer contacto", opciones_contacto)
            cuerpo1 = st.selectbox("Parte del cuerpo", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
            segundo_contacto = st.selectbox("Segundo contacto (opcional)", ["Ninguno"] + opciones_contacto)

        st.subheader("Resultados")
        col1, col2 = st.columns(2)
        with col1:
            gol = st.selectbox("¿Gol?", ["No", "Sí"])
            resultado = st.selectbox("Resultado final", ["Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco", "Gol"])
        with col2:
            perfil = st.selectbox("Perfil ejecutor", ["Hábil", "No hábil"])
            estrategia = st.selectbox("Estrategia", ["Sí", "No"])
            tipo_pase = st.selectbox("Tipo de ejecución", ["Centro", "Pase corto", "Disparo directo"])

        # Conversión de minutos
        minuto = 46 if "45+" in minuto_str else 91 if "90+" in minuto_str else int(minuto_str)

        if st.button("✅ Registrar Acción", type="primary"):
            registro_data = {
                "Jornada": match_day,
                "Rival": oponente,
                "Condición": field,
                "Periodo": periodo,
                "Minuto": minuto,
                "Acción": tipo_accion,
                "Equipo": equipo,
                "Ejecutor": ejecutor,
                "Zona Saque": zona_saque,
                "Zona Remate": zona_remate,
                "Primer Contacto": primer_contacto,
                "Parte Cuerpo": cuerpo1,
                "Segundo Contacto": segundo_contacto if segundo_contacto != "Ninguno" else "",
                "Gol": gol,
                "Resultado": resultado,
                "Perfil": perfil,
                "Estrategia": estrategia,
                "Tipo Ejecución": tipo_pase
            }
            
            st.session_state.registro.append(registro_data)
            st.success("Acción registrada exitosamente!")
            st.balloons()

    # ========== VISUALIZACIÓN ==========
    if st.session_state.registro:
        st.subheader("📊 Datos Registrados")
        df = pd.DataFrame(st.session_state.registro)
        
        # Eliminar registros
        index_to_delete = st.number_input("Índice a eliminar", min_value=0, max_value=len(df)-1, key="delete_index")
        if st.button("🗑️ Eliminar Registro", key="delete_button"):
            st.session_state.registro.pop(index_to_delete)
            st.experimental_rerun()
        
        st.dataframe(df, use_column_width=True)

        # Filtro de equipo
        st.subheader("🔍 Filtro de Equipo")
        equipo_filtro = st.radio(
            "Seleccionar equipo para visualizar:",
            ["Cavalry FC", "Oponente"],
            index=0,
            key="team_filter"
        )

        # Aplicar filtro
        filtered_df = df[df["Equipo"] == ("Cavalry FC" if equipo_filtro == "Cavalry FC" else "Rival")]

        # Procesamiento seguro de coordenadas
        if not filtered_df.empty:
            filtered_df = filtered_df.copy()
            filtered_df["coords_saque"] = filtered_df["Zona Saque"].map(zonas_coords)
            filtered_df["coords_remate"] = filtered_df["Zona Remate"].map(zonas_coords)
            filtered_df = filtered_df.dropna(subset=["coords_saque", "coords_remate"])
            
            if not filtered_df.empty:
                filtered_df[["x_saque", "y_saque"]] = pd.DataFrame(filtered_df["coords_saque"].tolist(), index=filtered_df.index)
                filtered_df[["x_remate", "y_remate"]] = pd.DataFrame(filtered_df["coords_remate"].tolist(), index=filtered_df.index)
                
                # Función de graficación
                def graficar_heatmap(title, x, y, color):
                    pitch = VerticalPitch(
                        pitch_type='statsbomb',
                        pitch_color='grass',
                        line_color='white',
                        half=True,
                        goal_type='box'
                    )
                    fig, ax = pitch.draw(figsize=(10, 6.5))
                    try:
                        pitch.kdeplot(
                            x, y, ax=ax,
                            cmap=f'{color.capitalize()}s',
                            levels=100,
                            fill=True,
                            alpha=0.75,
                            bw_adjust=0.5,
                            zorder=2
                        )
                        ax.text(
                            0.02, 0.03,
                            "By: Felipe Ormazabal\nFootball Scout - Data Analyst",
                            fontsize=9,
                            color='#404040',
                            ha='left',
                            va='bottom',
                            transform=ax.transAxes,
                            alpha=0.9,
                            fontstyle='italic'
                        )
                        st.subheader(title)
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error al generar el gráfico: {str(e)}")

                # Generar heatmaps
                graficar_heatmap("🟢 Densidad de Saques", filtered_df["x_saque"], filtered_df["y_saque"], "green")
                graficar_heatmap("🔴 Densidad de Remates", filtered_df["x_remate"], filtered_df["y_remate"], "red")

                # Descarga de datos
                csv = filtered_df.drop(columns=["coords_saque", "coords_remate", "x_saque", "y_saque", "x_remate", "y_remate"]).to_csv(index=False).encode('utf-8')
                st.download_button(
                    "⬇️ Descargar CSV Filtrado",
                    csv,
                    "acciones_filtradas.csv",
                    "text/csv",
                    key="download_filtered"
                )
            else:
                st.warning("⚠️ No hay datos válidos para visualizar después del filtrado")
        else:
            st.warning("⚠️ No hay datos para el equipo seleccionado")
    else:
        st.info("📭 No hay acciones registradas. Comienza registrando una acción arriba.")

# =============================================
# PESTAÑA 2: ANALÍTICA AVANZADA (COMPLETA)
# =============================================
def analytics_page():
    st.title("📈 Análisis Avanzado de Jugadas a Balón Parado")
    
    # Configurar URL de datos
    GITHUB_RAW_URL = "https://github.com/felipeorma/abp/blob/main/master_abp.csv"
    
    @st.cache_data(ttl=3600)
    def load_github_data(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            
            # Preprocesamiento
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
            return df
            
        except Exception as e:
            st.error(f"Error cargando datos: {str(e)}")
            return pd.DataFrame()

    df = load_github_data(GITHUB_RAW_URL)

    if not df.empty:
        # ========== SIDEBAR FILTROS ==========
        st.sidebar.header("🔍 Parámetros de Análisis")
        
        # Filtro temporal
        min_date = df['Fecha'].min().date()
        max_date = df['Fecha'].max().date()
        selected_dates = st.sidebar.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Filtros múltiples
        selected_competition = st.sidebar.multiselect(
            "Competición", 
            df['Competición'].unique()
        )
        
        selected_opponent = st.sidebar.multiselect(
            "Oponente", 
            df['Rival'].unique()
        )
        
        selected_player = st.sidebar.multiselect(
            "Jugador clave", 
            df['Ejecutor'].unique()
        )

        # ========== APLICAR FILTROS ==========
        filtered_df = df.copy()
        
        # Filtro de fechas
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
            filtered_df = filtered_df[
                (filtered_df['Fecha'].dt.date >= start_date) &
                (filtered_df['Fecha'].dt.date <= end_date)
            ]
        
        # Aplicar otros filtros
        filter_params = {
            'Competición': selected_competition,
            'Rival': selected_opponent,
            'Ejecutor': selected_player
        }
        
        for col, values in filter_params.items():
            if values:
                filtered_df = filtered_df[filtered_df[col].isin(values)]

        # ========== KPI HEADER ==========
        st.header("📊 Métricas Clave")
        col1, col2, col3, col4 = st.columns(4)
        
        kpis = {
            "Acciones Totales": len(filtered_df),
            "Tasa de Éxito": f"{filtered_df['Gol'].eq('Sí').mean()*100:.1f}%",
            "xG Promedio": f"{filtered_df['xG'].mean():.2f}",
            "Eficiencia Estratégica": f"{filtered_df['Estrategia'].eq('Sí').mean()*100:.1f}%"
        }
        
        for col, (kpi, value) in zip([col1, col2, col3, col4], kpis.items()):
            with col:
                st.metric(kpi, value)

        # ========== ANÁLISIS TÁCTICO ==========
        st.header("🔥 Heatmaps Tácticos")
        col1, col2 = st.columns(2)
        
        with col1:
            pitch = VerticalPitch(pitch_type='statsbomb', half=True)
            fig, ax = pitch.draw()
            try:
                pitch.kdeplot(
                    filtered_df['x_saque'], filtered_df['y_saque'],
                    ax=ax, cmap='Greens', levels=50, alpha=0.7
                )
                ax.set_title("Distribución de Saques", fontsize=14, pad=20)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error generando heatmap de saques: {str(e)}")
        
        with col2:
            pitch = VerticalPitch(pitch_type='statsbomb', half=True)
            fig, ax = pitch.draw()
            try:
                pitch.kdeplot(
                    filtered_df['x_remate'], filtered_df['y_remate'],
                    ax=ax, cmap='Reds', levels=50, alpha=0.7
                )
                ax.set_title("Zonas de Remate", fontsize=14, pad=20)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error generando heatmap de remates: {str(e)}")

        # ========== RANKINGS DE JUGADORES ==========
        st.header("🏅 Rankings de Jugadores")
        
        if not filtered_df.empty:
            player_stats = filtered_df.groupby('Ejecutor').agg(
                Acciones=('Acción', 'count'),
                Goles=('Gol', lambda x: sum(x == 'Sí')),
                xG=('xG', 'sum'),
                Precisión=('Precisión', 'mean')
            ).reset_index()
            
            # Top 5 en diferentes métricas
            metrics = {
                'Goles': ('Goles Directos', 'Viridis'),
                'xG': ('xG Generado', 'Plasma'),
                'Precisión': ('Precisión (%)', 'Rainbow')
            }
            
            cols = st.columns(3)
            for (metric, (title, color)), col in zip(metrics.items(), cols):
                with col:
                    top_players = player_stats.nlargest(5, metric)
                    fig = px.bar(
                        top_players,
                        x='Ejecutor',
                        y=metric,
                        title=title,
                        color=metric,
                        color_continuous_scale=color
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos para mostrar rankings")

        # ========== ANÁLISIS DE OPONENTES ==========
        st.header("🆚 Análisis de Oponentes")
        
        if not filtered_df.empty:
            opponent_analysis = filtered_df.groupby('Rival').agg(
                Acciones_Contra=('Acción', 'count'),
                Goles_Recibidos=('Gol', lambda x: sum(x == 'Sí')),
                Zona_Peligrosa=('Zona Remate', lambda x: x.mode()[0])
            ).reset_index()
            
            fig = px.treemap(
                opponent_analysis,
                path=['Rival'],
                values='Acciones_Contra',
                color='Goles_Recibidos',
                color_continuous_scale='Reds',
                title='Vulnerabilidad Defensiva por Oponente'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla interactiva
            st.subheader("Tabla Detallada de Oponentes")
            st.dataframe(
                opponent_analysis.sort_values('Goles_Recibidos', ascending=False),
                column_config={
                    "Rival": "Oponente",
                    "Acciones_Contra": st.column_config.NumberColumn("Acciones Contra"),
                    "Goles_Recibidos": st.column_config.NumberColumn("Goles Recibidos"),
                    "Zona_Peligrosa": st.column_config.TextColumn("Zona Más Peligrosa")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("No hay datos para análisis de oponentes")

        # ========== SEGMENTACIÓN TEMPORAL ==========
        st.header("⏳ Evolución Temporal")
        
        time_analysis = filtered_df.resample('W', on='Fecha').agg({
            'Acción': 'count',
            'Gol': lambda x: sum(x == 'Sí'),
            'xG': 'sum'
        }).reset_index()
        
        fig = px.line(
            time_analysis,
            x='Fecha',
            y=['Acción', 'Gol', 'xG'],
            title="Tendencias Semanales",
            labels={'value': 'Cantidad', 'variable': 'Métrica'},
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("No se pudo cargar el dataset desde GitHub. Verifica la URL del archivo.")

# =============================================
# NAVEGACIÓN
# =============================================
st.sidebar.title("Navegación")
page = st.sidebar.radio(
    "Seleccionar módulo:",
    ("🏟️ Registro en Vivo", "📊 Panel Analítico"),
    index=0
)

if page == "🏟️ Registro en Vivo":
    main_page()
else:
    analytics_page()

# =============================================
# ESTILOS CSS
# =============================================
st.markdown("""
<style>
    .stMetric {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric label {
        font-size: 1.1rem!important;
        color: #2c3e50!important;
        font-weight: 600!important;
    }
    .stPlotlyChart, .stDataFrame {
        border: 1px solid #e0e0e0!important;
        border-radius: 10px!important;
        padding: 15px!important;
        background-color: #ffffff;
    }
    .stHeader {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.3rem;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 2rem;
    }
    .st-bd {
        padding: 15px!important;
    }
    .st-emotion-cache-1y4p8pa {
        padding: 2rem 1rem;
    }
    .stButton>button {
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)
