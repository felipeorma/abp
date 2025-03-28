import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import datetime




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
    ], key=lambda x: x.split()[-1]) + ["Marco Carducci", "Rival"]

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
        datos["Fecha"] = st.date_input("Fecha", value=datetime.date.today())

    # Tiempo de juego
    with st.container(border=True):
        st.markdown("### ⏱️ Tiempo de Juego")
        col1, col2 = st.columns(2)
        periodo = col1.selectbox("Periodo", ["1T", "2T"])

        if periodo == "1T":
            minutos = [str(x) for x in range(0, 46)] + ["45+"]
        else:
            minutos = [str(x) for x in range(45, 91)] + ["90+"]

        minuto_str = col2.selectbox("Minuto", minutos)
        datos["Minuto"] = 46 if "45+" in minuto_str else 91 if "90+" in minuto_str else int(minuto_str)
        datos["Periodo"] = periodo

    # Tipo de acción
    # Tipo de acción
    with st.container(border=True):
       st.markdown("### ⚽ Acción")
       col1, col2, col3 = st.columns(3)  # nueva columna para ejecutor
       datos["Acción"] = col1.selectbox("Tipo de acción", ["Tiro libre", "Córner", "Lateral", "Penal"], key="accion_key")
       datos["Equipo"] = col2.selectbox("Equipo ejecutor", ["Cavalry FC", "Rival"])

       if datos["Equipo"] == "Cavalry FC":
           datos["Ejecutor"] = col3.selectbox("Ejecutor", jugadores)
       else:
           datos["Ejecutor"] = "Rival"
           col3.text_input("Ejecutor", value="Rival", disabled=True)
    # Detalles de ejecución
    with st.container(border=True):
        st.markdown("### 🎯 Detalles de Ejecución")
        st.image("https://github.com/felipeorma/abp/blob/main/MedioCampo_enumerado.JPG?raw=true", use_column_width=True)

        if datos["Acción"] == "Penal":
            datos["Zona Saque"] = "Penal"
            datos["Zona Remate"] = "Penal"
            datos["Primer Contacto"] = "N/A"
            datos["Parte Cuerpo"] = "N/A"
            datos["Segundo Contacto"] = ""
            st.info("Configuración automática para penales")
        else:
            col1, col2 = st.columns(2)

            # Zona de saque condicionada si es córner
            if datos["Acción"] == "Córner":
                zona_opciones_saque = [1, 2]
            else:
                zona_opciones_saque = [z for z in zonas if z != "Penal"]

            datos["Zona Saque"] = col1.selectbox("Zona de saque", zona_opciones_saque)
            datos["Zona Remate"] = col2.selectbox("Zona de remate", [z for z in zonas if z != "Penal"])

            opciones_contacto = jugadores + ["Oponente"]
            datos["Primer Contacto"] = st.selectbox("Primer contacto", opciones_contacto)
            datos["Parte Cuerpo"] = st.selectbox("Parte del cuerpo", ["Cabeza","Otro", "Pie"])
            segundo_contacto = st.selectbox("Segundo contacto (opcional)", ["Ninguno"] + opciones_contacto)
            datos["Segundo Contacto"] = segundo_contacto if segundo_contacto != "Ninguno" else ""

    # Resultados
    with st.container(border=True):
        st.markdown("### 📊 Resultados")
        col1, col2 = st.columns(2)

        datos["Gol"] = col1.selectbox("¿Gol?", ["No", "Sí"], key="gol_key")

        # Forzar Resultado = Gol si Gol = Sí
        if st.session_state.get("gol_key") == "Sí":
            datos["Resultado"] = "Gol"
            col1.text_input("Resultado final", value="Gol", disabled=True)
        else:
            datos["Resultado"] = col1.selectbox(
                "Resultado final",
                ["Gol", "Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco"]
            )

        datos["Perfil"] = col2.selectbox("Perfil ejecutor", ["Hábil", "No hábil"])
        datos["Estrategia"] = col2.selectbox("Estrategia", ["Sí", "No"])
        datos["Tipo Ejecución"] = col2.selectbox("Tipo de ejecución", ["Centro", "Pase corto", "Disparo directo"])

    return datos if st.form_submit_button("✅ Registrar Acción") else None

def procesar_registro(datos):
    st.session_state.registro.append(datos)
    st.success("Acción registrada exitosamente! ⚽")  

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
            st.warning("🚨 No hay datos para visualizar con los filtros actuales")
            return

        # Procesar coordenadas
        df = df.copy()
        df["coords_saque"] = df["Zona Saque"].map(zonas)
        df["coords_remate"] = df["Zona Remate"].map(zonas)
        df = df.dropna(subset=["coords_saque", "coords_remate"])
        
        # Convertir coordenadas a columnas separadas
        df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
        df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)
        
        # Configuración del campo (original)
        pitch = VerticalPitch(
            pitch_type='statsbomb',
            pitch_color='grass',
            line_color='white',
            half=True,
            goal_type='box',
            linewidth=1.5
        )

        # Parámetros clave para expansión del heatmap
        heatmap_params = {
            'cmap': 'Greens',
            'levels': 100,
            'fill': True,
            'alpha': 0.7,
            'bw_adjust': 0.48,  # Control principal de expansión
            'thresh': 0.01,      # Mostrar áreas de baja densidad
            'zorder': 2
        }

        # ========== HEATMAP DE SAQUES ==========
        fig1, ax1 = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax1)
        
        # Gráfico de densidad para saques
        pitch.kdeplot(
            df['x_saque'], 
            df['y_saque'],
            ax=ax1,
            **heatmap_params
        )
        
        # Configuración visual
        ax1.set_title('Distribución de Saques', 
                     fontsize=16, 
                     pad=20,
                     fontweight='bold')
        
        st.pyplot(fig1)

        # ========== HEATMAP DE REMATES ==========
        fig2, ax2 = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax2)
        
        # Cambiar colores para remates
        heatmap_params['cmap'] = 'Reds'
        
        # Gráfico de densidad para remates
        pitch.kdeplot(
            df['x_remate'], 
            df['y_remate'],
            ax=ax2,
            **heatmap_params
        )
        
        ax2.set_title('Zonas de Remate', 
                     fontsize=16, 
                     pad=20,
                     fontweight='bold')
        
        st.pyplot(fig2)

        # ========== DESCARGAR DATOS ==========
        csv = df.drop(columns=["coords_saque", "coords_remate", 
                             "x_saque", "y_saque", 
                             "x_remate", "y_remate"]).to_csv(index=False).encode('utf-8')
        
        st.download_button(
            "⬇️ Descargar CSV Filtrado",
            csv,
            "acciones_filtradas.csv",
            "text/csv",
            key='download-csv'
        )

    except Exception as e:
        st.error(f"🔥 Error crítico al generar visualizaciones: {str(e)}")
