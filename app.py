# Importar las librerías necesarias
import streamlit as st
import pandas as pd
import os
from mplsoccer import Pitch
import matplotlib.pyplot as plt
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Configurar el estilo de la página debe ser la primera llamada a Streamlit
st.set_page_config(layout="wide")

def configurar_estilo():
    # Estilos CSS personalizados
    st.markdown(
        """
        <style>
        /* Estilos generales */
        .reportview-container {
            background: #1f1f1f;
            color: white;
        }
        .sidebar .sidebar-content {
            background: #333333;
            color: white;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
        }
        /* Centrar el contenido principal */
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def mostrar_campo():
    st.title("Player Recruitment Needs / Necesidades de Incorporación de Jugadores ")
    pitch = Pitch(pitch_color='#aabb97', line_color='white', stripe=True)
    fig, ax = pitch.draw()
    return fig





def mostrar_login(CONTRASENA_CORRECTA):
    # Función para mostrar la pantalla de inicio de sesión en la barra lateral
    st.sidebar.title("Login / Inicio de Sesión")
    with st.sidebar.form(key='login_form'):
        contraseña = st.text_input("Password / Introduce la contraseña", type="password")
        iniciar_sesion = st.form_submit_button("Login / Iniciar sesión")
        if iniciar_sesion:
            if contraseña == CONTRASENA_CORRECTA:
                st.session_state['sesion_iniciada'] = True
                st.sidebar.success("¡Inicio de sesión exitoso!")
            else:
                st.sidebar.error("Contraseña incorrecta. Acceso denegado.")

def add_watermark(canvas, doc):
    # Función para agregar la marca de agua (tu nombre o licencia)
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 20)  # Aumenta el tamaño de la fuente
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setFillColor(colors.lightgrey)
    width, height = letter

    # Texto de la marca de agua (nombre o licencia)
    watermark_text = "Jose Maria Martin Nuñez - Licence FIFA Nº 202406-6950"

    # Dibujar la marca de agua repetida en varias posiciones
    step_x = 250  # Distancia entre cada marca de agua en el eje x
    step_y = 150  # Distancia entre cada marca de agua en el eje y

    for x in range(0, int(width), step_x):
        for y in range(0, int(height), step_y):
            canvas.saveState()
            canvas.translate(x, y)
            canvas.rotate(45)  # Rotar la marca de agua en diagonal
            canvas.drawCentredString(0, 0, watermark_text)
            canvas.restoreState()

    canvas.restoreState()

def generar_pdf(datos, idioma):
    # Función para generar el PDF con los datos
    doc = SimpleDocTemplate("report.pdf", pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    custom_style = ParagraphStyle(
        name='CustomStyle',
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=10,
        spaceBefore=10,
        alignment=1  # Centrado
    )

    # Título principal
    if idioma == 'English':
        title = Paragraph("Report on club requirements", styles['Title'])
    else:
        title = Paragraph("Informe sobre requerimientos de futbolistas", styles['Title'])
    elements.append(title)

    # Añadir un espaciador
    elements.append(Spacer(1, 12))

    # Tabla de datos
    data = []
    for key, value in datos.items():
        data.append([
            Paragraph(f"<b>{key}</b>", styles['Normal']),
            Paragraph(str(value), styles['Normal'])
        ])

    # Crear la tabla con las columnas ajustadas
    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Pie de página (opcional)
    footer = Paragraph(
        "José María Martín Núñez - FIFA FOOTBALL AGENT - Licence number: 202406-6950",
        custom_style
    )
    elements.append(footer)

    # Generar el PDF con la marca de agua
    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
    with open("report.pdf", "rb") as pdf_file:
        return pdf_file.read()

def guardar_datos(datos, archivo="informes_jugadores.csv"):
    # Función para guardar los datos en un archivo CSV
    if not os.path.exists(archivo):
        df = pd.DataFrame(columns=datos.keys())  # Crear archivo si no existe
    else:
        df = pd.read_csv(archivo)

    # Usar pd.concat() en lugar de append
    df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_csv(archivo, index=False)

def reset_form():
    # Función para resetear los campos del formulario
    for key in ['jugador', 'agente', 'url_transfermarkt']:
        st.session_state[key] = ""

def main():
    configurar_estilo()

    # Contraseña correcta definida
    CONTRASENA_CORRECTA = "240683"

    # Variable para mantener el estado de la sesión
    if 'sesion_iniciada' not in st.session_state:
        st.session_state['sesion_iniciada'] = False

    # Mostrar login si no se ha iniciado sesión
    if not st.session_state['sesion_iniciada']:
        mostrar_login(CONTRASENA_CORRECTA)
        # Mostrar el campo de fútbol centrado en la página principal
        st.markdown("<div class='centered'>", unsafe_allow_html=True)
        fig = mostrar_campo()
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()  # Detener la ejecución hasta que se inicie sesión


    # Inicializar variables en session_state para evitar errores
    session_vars = {
        'jugador': "",
        'agente': "",
        'url_transfermarkt': "",
        'position': "Goalkeeper",
        'ideal_age': "Under-23",
        'competitive_experience': "Category 1",
        'preferred_nationality': "Afghanistan",
        'style_of_play': [],
        'salary_range': "Less than 50,000€",
        'transfer_type': "Loan",
        'immediate_needs': "",
        'jugadores_observados': []
    }

    for key, value in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Cargar la imagen de tu licencia FIFA
    st.sidebar.image("licencia.png")  # Imagen en la barra lateral

    # Añadir nombre y licencia con iconos
    st.sidebar.markdown("<h3>José María Martín Núñez</h3>", unsafe_allow_html=True)
    st.sidebar.markdown("<h4>Licencia FIFA Nº: 202406-6950</h4>", unsafe_allow_html=True)

    # Añadir email y teléfono con iconos (reemplazados con marcadores de posición)
    st.sidebar.markdown("📧 **Email:** [email@example.com]")
    st.sidebar.markdown("📱 **Teléfono:** [123-456-7890]")

    # Añadir otras redes sociales o información si lo deseas
    st.sidebar.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/jos%C3%A9-m-mart%C3%ADn-6b805728/)")

    # Opciones de idioma, por defecto en inglés
    idioma = st.sidebar.radio("Select the language / Seleccione el idioma", ("English", "Español"), index=0)

    # Lista de las 211 federaciones de FIFA o países
    federaciones_fifa = [
        "Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", 
        "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", 
        "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", 
        "British Virgin Islands", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", 
        "Cape Verde", "Cayman Islands", "Central African Republic", "Chad", "Chile", "China PR", "Chinese Taipei", "Colombia", 
        "Comoros", "Congo", "Congo DR", "Cook Islands", "Costa Rica", "Croatia", "Cuba", "Curaçao", "Cyprus", "Czech Republic", 
        "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "England", "Equatorial Guinea", 
        "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Faroe Islands", "Fiji", "Finland", "France", "Gabon", "Gambia", "Georgia", 
        "Germany", "Ghana", "Gibraltar", "Greece", "Grenada", "Guam", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", 
        "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Israel", "Italy", "Ivory Coast", 
        "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea DPR", "Korea Republic", "Kosovo", "Kuwait", 
        "Kyrgyz Republic", "Lao People's Democratic Republic", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", 
        "Lithuania", "Luxembourg", "Macau", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Mauritania", 
        "Mauritius", "Mexico", "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", 
        "Namibia", "Nauru", "Nepal", "Netherlands", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", 
        "Northern Ireland", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", 
        "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Ireland", "Romania", "Russia", "Rwanda", 
        "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", 
        "Saudi Arabia", "Scotland", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", 
        "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", 
        "Switzerland", "Syria", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", 
        "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United States of America", 
        "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Wales", "Yemen", "Zambia", "Zimbabwe"
    ]

    # Función para resetear los campos del formulario
    def reset_form():
        for key in ['jugador', 'agente', 'url_transfermarkt']:
            st.session_state[key] = ""

    # Definir el formulario en inglés o español
    if idioma == "English":
        # Formulario en inglés
        st.subheader("Player Recruitment Needs")

        # 1. Positions to Strengthen
        club_name = st.text_input("Name of the Club", key='club_name')

        # Market Window
        ventana_mercado = st.selectbox(
            "Market Window to reinforce",
            ["Summer Transfer Window", "Winter Transfer Window", "General"],
            key='ventana_mercado'
        )

        with st.expander("1. Positions to strengthen"):
            position = st.selectbox(
                "Select the priority position you want to strengthen",
                ["Goalkeeper", "Center Back", "Left Back", "Right Back",
                 "Defensive Midfielder", "Attacking Midfielder", "Left Winger",
                 "Right Winger", "Striker"],
                 key='position'
            )

        # 2. Desired Player Profile
        with st.expander("2. Desired player profile"):
            col1, col2 = st.columns(2)
            with col1:
                ideal_age = st.selectbox(
                    "Ideal Age",
                    ["Under-23", "Between 23-28 years", "Over 28 years"],
                    key='ideal_age'
                )
            with col2:
                competitive_experience = st.multiselect(
                    "Competitive Experience",
                    ["Category 1", "Category 2", "Category 3", "Category 4",
                     "Category 5", "Other Categories"],
                    key='competitive_experience'
                )
            preferred_nationality = st.multiselect(
                "Preferred Nationality (Optional)",
                federaciones_fifa,
                key='preferred_nationality'
            )

            # Style of Play
            style_of_play = st.multiselect(
                "Select the key characteristics of the playing style",
                ["Technical", "Physical", "Versatile", "Specialized in dribbling",
                 "High pressing ability", "Build-up play from the back",
                 "Vision", "Good long pass", "1-on-1 capability",
                 "Movement and positioning"],
                 key='style_of_play'
            )

        # 3. Budget Availability
        with st.expander("3. Budget availability"):
            salary_range = st.selectbox(
                "Expected Salary Range",
                ["Less than 50,000€", "Between 50,000€ and 100,000€",
                 "More than 100,000€", "More than 500,000€",
                 "Between 500,000€ and 1,000,000€", "More than 1,000,000€",
                 "No salary limit"],
                 key='salary_range'
            )
            transfer_type = st.selectbox(
                "Type of Transfer",
                ["Loan", "Loan with option to buy", "Permanent signing"],
                key='transfer_type'
            )

        # 4. Immediate Needs
        with st.expander("4. Immediate needs"):
            immediate_needs = st.text_area(
                "Are there any positions that need urgent reinforcement? (Specify position and reason)",
                key='immediate_needs'
            )

        # 5. Current Contract
        with st.expander("5. Current contract"):
            free_agent = st.radio(
                "Do you want the player to be a Free Agent?",
                ("Yes", "No"),
                key='free_agent'
            )

            if free_agent == "No":
                contract_end = st.text_input(
                    "Enter the amount the club can afford to pay for the player",
                    key='contract_end'
                )
            else:
                contract_end = "Unspecified"

        # 6. Injury History
        with st.expander("6. Injury History"):
            lesion_historial = st.text_area(
                "Describe the player's injury history (if applicable)",
                key='lesion_historial'
            )

        # 7. Performance Statistics
        with st.expander("7. Performance Statistics"):
            periodo = st.selectbox("Time Period", ["Last 10 Matches", "Last Season", "Total"])

            # Goals
            goles_totales = st.number_input("Total Goals", min_value=0, step=1, key='goles_totales')
            if goles_totales > 0:
                goles_por_partido = goles_totales / (10 if periodo == "Last 10 Matches" else 38)
                st.write(f"Goals per match: {goles_por_partido:.2f}")
            else:
                goles_por_partido = 0

            # Assists
            asistencias_totales = st.number_input("Total Assists", min_value=0, step=1, key='asistencias_totales')
            if asistencias_totales > 0:
                asistencias_por_partido = asistencias_totales / (10 if periodo == "Last 10 Matches" else 38)
                st.write(f"Assists per match: {asistencias_por_partido:.2f}")
            else:
                asistencias_por_partido = 0

            # Interceptions
            intercepciones_totales = st.number_input("Total Interceptions", min_value=0, step=1, key='intercepciones_totales')
            if intercepciones_totales > 0:
                intercepciones_por_partido = intercepciones_totales / (10 if periodo == "Last 10 Matches" else 38)
                st.write(f"Interceptions per match: {intercepciones_por_partido:.2f}")
            else:
                intercepciones_por_partido = 0

            # Save Percentage (if goalkeeper)
            is_goalkeeper = st.radio("Is the player a goalkeeper?", ("Yes", "No"), key='is_goalkeeper')
            if is_goalkeeper == "Yes":
                paradas_totales = st.number_input("Total Saves", min_value=0, step=1, key='paradas_totales')
                total_disparos = st.number_input("Total Shots Faced", min_value=1, step=1, key='total_disparos')
                if paradas_totales > 0:
                    porcentaje_paradas = (paradas_totales / total_disparos) * 100
                    st.write(f"Save Percentage: {porcentaje_paradas:.2f}%")
                else:
                    porcentaje_paradas = 0
            else:
                porcentaje_paradas = "N/A"

        # 8. International Adaptability
        with st.expander("8. International Adaptability"):
            adaptabilidad_internacional = st.radio(
                "Has the player played in international leagues?",
                ("Yes", "No"),
                key='adaptabilidad_internacional'
            )

        # 9. Availability to Travel/Relocate
        with st.expander("9. Availability to Travel/Relocate"):
            disponibilidad_viajar = st.radio(
                "Is the player available to travel/relocate?",
                ("Yes", "No"),
                key='disponibilidad_viajar'
            )

        # 10. Languages Spoken
        with st.expander("10. Languages Spoken"):
            idiomas = st.text_area("Languages spoken by the player", key='idiomas')

        # 11. Market Value
        with st.expander("11. Market Value"):
            valor_mercado = st.text_input("Estimated current market value (if applicable)", key='valor_mercado')

        # 12. Positional Flexibility
        with st.expander("12. Positional Flexibility"):
            flexibilidad_posicional = st.text_area(
                "Additional positions the player can play",
                key='flexibilidad_posicional'
            )

        # 13. Scouting Recommendation
        with st.expander("13. Scouting Recommendation"):
            scouting_recomendacion = st.text_area(
                "Scouting evaluation of the player's potential",
                key='scouting_recomendacion'
            )

        # 14. International Competitions
        with st.expander("14. Participation in International Competitions"):
            competiciones_internacionales = st.text_area(
                "International competitions the player has participated in",
                key='competiciones_internacionales'
            )

        # 15. Attitude and Character
        with st.expander("15. Attitude and Character"):
            actitud_caracter = st.text_area(
                "Evaluation of the player's attitude and character",
                key='actitud_caracter'
            )

        # 16. Media or Social Media Presence
        with st.expander("16. Media or Social Media Presence"):
            seguimiento_medios = st.text_area(
                "Does the player have significant media or social media presence?",
                key='seguimiento_medios'
            )

        # Botón para enviar y generar el informe
        if st.button("Download Report"):
            datos = {
                "Name of Club": club_name,
                "Market Window to Reinforce": ventana_mercado,
                "Position": position,
                "Ideal Age": ideal_age,
                "Competitive Experience": competitive_experience,
                "Preferred Nationality": st.session_state['preferred_nationality'],
                "Style of Play": ", ".join(st.session_state['style_of_play']),
                "Salary Range": st.session_state['salary_range'],
                "Transfer Type": st.session_state['transfer_type'],
                "Immediate Needs": st.session_state['immediate_needs'] or "N/A",
                "Free Agent": free_agent,
                "Contract End Date": contract_end,
                "Injury History": lesion_historial,
                "Performance Statistics - Goals": goles_totales,
                "Goals per Match": goles_por_partido,
                "Performance Statistics - Assists": asistencias_totales,
                "Assists per Match": asistencias_por_partido,
                "Performance Statistics - Interceptions": intercepciones_totales,
                "Interceptions per Match": intercepciones_por_partido,
                "Save Percentage": porcentaje_paradas,
                "International Adaptability": adaptabilidad_internacional,
                "Availability to Travel/Relocate": disponibilidad_viajar,
                "Languages": idiomas,
                "Market Value": valor_mercado,
                "Positional Flexibility": flexibilidad_posicional,
                "Scouting Recommendation": scouting_recomendacion,
                "International Competitions": competiciones_internacionales,
                "Attitude and Character": actitud_caracter,
                "Media or Social Media Presence": seguimiento_medios
            }
            guardar_datos(datos)
            st.success("Report successfully submitted and saved.")
            st.session_state['jugadores_observados'] = []

            # Generar PDF
            pdf_data = generar_pdf(datos, idioma)

            # Botón para descargar el PDF
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name="report.pdf",
                mime="application/pdf"
            )

    else:
        # Formulario en español
        st.subheader("Necesidades de Incorporación de Jugadores")

        # 1. Posiciones a Refuerzar
        nombre_club = st.text_input("Nombre del club", key='nombre_club')

        # Ventana de Mercado
        ventana_mercado = st.selectbox(
            "Ventana a reforzar",
            ["Ventana de Transferencia Verano", "Ventana de Transferencia Invierno", "General"],
            key='ventana_mercado'
        )

        with st.expander("1. Posiciones a reforzar"):
            position = st.selectbox(
                "Seleccione la posición prioritaria que desea reforzar",
                ["Portero", "Defensa Central", "Lateral Izquierdo", "Lateral Derecho",
                 "Centrocampista Defensivo", "Centrocampista Ofensivo", "Extremo Izquierdo",
                 "Extremo Derecho", "Delantero"],
                 key='position'
            )

        # 2. Perfil del Jugador Deseado
        with st.expander("2. Perfil del Jugador deseado"):
            col1, col2 = st.columns(2)
            with col1:
                ideal_age = st.selectbox(
                    "Edad Ideal",
                    ["Sub-23", "Entre 23-28 años", "Más de 28 años"],
                    key='ideal_age'
                )
            with col2:
                competitive_experience = st.multiselect(
                    "Experiencia Competitiva",
                    ["Categoría 1", "Categoría 2", "Categoría 3", "Categoría 4",
                     "Categoría 5", "Otras Categorías"],
                    key='competitive_experience'
                )
            preferred_nationality = st.multiselect(
                "Nacionalidad Preferente (Opcional)",
                federaciones_fifa,
                key='preferred_nationality'
            )

            # Estilo de Juego
            style_of_play = st.multiselect(
                "Seleccione las características clave del estilo de juego",
                ["Técnico", "Físico", "Versátil", "Especializado en desborde",
                 "Capacidad de presión alta", "Construcción desde el fondo",
                 "Visión", "Buen pase largo", "Capacidad en 1 vs 1",
                 "Desmarque y movilidad"],
                 key='style_of_play'
            )

        # 3. Disponibilidad Presupuestaria
        with st.expander("3. Disponibilidad presupuestaria"):
            salary_range = st.selectbox(
                "Rango de salario esperado",
                ["Menos de 50,000€", "Entre 50,000€ y 100,000€",
                 "Más de 100,000€", "Más de 500,000€", "Entre 500,000€ y 1,000,000€",
                 "Más de 1,000,000€", "Sin límite salarial"],
                 key='salary_range'
            )
            transfer_type = st.selectbox(
                "Tipología de incorporación",
                ["Cesión", "Cesión con opción de compra", "Fichaje definitivo"],
                key='transfer_type'
            )

        # 4. Necesidades Inmediatas
        with st.expander("4. Necesidades inmediatas"):
            immediate_needs = st.text_area(
                "¿Existen posiciones que necesitan ser reforzadas de manera urgente? (Describa posición y motivo)",
                key='immediate_needs'
            )

        # 5. Contrato Actual
        with st.expander("5. Contrato actual"):
            agente_libre = st.radio(
                "¿Quieren el jugador Agente Libre?",
                ("Sí", "No"),
                key='agente_libre'
            )

            if agente_libre == "No":
                contract_end = st.text_input(
                    "Ingrese lo que puede llegar a pagar el club por el jugador/a",
                    key='contract_end'
                )
            else:
                contract_end = "Sin especificar"

        # 6. Historial de Lesiones
        with st.expander("6. Historial de Lesiones"):
            lesion_historial = st.text_area(
                "Describa el historial de lesiones del jugador (si aplica)",
                key='lesion_historial'
            )

        # 7. Estadísticas de Rendimiento
        with st.expander("7. Estadísticas de Rendimiento"):
            periodo = st.selectbox("Periodo de Tiempo", ["Últimos 10 partidos", "Última temporada", "Total"])

            # Goles
            goles_totales = st.number_input("Total de goles", min_value=0, step=1, key='goles_totales')
            if goles_totales > 0:
                goles_por_partido = goles_totales / (10 if periodo == "Últimos 10 partidos" else 38)
                st.write(f"Goles por partido: {goles_por_partido:.2f}")
            else:
                goles_por_partido = 0

            # Asistencias
            asistencias_totales = st.number_input("Total de asistencias", min_value=0, step=1, key='asistencias_totales')
            if asistencias_totales > 0:
                asistencias_por_partido = asistencias_totales / (10 if periodo == "Últimos 10 partidos" else 38)
                st.write(f"Asistencias por partido: {asistencias_por_partido:.2f}")
            else:
                asistencias_por_partido = 0

            # Intercepciones
            intercepciones_totales = st.number_input("Total de intercepciones", min_value=0, step=1, key='intercepciones_totales')
            if intercepciones_totales > 0:
                intercepciones_por_partido = intercepciones_totales / (10 if periodo == "Últimos 10 partidos" else 38)
                st.write(f"Intercepciones por partido: {intercepciones_por_partido:.2f}")
            else:
                intercepciones_por_partido = 0

            # Porcentaje de paradas (si es portero)
            is_goalkeeper = st.radio("¿El jugador es portero?", ("Sí", "No"), key='is_goalkeeper')
            if is_goalkeeper == "Sí":
                paradas_totales = st.number_input("Total de paradas", min_value=0, step=1, key='paradas_totales')
                total_disparos = st.number_input("Total de disparos enfrentados", min_value=1, step=1, key='total_disparos')
                if paradas_totales > 0:
                    porcentaje_paradas = (paradas_totales / total_disparos) * 100
                    st.write(f"Porcentaje de paradas: {porcentaje_paradas:.2f}%")
                else:
                    porcentaje_paradas = 0
            else:
                porcentaje_paradas = "N/A"

        # 8. Adaptabilidad Internacional
        with st.expander("8. Adaptabilidad Internacional"):
            adaptabilidad_internacional = st.radio(
                "¿Ha jugado en ligas internacionales?",
                ("Sí", "No"),
                key='adaptabilidad_internacional'
            )

        # 9. Disponibilidad para Viajar/Mudarse
        with st.expander("9. Disponibilidad para Viajar/Mudarse"):
            disponibilidad_viajar = st.radio(
                "¿Está disponible para viajar/mudarse?",
                ("Sí", "No"),
                key='disponibilidad_viajar'
            )

        # 10. Idiomas que habla
        with st.expander("10. Idiomas que habla"):
            idiomas = st.text_area("Idiomas que el jugador habla", key='idiomas')

        # 11. Valor de Mercado
        with st.expander("11. Valor de Mercado"):
            valor_mercado = st.text_input("Valor de mercado actual estimado (si aplica)", key='valor_mercado')

        # 12. Flexibilidad Posicional
        with st.expander("12. Flexibilidad Posicional"):
            flexibilidad_posicional = st.text_area(
                "Posiciones adicionales en las que puede jugar",
                key='flexibilidad_posicional'
            )

        # 13. Recomendación de Scouting
        with st.expander("13. Recomendación de Scouting"):
            scouting_recomendacion = st.text_area(
                "Evaluación del scouting sobre el potencial del jugador",
                key='scouting_recomendacion'
            )

        # 14. Participación en Competiciones Internacionales
        with st.expander("14. Participación en Competiciones Internacionales"):
            competiciones_internacionales = st.text_area(
                "Competiciones internacionales en las que ha participado",
                key='competiciones_internacionales'
            )

        # 15. Actitud y Carácter
        with st.expander("15. Actitud y Carácter"):
            actitud_caracter = st.text_area(
                "Evaluación de actitud y carácter",
                key='actitud_caracter'
            )

        # 16. Seguimiento en Medios o Redes Sociales
        with st.expander("16. Seguimiento en Medios o Redes Sociales"):
            seguimiento_medios = st.text_area(
                "¿Tiene el jugador una presencia relevante en redes sociales o medios?",
                key='seguimiento_medios'
            )

        # Botón para enviar y generar el informe
        if st.button("Descargar Informe"):
            datos = {
                "Nombre del Club": nombre_club,
                "Ventana a Reforzar": ventana_mercado,
                "Posición": position,
                "Edad Ideal": ideal_age,
                "Experiencia Competitiva": competitive_experience,
                "Nacionalidad Preferente": st.session_state['preferred_nationality'],
                "Estilo de Juego": ", ".join(st.session_state['style_of_play']),
                "Rango Salarial": st.session_state['salary_range'],
                "Tipología de Incorporación": st.session_state['transfer_type'],
                "Necesidad Inmediata": st.session_state['immediate_needs'] or "N/A",
                "Agente Libre": agente_libre,
                "Fecha de Fin de Contrato": contract_end,
                "Historial de Lesiones": lesion_historial,
                "Estadísticas de Rendimiento - Goles": goles_totales,
                "Goles por Partido": goles_por_partido,
                "Estadísticas de Rendimiento - Asistencias": asistencias_totales,
                "Asistencias por Partido": asistencias_por_partido,
                "Estadísticas de Rendimiento - Intercepciones": intercepciones_totales,
                "Intercepciones por Partido": intercepciones_por_partido,
                "Porcentaje de Paradas": porcentaje_paradas,
                "Adaptabilidad Internacional": adaptabilidad_internacional,
                "Disponibilidad para Viajar/Mudarse": disponibilidad_viajar,
                "Idiomas": idiomas,
                "Valor de Mercado": valor_mercado,
                "Flexibilidad Posicional": flexibilidad_posicional,
                "Recomendación de Scouting": scouting_recomendacion,
                "Competiciones Internacionales": competiciones_internacionales,
                "Actitud y Carácter": actitud_caracter,
                "Seguimiento en Redes Sociales": seguimiento_medios
            }
            guardar_datos(datos)
            st.success("Informe enviado y guardado exitosamente.")
            st.session_state['jugadores_observados'] = []

            # Generar PDF
            pdf_data = generar_pdf(datos, idioma)

            # Botón para descargar el PDF
            st.download_button(
                label="Descargar PDF",
                data=pdf_data,
                file_name="informe.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
