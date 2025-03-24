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
    with st.form("form_registro", clear_on_submit=True):
        mostrar_formulario(jugadores_cavalry, equipos_cpl, zonas_coords)
    
    mostrar_datos_y_visualizaciones(zonas_coords)

def mostrar_formulario(jugadores, equipos, zonas):
    st.subheader("📋 Registrar nueva acción")
    
    # Paso 1: Contexto del partido
    with st.container(border=True):
        st.markdown("### 🗓️ Contexto del Partido")
        col1, col2, col3 = st.columns(3)
        with col1:
            match_day = st.selectbox("Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
        with col2:
            oponente = st.selectbox("Rival", equipos)
        with col3:
            field = st.selectbox("Condición", ["Local", "Visitante"])

    # Resto del formulario... (mantener igual que en tu código original)

def mostrar_datos_y_visualizaciones(zonas):
    if st.session_state.registro:
        df = pd.DataFrame(st.session_state.registro)
        
        # Eliminar registros
        col1, col2 = st.columns([3,1])
        with col1:
            st.subheader("📊 Datos Registrados")
            st.dataframe(df, use_container_width=True)
        with col2:
            index_to_delete = st.number_input("Índice a eliminar", min_value=0, max_value=len(df)-1)
            if st.button("🗑️ Eliminar Registro"):
                st.session_state.registro.pop(index_to_delete)
                st.experimental_rerun()

        # Filtro y visualización
        st.markdown("### 🔍 Filtro de Equipo")
        equipo_filtro = st.radio(
            "Seleccionar equipo para visualizar:",
            ["Cavalry FC", "Oponente"],
            index=0
        )
        
        filtered_df = df[df["Equipo"] == ("Cavalry FC" if equipo_filtro == "Cavalry FC" else "Rival")]
        generar_heatmaps(filtered_df, zonas)

def generar_heatmaps(df, zonas):
    try:
        # Procesar coordenadas
        df = df.copy()
        df["coords_saque"] = df["Zona Saque"].map(zonas)
        df["coords_remate"] = df["Zona Remate"].map(zonas)
        df = df.dropna(subset=["coords_saque", "coords_remate"])
        
        df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
        df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)

        # Configurar pitch
        pitch = VerticalPitch(
            pitch_type='statsbomb', 
            pitch_color='grass', 
            line_color='white',
            half=True,
            goal_type='box'
        )

        # Heatmap de saques
        fig, ax = pitch.draw(figsize=(10, 6.5))
        pitch.kdeplot(
            df['x_saque'], df['y_saque'],
            ax=ax, cmap='Greens', levels=50, alpha=0.7
        )
        ax.set_title("Distribución de Saques", fontsize=14, pad=20)
        st.pyplot(fig)

        # Heatmap de remates
        fig, ax = pitch.draw(figsize=(10, 6.5))
        pitch.kdeplot(
            df['x_remate'], df['y_remate'],
            ax=ax, cmap='Reds', levels=50, alpha=0.7
        )
        ax.set_title("Zonas de Remate", fontsize=14, pad=20)
        st.pyplot(fig)

        # Descarga de datos
        csv = df.drop(columns=["coords_saque", "coords_remate", "x_saque", "y_saque", "x_remate", "y_remate"]).to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Descargar CSV Filtrado",
            csv,
            "acciones_filtradas.csv",
            "text/csv",
            key='download-csv'
        )
        
    except Exception as e:
        st.error(f"Error generando visualizaciones: {str(e)}")
