import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from mplsoccer import VerticalPitch

# Inicialización y formulario (se mantienen igual)
# ...

# Coordenadas rotadas 180 grados (volteamos ambos ejes)
zona_coords = {
    1: (100, 95),   2: (100, 37),     # Esquinas superiores
    3: (78, 82),    4: (78, 50),      # Laterales superiores
    5: (95, 70),    6: (95, 62),      # Central superior
    7: (95, 66),    8: (95, 78),
    9: (95, 54),    10: (88, 70),     # Delantera
    11: (88, 62),   12: (88, 78),
    13: (88, 54),   14: (70, 72),     # Mediocampo
    15: (70, 60),   16: (55, 80),     # Defensa
    17: (55, 52),   "Penal": (88, 66) # Punto penal
}

def dibujar_half_pitch(title, x, y, cmap):
    st.subheader(title)
    pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', 
                        pitch_color='grass', half=True)
    fig, ax = pitch.draw(figsize=(8, 6))
    
    # Aplicamos la rotación visual (intercambiamos y complementamos)
    if not x.empty and not y.empty:
        pitch.kdeplot(x=100-np.array(y), y=100-np.array(x), ax=ax, fill=True,
                     levels=50, cmap=cmap, alpha=0.6)
        pitch.scatter(100-np.array(y), 100-np.array(x), ax=ax, color="black",
                     s=30, edgecolors='white')
    st.pyplot(fig)