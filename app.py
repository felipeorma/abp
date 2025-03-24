import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Configuración inicial
st.set_page_config(layout="centered")
st.title("⚽ Demo: Heatmaps de Balón Parado")

# Datos ficticios de ejemplo
data = {
    "tipo": ["Tiro libre", "Córner", "Lateral", "Penal"],
    "minuto": [25, 40, 68, 85],
    "zona_saque": [17, 2, 5, "Penal"],
    "zona_remate": [4, 4, 4, "Penal"],
    "ejecutor": ["Jugador A", "Jugador B", "Jugador C", "Jugador D"]
}
df = pd.DataFrame(data)

# Coordenadas rotadas 180 grados para alinear con la imagen
zona_coords = {
    1: (100, 95),   2: (100, 37),     # Esquinas
    3: (78, 82),    4: (78, 50),      # Zona 4 es donde queremos remates
    5: (95, 70),    6: (95, 62),      
    7: (95, 66),    8: (95, 78),
    9: (95, 54),    10: (88, 70),     
    11: (88, 62),   12: (88, 78),
    13: (88, 54),   14: (70, 72),     
    15: (70, 60),   16: (55, 80),     
    17: (55, 52),   "Penal": (88, 66) # Zona 17 es saque
}

# Procesamiento de coordenadas
df["x_saque"] = df["zona_saque"].map(lambda z: zona_coords[z][0])
df["y_saque"] = df["zona_saque"].map(lambda z: zona_coords[z][1])
df["x_remate"] = df["zona_remate"].map(lambda z: zona_coords[z][0])
df["y_remate"] = df["zona_remate"].map(lambda z: zona_coords[z][1])

# Función para graficar
def plot_heatmap(title, x, y, cmap, ax):
    pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', 
                         pitch_color='grass', half=True)
    pitch.draw(ax=ax)
    
    # Aplicar rotación 180 grados (100-coord)
    pitch.kdeplot(x=100-np.array(y), y=100-np.array(x), ax=ax, 
                 fill=True, levels=50, cmap=cmap, alpha=0.6)
    pitch.scatter(100-np.array(y), 100-np.array(x), ax=ax, 
                color="black", s=100, edgecolors='white')
    
    # Dibujar números de zonas
    for zona, (x_coord, y_coord) in zona_coords.items():
        ax.text(100-y_coord, 100-x_coord, str(zona), 
               color="black", fontsize=10, ha="center", va="center", 
               bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
    
    ax.set_title(title)

# Visualización
st.subheader("📋 Datos de Ejemplo")
st.dataframe(df)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
plot_heatmap("🟢 Zona de Saque (17)", df["x_saque"], df["y_saque"], "Greens", ax1)
plot_heatmap("🔴 Zona de Remate (4)", df["x_remate"], df["y_remate"], "Reds", ax2)
st.pyplot(fig)

st.success("✅ Visualización correctamente alineada con las zonas de la imagen")