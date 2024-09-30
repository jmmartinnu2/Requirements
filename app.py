import streamlit as st
import pandas as pd
import os
from io import StringIO
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

# Configurar tema oscuro
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
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
    </style>
    """, unsafe_allow_html=True
)

# Función personalizada de FPDF para trabajar con UTF-8
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Player Recruitment Report", 0, 1, "C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(4)

    def chapter_body(self, body):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)

# Función para agregar la marca de agua (tu nombre o licencia)
def add_watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 20)
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setFillColor(colors.lightgrey)
    width, height = letter

    # Texto de la marca de agua (nombre o licencia)
    watermark_text = "Jose Maria Martin Nuñez - Licence FIFA Nº 202406-6950"

    # Dibujar la marca de agua repetida en varias posiciones
    for x in range(0, int(width), 150):  # Cada 150 unidades en el eje x
        for y in range(0, int(height), 200):  # Cada 200 unidades en el eje y
            canvas.saveState()
            canvas.translate(x, y)
            canvas.rotate(45)  # Rotar la marca de agua en diagonal
            canvas.drawCentredString(0, 0, watermark_text)  # Texto de la marca de agua
            canvas.restoreState()

    canvas.restoreState()

# Función para generar el PDF con mejor diseño visual y sin colores en la tabla
def generar_pdf(datos):
    # Crear el documento PDF
    doc = SimpleDocTemplate("report.pdf", pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Espaciado general
    general_spacer = Spacer(1, 12)

    # Título principal: Nombre de Agente FIFA
    titulo_fifa = Paragraph("Report for FIFA Agent:<br/><b>José Mª Martín Núñez - License: 202406-6950</b>", styles["Title"])
    elements.append(titulo_fifa)
    elements.append(Spacer(1, 12))

    # Línea divisoria
    elements.append(Spacer(1, 6))
    elements.append(Paragraph('<hr width="100%" color="gray" size="1">', styles["Normal"]))

    # Estructura en dos columnas: Claves (a la izquierda) y Valores (a la derecha)
    data = []
    for key, value in datos.items():
        data.append([f"{key}", f"{value}"])

    # Obtener estilos de párrafo
    styles = getSampleStyleSheet()
    style = styles['Normal']  # Definir estilo normal para los párrafos

    # Crear la tabla para organizar los datos en dos columnas, ajustando el tamaño dinámico de las celdas
    table_data = []

    # Recorrer los datos y crear párrafos para cada celda
    for row in data:
        new_row = []
        for cell in row:
            if isinstance(cell, str):  # Si el contenido es texto, convertirlo a párrafo
                new_row.append(Paragraph(cell, style))
            else:
                new_row.append(cell)  # Si no es texto, dejarlo tal cual
        table_data.append(new_row)

    # Crear la tabla con las columnas ajustadas
    table = Table(table_data, colWidths=[150, 300])  # Ajustar los anchos de las columnas según tu necesidad

    # Establecer el estilo de la tabla
    table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Tamaño de fuente ajustado para la tabla
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Líneas negras para la tabla
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear en el medio verticalmente
    ]))

    # Agregar la tabla a los elementos
    elements.append(table)

    # Generar el PDF con la marca de agua (nombre o licencia)
    doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)

    # Leer y devolver el archivo PDF generado
    with open("report.pdf", "rb") as pdf_file:
        return pdf_file.read()

# Inicializar session_state para evitar errores
if 'jugador' not in st.session_state:
    st.session_state['jugador'] = ""
if 'agente' not in st.session_state:
    st.session_state['agente'] = ""
if 'url_transfermarkt' not in st.session_state:
    st.session_state['url_transfermarkt'] = ""
if 'position' not in st.session_state:
    st.session_state['position'] = "Goalkeeper"
if 'ideal_age' not in st.session_state:
    st.session_state['ideal_age'] = "Under-23"
if 'competitive_experience' not in st.session_state:
    st.session_state['competitive_experience'] = "Category 1"
if 'preferred_nationality' not in st.session_state:
    st.session_state['preferred_nationality'] = "Afghanistan"
if 'style_of_play' not in st.session_state:
    st.session_state['style_of_play'] = []
if 'salary_range' not in st.session_state:
    st.session_state['salary_range'] = "Less than 50,000€"
if 'transfer_type' not in st.session_state:
    st.session_state['transfer_type'] = "Loan"
if 'immediate_needs' not in st.session_state:
    st.session_state['immediate_needs'] = ""
if 'jugadores_observados' not in st.session_state:
    st.session_state['jugadores_observados'] = []

# Función para guardar los datos en un archivo CSV
def guardar_datos(datos, archivo="informes_jugadores.csv"):
    if not os.path.exists(archivo):
        df = pd.DataFrame(columns=datos.keys())  # Crear archivo si no existe
    else:
        df = pd.read_csv(archivo)
    
    # Usar pd.concat() en lugar de append
    df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_csv(archivo, index=False)

# Cargar la imagen de tu licencia FIFA
st.sidebar.image("licencia.png")  # Imagen en la barra lateral

# Añadir nombre y licencia con iconos
st.sidebar.markdown("<h3>José María Martín Núñez</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<h4>Licencia FIFA Nº: 202406-6950</h4>", unsafe_allow_html=True)

# Añadir email y teléfono con iconos
st.sidebar.markdown("📧 **Email:** jmnagente@gmail.com")
st.sidebar.markdown("📱 **Teléfono:** +34 645 764853")

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
    st.subheader("Player Recruitment Needs")

    # 1. Positions to Strengthen
    club_name = st.text_input("Name of the Club", key='club_name')
    
    # Campo de selección para Ventana de Mercado
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
            competitive_experience = st.selectbox(
                "Competitive Experience",
                ["Category 1", "Category 2", "Category 3", "Category 4", "Category 5", "Other Categories"],
                key='competitive_experience'
            )
        preferred_nationality = st.multiselect("Preferred Nationality (Optional)", federaciones_fifa, key='preferred_nationality')

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
        immediate_needs = st.text_area("Are there any positions that need urgent reinforcement? (Specify position and reason)", key='immediate_needs')

    # 5. Field to select if the player is a free agent or not
    with st.expander("5. Current contract"):
        free_agent = st.radio(
            "Do you want the player to be a Free Agent?", 
            ("Yes", "No"), 
            key='free_agent'
        )

    # If the player is not a free agent, show field for contract end date
    if free_agent == "No":
        contract_end = st.text_input("Enter the amount the club can afford to pay for the player", key='contract_end')
    else:
        contract_end = "Unspecified"  # If the player is a free agent, no contract end date is required

    # Add new metrics to the form
    # 6. Injury History
    with st.expander("6. Injury History"):
        lesion_historial = st.text_area("Describe the player's injury history (if applicable)", key='lesion_historial')

    # 7. Performance Statistics
    with st.expander("7. Performance Statistics"):
        periodo = st.selectbox("Time Period", ["Last 10 Matches", "Last Season", "Total"])
        
        # Goles
        goles_totales = st.number_input("Total Goals", min_value=0, step=1, key='goles_totales')
        if goles_totales > 0:
            goles_por_partido = goles_totales / (10 if periodo == "Last 10 Matches" else 38)  # 38 es una suposición para una temporada completa
            st.write(f"Goals per match: {goles_por_partido:.2f}")
        else:
            goles_por_partido = 0  # Definir como 0 si no hay goles totales

        # Asistencias
        asistencias_totales = st.number_input("Total Assists", min_value=0, step=1, key='asistencias_totales')
        if asistencias_totales > 0:
            asistencias_por_partido = asistencias_totales / (10 if periodo == "Last 10 Matches" else 38)
            st.write(f"Assists per match: {asistencias_por_partido:.2f}")
        else:
            asistencias_por_partido = 0  # Definir como 0 si no hay asistencias totales

        # Intercepciones
        intercepciones_totales = st.number_input("Total Interceptions", min_value=0, step=1, key='intercepciones_totales')
        if intercepciones_totales > 0:
            intercepciones_por_partido = intercepciones_totales / (10 if periodo == "Last 10 Matches" else 38)
            st.write(f"Interceptions per match: {intercepciones_por_partido:.2f}")
        else:
            intercepciones_por_partido = 0  # Definir como 0 si no hay intercepciones totales

        # Porcentaje de paradas (si es portero)
        is_goalkeeper = st.radio("Is the player a goalkeeper?", ("Yes", "No"), key='is_goalkeeper')
        if is_goalkeeper == "Yes":
            paradas_totales = st.number_input("Total Saves", min_value=0, step=1, key='paradas_totales')
            total_disparos = st.number_input("Total Shots Faced", min_value=1, step=1, key='total_disparos')
            if paradas_totales > 0:
                porcentaje_paradas = (paradas_totales / total_disparos) * 100
                st.write(f"Save Percentage: {porcentaje_paradas:.2f}%")
            else:
                porcentaje_paradas = 0  # Definir como 0 si no hay paradas totales
        else:
            porcentaje_paradas = "N/A"  # Si no es portero, el porcentaje de paradas no aplica

    # 8. International Adaptability
    with st.expander("8. International Adaptability"):
        adaptabilidad_internacional = st.radio("Has the player played in international leagues?", ("Yes", "No"), key='adaptabilidad_internacional')

    # 9. Availability to Travel/Relocate
    with st.expander("9. Availability to Travel/Relocate"):
        disponibilidad_viajar = st.radio("Is the player available to travel/relocate?", ("Yes", "No"), key='disponibilidad_viajar')

    # 10. Language Proficiency
    with st.expander("10. Languages Spoken"):
        idiomas = st.text_area("Languages spoken by the player", key='idiomas')

    # 11. Current Market Value
    with st.expander("11. Market Value"):
        valor_mercado = st.text_input("Estimated current market value (if applicable)", key='valor_mercado')

    # 12. Positional Flexibility
    with st.expander("12. Positional Flexibility"):
        flexibilidad_posicional = st.text_area("Additional positions the player can play", key='flexibilidad_posicional')

    # 13. Scouting Recommendation
    with st.expander("13. Scouting Recommendation"):
        scouting_recomendacion = st.text_area("Scouting evaluation of the player's potential", key='scouting_recomendacion')

    # 14. Participation in International Competitions
    with st.expander("14. Participation in International Competitions"):
        competiciones_internacionales = st.text_area("International competitions the player has participated in", key='competiciones_internacionales')

    # 15. Attitude and Character
    with st.expander("15. Attitude and Character"):
        actitud_caracter = st.text_area("Evaluation of the player's attitude and character", key='actitud_caracter')

    # 16. Media or Social Media Presence
    with st.expander("16. Media or Social Media Presence"):
        seguimiento_medios = st.text_area("Does the player have significant media or social media presence?", key='seguimiento_medios')

    # Si se está usando en inglés:
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
            "Observed Players": st.session_state['jugadores_observados'],
            "Free Agent": free_agent,
            "Contract End Date": contract_end,
            "Injury History": lesion_historial,
            "Performance Statistics - Goals": goles_totales,
            "Performance Statistics - Goals per Match": goles_por_partido,
            "Performance Statistics - Assists": asistencias_totales,
            "Performance Statistics - Assists per Match": asistencias_por_partido,
            "Performance Statistics - Interceptions": intercepciones_totales,
            "Performance Statistics - Interceptions per Match": intercepciones_por_partido,
            "Performance Statistics - Save Percentage": porcentaje_paradas,
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
        pdf_data = generar_pdf(datos)

        # Botón para descargar el PDF
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name="report.pdf",
            mime="application/pdf"
        )

# Formulario en español
else:
    st.subheader("Necesidades de Incorporación de Jugadores")

    # 1. Posiciones a Refuerzar
    nombre_club = st.text_input("Nombre del club", key='nombre_club')

    # Campo de selección para Ventana de Mercado
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
            competitive_experience = st.selectbox(
                "Experiencia Competitiva",
                ["Categoria 1", "Categoria 2", "Categoria 3", "Categoria 4", "Categoria 5", "Otras Categorias"],
                key='competitive_experience'
            )
        preferred_nationality = st.multiselect("Nacionalidad Preferente (Opcional)", federaciones_fifa, key='preferred_nationality')

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
        immediate_needs = st.text_area("¿Existen posiciones que necesitan ser reforzadas de manera urgente? (Describa posición y motivo)", key='immediate_needs')

    # 5. Campo para seleccionar si el jugador es Agente Libre o no
    with st.expander("5. Contrato actual"):
        agente_libre = st.radio(
            "¿Quieren el jugador Agente Libre?", 
            ("Sí", "No"), 
            key='agente_libre'
        )

    # Si no es agente libre, mostrar campo para la fecha de finalización de contrato
    if agente_libre == "No":
        contract_end = st.text_input("Ingrese lo que puede llegar a pagar el club por el jugador/a", key='contract_end')
    else:
        contract_end = "Sin especificar"  # Si es agente libre, no se requiere fecha de finalización del contrato

    # Añadir nuevas métricas al formulario
    # 6. Historial de lesiones
    with st.expander("6. Historial de Lesiones"):
        lesion_historial = st.text_area("Describa el historial de lesiones del jugador (si aplica)", key='lesion_historial')

    # 7. Estadísticas de Rendimiento
    with st.expander("7. Estadísticas de Rendimiento"):
        periodo = st.selectbox("Periodo de Tiempo", ["Últimos 10 partidos", "Última temporada", "Total"])
        
        # Goles
        goles_totales = st.number_input("Total de goles", min_value=0, step=1, key='goles_totales')
        if goles_totales > 0:
            goles_por_partido = goles_totales / (10 if periodo == "Últimos 10 partidos" else 38)
            st.write(f"Goles por partido: {goles_por_partido:.2f}")
        else:
            goles_por_partido = 0  # Definir como 0 si no hay goles totales

        # Asistencias
        asistencias_totales = st.number_input("Total de asistencias", min_value=0, step=1, key='asistencias_totales')
        if asistencias_totales > 0:
            asistencias_por_partido = asistencias_totales / (10 if periodo == "Últimos 10 partidos" else 38)
            st.write(f"Asistencias por partido: {asistencias_por_partido:.2f}")
        else:
            asistencias_por_partido = 0  # Definir como 0 si no hay asistencias totales

        # Intercepciones
        intercepciones_totales = st.number_input("Total de intercepciones", min_value=0, step=1, key='intercepciones_totales')
        if intercepciones_totales > 0:
            intercepciones_por_partido = intercepciones_totales / (10 if periodo == "Últimos 10 partidos" else 38)
            st.write(f"Intercepciones por partido: {intercepciones_por_partido:.2f}")
        else:
            intercepciones_por_partido = 0  # Definir como 0 si no hay intercepciones totales

        # Porcentaje de paradas (si es portero)
        is_goalkeeper = st.radio("¿El jugador es portero?", ("Sí", "No"), key='is_goalkeeper')
        if is_goalkeeper == "Sí":
            paradas_totales = st.number_input("Total de paradas", min_value=0, step=1, key='paradas_totales')
            total_disparos = st.number_input("Total de disparos enfrentados", min_value=1, step=1, key='total_disparos')
            if paradas_totales > 0:
                porcentaje_paradas = (paradas_totales / total_disparos) * 100
                st.write(f"Porcentaje de paradas: {porcentaje_paradas:.2f}%")
            else:
                porcentaje_paradas = 0  # Definir como 0 si no hay paradas totales
        else:
            porcentaje_paradas = "N/A"  # Si no es portero, el porcentaje de paradas no aplica

    # 8. Adaptabilidad Internacional
    with st.expander("8. Adaptabilidad Internacional"):
        adaptabilidad_internacional = st.radio("¿Ha jugado en ligas internacionales?", ("Sí", "No"), key='adaptabilidad_internacional')

    # 9. Disponibilidad para Viajar/Mudarse
    with st.expander("9. Disponibilidad para Viajar/Mudarse"):
        disponibilidad_viajar = st.radio("¿Está disponible para viajar/mudarse?", ("Sí", "No"), key='disponibilidad_viajar')

    # 10. Nivel de Idiomas
    with st.expander("10. Idiomas que habla"):
        idiomas = st.text_area("Idiomas que el jugador habla", key='idiomas')

    # 11. Valor de Mercado Actual
    with st.expander("11. Valor de Mercado"):
        valor_mercado = st.text_input("Valor de mercado actual estimado (si aplica)", key='valor_mercado')

    # 12. Flexibilidad Posicional
    with st.expander("12. Flexibilidad Posicional"):
        flexibilidad_posicional = st.text_area("Posiciones adicionales en las que puede jugar", key='flexibilidad_posicional')

    # 13. Recomendación de Scouting
    with st.expander("13. Recomendación de Scouting"):
        scouting_recomendacion = st.text_area("Evaluación del scouting sobre el potencial del jugador", key='scouting_recomendacion')

    # 14. Presencia en Competiciones Internacionales
    with st.expander("14. Participación en Competiciones Internacionales"):
        competiciones_internacionales = st.text_area("Competiciones internacionales en las que ha participado", key='competiciones_internacionales')

    # 15. Actitud y Carácter
    with st.expander("15. Actitud y Carácter"):
        actitud_caracter = st.text_area("Evaluación de actitud y carácter", key='actitud_caracter')

    # 16. Seguimiento Mediático o en Redes Sociales
    with st.expander("16. Seguimiento en Medios o Redes Sociales"):
        seguimiento_medios = st.text_area("¿Tiene el jugador una presencia relevante en redes sociales o medios?", key='seguimiento_medios')

    # Botón de Enviar
    if st.button("Descargar Informe"):
        datos = {
            "Nombre del Club": nombre_club,
            "Ventana a Reforzar": ventana_mercado,
            "Posiciones": position,
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
            "Estadísticas de Rendimiento - Goles por Partido": goles_por_partido,
            "Estadísticas de Rendimiento - Asistencias": asistencias_totales,
            "Estadísticas de Rendimiento - Asistencias por Partido": asistencias_por_partido,
            "Estadísticas de Rendimiento - Intercepciones": intercepciones_totales,
            "Estadísticas de Rendimiento - Intercepciones por Partido": intercepciones_por_partido,
            "Estadísticas de Rendimiento - Porcentaje de Paradas": porcentaje_paradas,
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
        # Guardar los datos en el archivo CSV
        guardar_datos(datos)

        # Generar PDF con los datos nuevos
        pdf_data = generar_pdf(datos)

        # Botón para descargar el PDF
        st.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name="report.pdf",
            mime="application/pdf"
        )
