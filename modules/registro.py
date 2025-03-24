import streamlit as st
import pandas as pd
from utils.visualizaciones import plot_heatmap_registro

# Datos estáticos
JUGADORES = [
    "Joseph Holliday", "Neven Fewster", "Callum Montgomery", "Bradley Kamdem",
    "Tom Field", "Eryk Kobza", "Michael Harms", "Fraser Aird", 
    "Mihail Gherasimencov", "Charlie Trafford", "Jesse Daley", "Sergio Camargo",
    "Jay Herdman", "Caniggia Elva", "Maël Henry", "Shamit Shome",
    "Diego Gutiérrez", "Niko Myroniuk", "Josh Belbin", "James McGlinchey",
    "Ali Musse", "Tobias Warschewski", "Nicolas Wähling", "Chanan Chanda",
    "Myer Bevan", "Marco Carducci"
]

EQUIPOS_CPL = [
    "Atlético Ottawa", "Forge FC", "HFX Wanderers FC",
    "Pacific FC", "Valour FC", "Vancouver FC", "York United FC"
]

def registro_page():
    st.title("⚽ Registro y Heatmap de Balón Parado - Cavalry FC")
    
    if "registro" not in st.session_state:
        st.session_state.registro = []
    
    mostrar_formulario()
    mostrar_datos_registrados()

def mostrar_formulario():
    with st.form("form_registro", clear_on_submit=True):
        # Paso 1: Contexto del partido
        with st.container(border=True):
            st.markdown("### 🗓️ Contexto del Partido")
            col1, col2, col3 = st.columns(3)
            with col1:
                jornada = st.selectbox("Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
            with col2:
                rival = st.selectbox("Rival", EQUIPOS_CPL)
            with col3:
                condicion = st.selectbox("Condición", ["Local", "Visitante"])
        
        # ... (Continuar con el resto del formulario)
        
        if st.form_submit_button("✅ Registrar Acción"):
            registrar_accion({
                "Jornada": jornada,
                "Rival": rival,
                "Condición": condicion,
                # ... (resto de campos)
            })

def registrar_accion(datos):
    st.session_state.registro.append(datos)
    st.success("Acción registrada exitosamente!")
    st.balloons()

def mostrar_datos_registrados():
    if st.session_state.registro:
        df = pd.DataFrame(st.session_state.registro)
        st.dataframe(df, use_container_width=True)
        
        # Filtro y heatmaps
        equipo_filtro = st.radio(
            "Filtrar por equipo:",
            ["Cavalry FC", "Oponente"],
            index=0,
            key="filtro_equipo"
        )
        
        filtered_df = df[df["Equipo"] == ("Cavalry FC" if equipo_filtro == "Cavalry FC" else "Rival")]
        plot_heatmap_registro(filtered_df)
