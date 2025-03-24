import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Configuración inicial
st.set_page_config(layout="centered")
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
# ... (El formulario se mantiene igual hasta la sección de visualización)

# ========== VISUALIZACIÓN ==========
if st.session_state.registro:
    st.subheader("📊 Datos Registrados")
    df = pd.DataFrame(st.session_state.registro)
    
    # Eliminar registros (se mantiene igual)
    
    # Selector de equipo con radio buttons
    st.markdown("### 🔍 Filtro de Equipo")
    equipo_filtro = st.radio(
        "Seleccionar equipo para visualizar:",
        ["Cavalry FC", "Oponente"],
        index=0  # Cavalry FC seleccionado por defecto
    )

    # Filtrar datos
    filtered_df = df[df["Equipo"] == ("Cavalry FC" if equipo_filtro == "Cavalry FC" else "Rival")]

    if not filtered_df.empty:
        # Procesamiento de coordenadas (se mantiene igual)

        # Función de graficación mejorada
        def graficar_heatmap(title, x, y, color):
            pitch = VerticalPitch(
                pitch_type='statsbomb', 
                pitch_color='grass', 
                line_color='white',
                half=True,  # Media cancha para ambos tipos
                goal_type='box'
            )
            fig, ax = pitch.draw(figsize=(10, 6.5))
            
            try:
                x = pd.to_numeric(x, errors='coerce')
                y = pd.to_numeric(y, errors='coerce')
                valid = x.notna() & y.notna()
                x_valid = x[valid]
                y_valid = y[valid]
                
                if not x_valid.empty:
                    # Heatmap principal
                    kde = pitch.kdeplot(
                        x_valid, y_valid, ax=ax,
                        cmap=f'{color.capitalize()}s',
                        levels=100,
                        fill=True,
                        alpha=0.75,
                        bw_adjust=0.5,
                        zorder=2
                    )
                    
                    # Firma profesional
                    ax.text(
                        0.02, 0.03,  # Posición inferior izquierda
                        "By: Felipe Ormazabal\nFootball Scout - Data Analyst",
                        fontsize=9,
                        color='#404040',
                        ha='left',
                        va='bottom',
                        transform=ax.transAxes,
                        alpha=0.9,
                        fontstyle='italic'
                    )
                    
            except Exception as e:
                st.error(f"Error al generar el gráfico: {str(e)}")
            
            st.subheader(title)
            st.pyplot(fig)

        # Generar ambos heatmaps en media cancha
        graficar_heatmap("🟢 Densidad de Saques", filtered_df["x_saque"], filtered_df["y_saque"], "green")
        graficar_heatmap("🔴 Densidad de Remates", filtered_df["x_remate"], filtered_df["y_remate"], "red")

        # Descarga de datos (se mantiene igual)
    else:
        st.warning("⚠️ No hay datos para el equipo seleccionado")

else:
    st.info("📭 No hay acciones registradas. Comienza registrando una acción arriba.")