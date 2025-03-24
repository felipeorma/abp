import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

# Leer el CSV generado desde la app
df = pd.read_csv("acciones_zonas.csv")

# Mapeo manual de cada zona a coordenadas promedio (x, y)
# ⚠️ Adaptado a cancha de 68x105 (puedes ajustar si usas otro sistema)
zona_coords = {
    1: (10, 95),   2: (58, 95),
    3: (18, 78),   4: (50, 78),
    5: (30, 100),  6: (38, 100),  7: (34, 100),  8: (22, 100), 9: (46, 100),
    10: (30, 88), 11: (38, 88), 12: (22, 88), 13: (46, 88),
    14: (28, 70), 15: (40, 70),
    16: (20, 55), 17: (48, 55)
}

# Crear una nueva columna con las coordenadas
df["coords"] = df["zona"].map(zona_coords)
df["x"] = df["coords"].apply(lambda c: c[0])
df["y"] = df["coords"].apply(lambda c: c[1])

# Crear el campo
pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', pitch_color='grass', linewidth=1)
fig, ax = pitch.draw(figsize=(8, 6))

# Crear heatmap tipo scatter con transparencia
pitch.kdeplot(
    x=df["x"],
    y=df["y"],
    ax=ax,
    fill=True,
    levels=100,
    cmap="Reds",
    shade_lowest=False,
    alpha=0.8
)

# Agregar puntos individuales (opcional)
pitch.scatter(df["x"], df["y"], ax=ax, color="black", s=30, edgecolors='white', zorder=2)

# Título
plt.title("🔥 Heatmap de zonas de finalización - Acciones de balón parado", fontsize=14)

# Mostrar
plt.tight_layout()
plt.show()
