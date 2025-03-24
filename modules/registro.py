import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

def registro_page():
    # Datos ordenados
    jugadores, equipos, zonas_coords = cargar_datos()
    
    # Formulario
    with st.form("form_registro", clear_on_submit=True):
        datos = mostrar_formulario(jugadores, equipos, zonas_coords)
    
    if datos:  # Solo si se envió el formulario
        procesar_registro(datos)
    
    mostrar_datos_y_visualizaciones(zonas_coords)

def cargar_datos():
    jugadores = sorted([
        "Joseph Holliday", "Neven Fewster", "Callum Montgomery", "Bradley Kamdem",
        "Tom Field", "Eryk Kobza", "Michael Harms", "Fraser Aird", 
        "Mihail Gherasimencov", "Charlie Trafford", "Jesse Daley", "Sergio Camargo",
        "Jay Herdman", "Caniggia Elva", "Maël Henry", "Shamit Shome",
        "Diego Gutiérrez", "Niko Myroniuk", "Josh Belbin", "James McGlinchey",
        "Ali Musse", "Tobias Warschewski", "Nicolas Wähling", "Chanan Chanda",
        "Myer Bevan"
    ], key=lambda x: x.split()[-1]) + ["Marco Carducci"]

    equipos = sorted([
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
    
    return jugadores, equipos, zonas_coords

def mostrar_formulario(jugadores, equipos, zonas):
    datos = {}
    st.subheader("📋 Registrar nueva acción")
    
    # Contexto del partido
    with st.container(border=True):
        st.markdown("### 🗓️ Contexto del Partido")
        col1, col2, col3 = st.columns(3)
        datos["Jornada"] = col1.selectbox("Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
        datos["Rival"] = col2.selectbox("Rival", equipos)
        datos["Condición"] = col3.selectbox("Condición", ["Local", "Visitante"])

    # Tiempo de juego
    with st.container(border=True):
        st.markdown("### ⏱️ Tiempo de Juego")
        col1, col2 = st.columns(2)
        periodo = col1.selectbox("Periodo", ["1T", "2T"])
        
        # Generar opciones de minuto según periodo
        if periodo == "1T":
            minutos = [str(x) for x in range(0,46)] + ["45+"]
        else:
            minutos = [str(x) for x in range(45,91)] + ["90+"]
        
        minuto_str = col2.selectbox("Minuto", minutos)
        datos["Minuto"] = 46 if "45+" in minuto_str else 91 if "90+" in minuto_str else int(minuto_str)
        datos["Periodo"] = periodo

    # Tipo de acción
    with st.container(border=True):
        st.markdown("### ⚽ Acción")
        col1, col2 = st.columns(2)
        datos["Acción"] = col1.selectbox("Tipo de acción", ["Tiro libre", "Córner", "Lateral", "Penal"])
        datos["Equipo"] = col2.selectbox("Equipo ejecutor", ["Cavalry FC", "Rival"])

    # Detalles de ejecución
    with st.container(border=True):
        st.markdown("### 🎯 Detalles de Ejecución")
        st.image("https://github.com/felipeorma/abp/blob/main/MedioCampo_enumerado.JPG?raw=true", 
                use_column_width=True)
        
        # Lógica condicional para tipos de acción
        if datos["Acción"] == "Penal":
            datos["Zona Saque"] = "Penal"
            datos["Zona Remate"] = "Penal"
            datos["Primer Contacto"] = "N/A"
            datos["Parte Cuerpo"] = "N/A"
            datos["Segundo Contacto"] = ""
            st.info("Configuración automática para penales")
        else:
            col1, col2 = st.columns(2)
            
            # Restricción de zonas para córner
            if datos["Acción"] == "Córner":
                zona_opciones_saque = [1, 2]
            else:
                zona_opciones_saque = [z for z in zonas if z != "Penal"]
            
            datos["Zona Saque"] = col1.selectbox("Zona de saque", zona_opciones_saque)
            datos["Zona Remate"] = col2.selectbox("Zona de remate", [z for z in zonas if z != "Penal"])
            
            # Contactos
            opciones_contacto = jugadores + ["Oponente"]
            datos["Primer Contacto"] = st.selectbox("Primer contacto", opciones_contacto)
            datos["Parte Cuerpo"] = st.selectbox("Parte del cuerpo", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
            segundo_contacto = st.selectbox("Segundo contacto (opcional)", ["Ninguno"] + opciones_contacto)
            datos["Segundo Contacto"] = segundo_contacto if segundo_contacto != "Ninguno" else ""

    # Resultados
    with st.container(border=True):
        st.markdown("### 📊 Resultados")
        col1, col2 = st.columns(2)
        datos["Gol"] = col1.selectbox("¿Gol?", ["No", "Sí"])
        datos["Resultado"] = col1.selectbox("Resultado final", ["Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco", "Gol"])
        datos["Perfil"] = col2.selectbox("Perfil ejecutor", ["Hábil", "No hábil"])
        datos["Estrategia"] = col2.selectbox("Estrategia", ["Sí", "No"])
        datos["Tipo Ejecución"] = col2.selectbox("Tipo de ejecución", ["Centro", "Pase corto", "Disparo directo"])

    return datos if st.form_submit_button("✅ Registrar Acción") else None

def procesar_registro(datos):
    st.session_state.registro.append(datos)
    st.success("Acción registrada exitosamente!")
    st.balloons()

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
        if df.empty:
            st.warning("No hay datos para visualizar con los filtros actuales")
            return

        # Procesar coordenadas
        df = df.copy()
        df["coords_saque"] = df["Zona Saque"].map(zonas)
        df["coords_remate"] = df["Zona Remate"].map(zonas)
        df = df.dropna(subset=["coords_saque", "coords_remate"])
        
        df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
        df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)
        
        # Configuración optimizada del pitch
        pitch = VerticalPitch(
            pitch_type='statsbomb',
            pitch_color='grass',
            line_color='white',
            half=True,
            goal_type='box',
            linewidth=1.5,
            pad_top=15
        )

        # Heatmap de Saques
        fig1, ax1 = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax1)
        
        # Ajustes clave para el heatmap:
        kde1 = pitch.kdeplot(
            df['x_saque'], df['y_saque'],
            ax=ax1,
            cmap='Greens',
            levels=200,  # Más niveles para suavizado
            fill=True,
            alpha=0.6,   # Mayor transparencia
            bw_adjust=0.2,  # Aumentar el ancho de banda
            zorder=2
        )
        
        ax1.set_title('Distribución de Saques', fontsize=16, pad=20, weight='bold')
        st.pyplot(fig1)

        # Heatmap de Remates
        fig2, ax2 = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax2)
        
        kde2 = pitch.kdeplot(
            df['x_remate'], df['y_remate'],
            ax=ax2,
            cmap='Reds',
            levels=200,
            fill=True,
            alpha=0.6,
            bw_adjust=0.5,  # Mismo ajuste que para saques
            zorder=2
        )
        
        ax2.set_title('Zonas de Remate', fontsize=16, pad=20, weight='bold')
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"Error generando visualizaciones: {str(e)}")
