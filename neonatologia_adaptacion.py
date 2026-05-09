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

    fc = st.number_input("FC")
    fr = st.number_input("FR")
    temp = st.number_input("Temperatura")
    sat = st.number_input("Sat O2")

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
FC: {fc} lpm
FR: {fr} rpm
TEMP: {temp} °C
SAT O2: {sat}%
"""

        st.success("Historia generada")
        st.text_area("Resultado", historia, height=400)
