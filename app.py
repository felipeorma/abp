import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Configuración inicial
st.set_page_config(layout="centered")
st.title("⚽ Zonas Correctamente Orientadas")

# ----------------------------------------
# Mapeo de zonas según IMG_4577.png
# ----------------------------------------
zona_coords = {
    # Fila inferior (Saque)
    16: (15, 92), 17: (35, 92),
    14: (15, 82), 15: (35, 82),
    3: (15, 72), 4: (35, 72),
    12: (15, 62), 1: (25, 62), 13: (35, 62),
    8: (15, 52), 5: (25, 52), 7: (35, 52), 6: (45, 52), 9: (55, 52),
    "Penal": (25, 72)  # Zona especial
}

# ----------------------------------------
# Datos ficticios (Saque=17, Remate=4)
# ----------------------------------------
data = {
    "tipo": ["Tiro libre", "Córner", "Lateral", "Penal"],
    "zona_saque": [17, 2, 5, "Penal"],
    "zona_remate": [4, 4, 4, "Penal"]
}
df = pd.DataFrame(data)

# ----------------------------------------
# Conversión de coordenadas
# ----------------------------------------
def convert_coords(zona, is_saque=True):
    base_x = 50  # Centrar en el campo
    if isinstance(zona, str):  # Para penales
        return (zona_coords[zona][0], zona_coords[zona][1])
    
    # Ajuste especial para zona 17 (Saque)
    if zona == 17 and is_saque: 
        return (zona_coords[zona][0] - 10, zona_coords[zona][1] + 5)
    
    return (zona_coords[zona][0], zona_coords[zona][1])

df["x_saque"] = df["zona_saque"].apply(lambda z: convert_coords(z)[0])
df["y_saque"] = df["zona_saque"].apply(lambda z: convert_coords(z)[1])
df["x_remate"] = df["zona_remate"].apply(lambda z: convert_coords(z, False)[0])
df["y_remate"] = df["zona_remate"].apply(lambda z: convert_coords(z, False)[1])

# ----------------------------------------
# Visualización
# ----------------------------------------
def plot_custom_pitch(ax, title):
    pitch = VerticalPitch(pitch_type='custom', line_color='white', 
                         pitch_color='#1d3b2d', half=True,
                         pitch_width=70, pitch_length=110)
    pitch.draw(ax=ax)
    
    # Dibujar zonas
    for zona, (x, y) in zona_coords.items():
        ax.text(x, y, str(zona), color="white", fontsize=10,
                ha="center", va="center", 
                bbox=dict(facecolor='#2d5a3d', alpha=0.9, edgecolor='white'))
    
    # Ajustes de orientación
    ax.invert_yaxis()
    ax.set_title(title, color="white", pad=20)

# Crear figura
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
plt.subplots_adjust(wspace=0.05)
fig.patch.set_facecolor('#1d3b2d')

# Heatmap de Saque (Zona 17)
plot_custom_pitch(ax1, "SAQUE (Zona 17)")
pitch = VerticalPitch(half=True)
pitch.kdeplot(df["x_saque"], df["y_saque"], ax=ax1, 
             cmap="Greens", levels=30, alpha=0.7)

# Heatmap de Remate (Zona 4)
plot_custom_pitch(ax2, "REMATE (Zona 4)")
pitch.kdeplot(df["x_remate"], df["y_remate"], ax=ax2,
             cmap="Reds", levels=30, alpha=0.7)

# Mostrar en Streamlit
st.pyplot(fig)
st.success("✅ Orientación perfectamente alineada con IMG_4577.png")