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

    # Coordenadas centrales representativas para cada zona (finales)
    zonas_coords = {
        1:  (120, 0),    2:  (120, 80),   3:  (93, 9),    4:  (93, 71),
        5:  (114, 30),  6:  (114, 50),  7:  (114, 40),  8:  (111, 15),
        9:  (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
       13: (105, 55), 14: (93, 29),  15: (93, 51), 16: (72, 20),
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

    # Función para graficar heatmap con estilo tipo sofascore
    def graficar_heatmap(title, x, y, cmap):
        st.subheader(title)
        pitch = VerticalPitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
        fig, ax = pitch.draw(figsize=(6, 9))

        fig.patch.set_facecolor('#0e1117')  # fondo total oscuro

        if len(x) >= 2:
            try:
                pitch.kdeplot(
                    x, y, ax=ax,
                    fill=True, cmap=cmap, levels=100,
                    alpha=0.8, bw_adjust=0.6
                )
            except ValueError:
                st.warning("⚠️ No se pudo generar el heatmap. Verifica que haya suficientes datos.")

        st.pyplot(fig)

    # Visualizar ambos heatmaps con estilo tipo sofascore
    graficar_heatmap("🟢 Heatmap - Zona de Saque", df["x_saque"], df["y_saque"], "inferno")
    graficar_heatmap("🔴 Heatmap - Zona de Remate", df["x_remate"], df["y_remate"], "inferno")

# 👇 Esta línea garantiza que todo se ejecute cuando el script corre en Streamlit
if __name__ == "__main__":
    main()
