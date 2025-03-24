# ... (parte inicial del código se mantiene igual)

# Formulario de registro
st.subheader("📋 Registrar nueva acción")
match_day = st.selectbox("🗓️ Jornada", ["Rueda 1", "Rueda 2", "Rueda 3", "Rueda 4"])
oponente = st.selectbox("🆚 Rival", equipos_cpl)
field = st.selectbox("📍 Condición de campo", ["Local", "Visitante"])
tipo_accion = st.selectbox("⚙️ Tipo de acción", ["Tiro libre", "Córner", "Lateral", "Penal"])
equipo = st.selectbox("🏳️ Equipo que ejecutó", ["Cavalry FC", "Rival"])

# Selección de periodo y minuto con opciones extendidas
periodo = st.selectbox("⏱️ Periodo", ["1T", "2T"])
if periodo == "1T":
    minuto_opts = [str(x) for x in range(0, 46)] + ["45+"]
else:
    minuto_opts = [str(x) for x in range(45, 91)] + ["90+"]
    
minuto_str = st.selectbox("⏱️ Minuto", minuto_opts)

# Lógica condicional para zonas y contactos
if tipo_accion == "Penal":
    zona_saque = "Penal"
    st.selectbox("📍 Zona de saque (automático)", ["Penal"], disabled=True)
    zona_remate = "Penal"
    st.selectbox("🎯 Zona de remate (automático)", ["Penal"], disabled=True)
    
    # Ocultar campos de contacto para penales
    primer_contacto = "N/A"
    cuerpo1 = "N/A"
    segundo_contacto = "N/A"
    
elif tipo_accion == "Córner":
    zona_saque = st.selectbox("📍 Zona de saque (solo córneres)", [1, 2])
    zona_remate = st.selectbox("🎯 Zona de remate", [key for key in zonas_coords.keys() if key != "Penal"])
    
    # Campos normales de contacto
    primer_contacto = st.selectbox("🤝 Primer contacto (jugador)", jugadores_cavalry + ["Rival"])
    cuerpo1 = st.selectbox("🦵 Parte del cuerpo (1er contacto)", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
    segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")
    
else:
    available_zones = [key for key in zonas_coords.keys() if key != "Penal"]
    zona_saque = st.selectbox("📍 Zona de saque", available_zones)
    zona_remate = st.selectbox("🎯 Zona de remate", available_zones)
    
    # Campos normales de contacto
    primer_contacto = st.selectbox("🤝 Primer contacto (jugador)", jugadores_cavalry + ["Rival"])
    cuerpo1 = st.selectbox("🦵 Parte del cuerpo (1er contacto)", ["Cabeza", "Pie derecho", "Pie izquierdo", "Tronco", "Otro"])
    segundo_contacto = st.text_input("📌 Segundo contacto (opcional)")

# Resto de campos comunes
ejecutor = st.selectbox("👟 Ejecutante", jugadores_cavalry)
gol = st.selectbox("🥅 ¿Terminó en gol?", ["No", "Sí"])
resultado = st.selectbox("🎯 Resultado final de la jugada", ["Despeje", "Posesión rival", "Disparo desviado", "Disparo al arco", "Gol"])
perfil = st.selectbox("🦶 Perfil del ejecutante", ["Hábil", "No hábil"])
estrategia = st.selectbox("📈 ¿Fue jugada estratégica?", ["Sí", "No"])
tipo_pase = st.selectbox("📨 Tipo de ejecución", ["Centro", "Pase corto", "Disparo directo"])

# Convertir minutos extendidos a valores numéricos
if "45+" in minuto_str:
    minuto = 46
elif "90+" in minuto_str:
    minuto = 91
else:
    minuto = int(minuto_str)

if st.button("✅ Agregar acción"):
    registro_data = {
        "MatchDay": match_day,
        "Opponent": oponente,
        "Field": field,
        "Action Type": tipo_accion,
        "Team": equipo,
        "minuto": minuto,
        "Period": periodo,
        "zona_saque": zona_saque,
        "zona_remate": zona_remate,
        "Player Taker": ejecutor,
        "Goal": gol,
        "Player 1st Contact": primer_contacto,
        "Body Part 1st Contact": cuerpo1,
        "2nd Contact": segundo_contacto,
        "Play Outcome": resultado,
        "Taker Profile": perfil,
        "Strategic": estrategia,
        "Direct / Short Pass": tipo_pase
    }
    
    st.session_state.registro.append(registro_data)
    st.success("Acción registrada correctamente ✅")

# ... (el resto del código se mantiene igual)