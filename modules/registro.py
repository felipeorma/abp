import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

def registro_page():
    # Datos ordenados
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

    # Formulario
    with st.form("form_registro"):
        st.subheader("📋 Registrar nueva acción")
        
        # Paso 1: Contexto del partido
        with st.container(border=True):
            st.markdown("### 🗓️ Contexto del Partido")
            col1, col2, col3 = st.columns(3)
            with col1:
                match_day = st.selectbox("Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
            with col2:
                oponente = st.selectbox("Rival", equipos_cpl)
            with col3:
                field = st.selectbox("Condición", ["Local", "Visitante"])

        # Paso 2: Tiempo del juego
        with st.container(border=True):
            st.markdown("### ⏱️ Tiempo de Juego")
            col1, col2 = st.columns(2)
            with col1:
                periodo = st.selectbox("Periodo", ["1T", "2T"])
            with col2:
                minuto_opciones = [str(x) for x in (range(0,46) if periodo == "1T" else range(45,91))]
                minuto_opciones += ["45+"] if periodo == "1T" else ["90+"]
                minuto_str = st.selectbox("Minuto", minuto_opciones)

        # Resto del formulario...
        
        if st.form_submit_button("✅ Registrar Acción"):
            minuto = 46 if "45+" in minuto_str else 91 if "90+" in minuto_str else int(minuto_str)
            registro_data = {
                # ... (todos los campos del formulario)
            }
            st.session_state.registro.append(registro_data)
            st.success("Acción registrada exitosamente!")
            st.balloons()

    # Visualización
    if st.session_state.registro:
        df = pd.DataFrame(st.session_state.registro)
        st.dataframe(df, use_container_width=True)
        
        # Heatmaps
        filtered_df = procesar_datos_visualizacion(df, zonas_coords)
        if not filtered_df.empty:
            generar_heatmaps(filtered_df)

def procesar_datos_visualizacion(df, zonas_coords):
    equipo_filtro = st.radio(
        "Seleccionar equipo para visualizar:",
        ["Cavalry FC", "Oponente"],
        index=0
    )
    
    filtered_df = df[df["Equipo"] == ("Cavalry FC" if equipo_filtro == "Cavalry FC" else "Rival")]
    
    filtered_df = filtered_df.copy()
    filtered_df["coords_saque"] = filtered_df["Zona Saque"].map(zonas_coords)
    filtered_df["coords_remate"] = filtered_df["Zona Remate"].map(zonas_coords)
    return filtered_df.dropna(subset=["coords_saque", "coords_remate"])

def generar_heatmaps(filtered_df):
    filtered_df[["x_saque", "y_saque"]] = pd.DataFrame(filtered_df["coords_saque"].tolist(), index=filtered_df.index)
    filtered_df[["x_remate", "y_remate"]] = pd.DataFrame(filtered_df["coords_remate"].tolist(), index=filtered_df.index)

    pitch = VerticalPitch(pitch_type='statsbomb', half=True)
    
    fig, ax = pitch.draw()
    pitch.kdeplot(
        filtered_df['x_saque'], filtered_df['y_saque'],
        ax=ax, cmap='Greens', levels=50, alpha=0.7
    )
    st.pyplot(fig)

    fig, ax = pitch.draw()
    pitch.kdeplot(
        filtered_df['x_remate'], filtered_df['y_remate'],
        ax=ax, cmap='Reds', levels=50, alpha=0.7
    )
    st.pyplot(fig)
