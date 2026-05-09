import streamlit as st
from datetime import date

def render():

    st.header("👶 HISTORIA CLÍNICA - ADAPTACIÓN NEONATAL")

    # =========================
    # DATOS DEL RECIÉN NACIDO
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre RN")
        fecha_nacimiento = st.date_input("Fecha nacimiento")
        sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])

    with col2:
        peso = st.number_input("Peso (g)")
        talla = st.number_input("Talla (cm)")
        edad_gestacional = st.number_input("Edad gestacional (semanas)")

    # =========================
    # APGAR
    # =========================
    st.subheader("APGAR")

    col1, col2 = st.columns(2)

    with col1:
        apgar1 = st.number_input("APGAR 1 min", min_value=0, max_value=10)

    with col2:
        apgar5 = st.number_input("APGAR 5 min", min_value=0, max_value=10)

    # =========================
    # NACIMIENTO (PLANTILLA FIJA 🔥)
    # =========================
    nacimiento = """ADAPTACIÓN NEONATAL

Se recibe recién nacido con adecuado esfuerzo respiratorio y tono, se coloca bajo calor radiante, se realiza secado cefalocaudal, aspiración suave de secreciones, permeabilidad de coanas y esófago adecuada, ano permeable. Se aplican medidas de profilaxis: vitamina K intramuscular, profilaxis ocular con yodopovidona, profilaxis umbilical con clorhexidina. Vacunas BCG y hepatitis B pendientes de aplicar. Informe brindado a la madre.
"""

    st.subheader("Adaptación neonatal")
    nacimiento_editable = st.text_area("Texto adaptación", value=nacimiento, height=200)

    # =========================
    # EXAMEN FÍSICO
    # =========================
    st.subheader("Examen físico")

    examen = st.text_area(
        "Examen físico",
        value="RECIÉN NACIDO EN BUEN ESTADO GENERAL, ACTIVO, REACTIVO, NORMOCÉFALO, SIN DIFICULTAD RESPIRATORIA...",
        height=200
    )

    # =========================
    # SIGNOS VITALES
    # =========================
    st.subheader("Signos vitales")

    col_sv1, col_sv2, col_sv3 = st.columns(3)
    with col_sv1:
        ta = st.text_input("TA (mmHg)")
    with col_sv2:
        fc = st.text_input("FC (lpm)")
    with col_sv3:
        sat = st.text_input("SpO2 (%)")

    col_sv4, col_sv5, col_sv6 = st.columns(3)
    with col_sv4:
        fr = st.text_input("FR (rpm)")
    with col_sv5:
        glucometria = st.text_input("Glucometría (mg/dl)")
    with col_sv6:
        temp = st.text_input("Temperatura (°C)")

    # =========================
    # GENERAR HISTORIA 🔥
    # =========================
    if st.button("🧾 Generar Historia Neonatal"):

        historia = f"""
HISTORIA CLÍNICA DE ADAPTACIÓN NEONATAL

NOMBRE: {nombre}
FECHA NACIMIENTO: {fecha_nacimiento}
SEXO: {sexo}

EDAD GESTACIONAL: {edad_gestacional} SEMANAS
PESO: {peso} g
TALLA: {talla} cm

APGAR: {apgar1}/{apgar5}

NACIMIENTO:
{nacimiento_editable}

EXAMEN FÍSICO:
{examen}

SIGNOS VITALES:
TA: {ta} mmHg
FC: {fc} lpm
FR: {fr} rpm
GLUCOMETRÍA: {glucometria} mg/dl
TEMP: {temp} °C
SAT O2: {sat}%
"""

        st.success("Historia generada")
        st.text_area("Resultado", historia, height=400)
