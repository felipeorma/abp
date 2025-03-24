import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mplsoccer import VerticalPitch
from PIL import Image

def main():
    # Configuración de la página
    st.set_page_config(layout="centered")
    st.title("⚽ Heatmaps de Balón Parado - Saque y Remate")

    # Cargar CSV simulado
    try:
        df = pd.read_csv("fake_abp_dataset.csv")
    except FileNotFoundError:
        st.error("❌ Archivo 'fake_abp_dataset.csv' no encontrado en el repositorio. Sube el archivo al mismo nivel del script.")
        st.stop()

    # Coordenadas centrales representativas para cada zona
    zonas_coords = {
        1:  (120, 0),    2:  (120, 80),   3:  (93, 9),    4:  (93, 71),
        5:  (114, 30),  6:  (114, 50),  7:  (114, 40),  8:  (111, 15),
        9:  (111, 62), 10: (114, 20), 11: (114, 65), 12: (105, 15),
       13: (105, 65), 14: (93, 29),  15: (93, 51), 16: (72, 20),
       17: (72, 60), "Penal": (108, 40)
    }

    # Asignar coordenadas centrales a cada acción en el dataframe
    df["coords_saque"] = df["zona_saque"].map(zonas_coords)
    df["coords_remate"] = df["zona_remate"].map(zonas_coords)

    # Eliminar filas con coordenadas inválidas
    df = df.dropna(subset=["coords_saque", "coords_remate"])

    # Separar en columnas x/y
    df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
    df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)

    # Función para graficar heatmap con etiquetas
    def graficar_heatmap(title, x, y, cmap):
        st.subheader(title)
        pitch = VerticalPitch(pitch_type='statsbomb', half=False, pitch_color='grass', line_color='white')
        fig, ax = pitch.draw(figsize=(6, 9))

        # Dibujar los números de zonas para verificación
        for zona, (x_z, y_z) in zonas_coords.items():
            pitch.annotate(str(zona), (x_z, y_z), ax=ax, fontsize=10, ha='center', va='center', color='black', bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))

        if len(x) >= 2:
            try:
                pitch.kdeplot(x, y, ax=ax, fill=True, cmap=cmap, levels=200, alpha=0.4, bw_adjust=0.3)
            except ValueError:
                st.warning("⚠️ No se pudo generar el heatmap. Verifica que haya suficientes datos.")

        st.pyplot(fig)

    # Visualizar ambos heatmaps
    graficar_heatmap("🟢 Heatmap - Zona de Saque", df["x_saque"], df["y_saque"], "Greens")
    graficar_heatmap("🔴 Heatmap - Zona de Remate", df["x_remate"], df["y_remate"], "Reds")

# 👇 Esta línea garantiza que todo se ejecute cuando el script corre en Streamlit
if __name__ == "__main__":
    main()
