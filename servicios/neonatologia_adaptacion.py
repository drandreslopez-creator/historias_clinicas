import hashlib
import json
from datetime import date

import streamlit as st

from servicios.pediatria_urgencias import (
    actualizar_texto_extraido,
    complementar_analisis_con_ia,
    construir_resumen_paraclinicos_para_analisis,
    construir_resumen_signos_para_analisis,
    extraer_resumen_examen_para_analisis,
    generar_analisis_asistido_urgencias,
)


PREFIX = "neo_adaptacion"


def _float_or_none(valor):
    texto = str(valor or "").strip().replace(",", ".")
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def _init_defaults():
    defaults = {
        f"{PREFIX}_nombre": "",
        f"{PREFIX}_fecha_nacimiento": None,
        f"{PREFIX}_sexo": None,
        f"{PREFIX}_peso": "",
        f"{PREFIX}_talla": "",
        f"{PREFIX}_edad_gestacional": "",
        f"{PREFIX}_apgar1": "",
        f"{PREFIX}_apgar5": "",
        f"{PREFIX}_nacimiento": """ADAPTACIÓN NEONATAL

SE RECIBE RECIÉN NACIDO CON ADECUADO ESFUERZO RESPIRATORIO Y TONO, SE COLOCA BAJO CALOR RADIANTE, SE REALIZA SECADO CEFALOCAUDAL, ASPIRACIÓN SUAVE DE SECRECIONES, PERMEABILIDAD DE COANAS Y ESÓFAGO ADECUADA, ANO PERMEABLE. SE APLICAN MEDIDAS DE PROFILAXIS: VITAMINA K INTRAMUSCULAR, PROFILAXIS OCULAR Y PROFILAXIS UMBILICAL. INFORME BRINDADO A LA MADRE.""",
        f"{PREFIX}_examen": "RECIÉN NACIDO EN BUEN ESTADO GENERAL, ACTIVO, REACTIVO, SIN DIFICULTAD RESPIRATORIA.",
        f"{PREFIX}_ta": "",
        f"{PREFIX}_fc": "",
        f"{PREFIX}_sat": "",
        f"{PREFIX}_fr": "",
        f"{PREFIX}_glucometria": "",
        f"{PREFIX}_temp": "",
        f"{PREFIX}_paraclinicos_texto": "",
        f"{PREFIX}_paraclinicos_auto": "",
        f"{PREFIX}_paraclinicos_pdf_sig": "",
        f"{PREFIX}_imagenes_texto": "",
        f"{PREFIX}_imagenes_auto": "",
        f"{PREFIX}_imagenes_pdf_sig": "",
        f"{PREFIX}_analisis": "",
        f"{PREFIX}_analisis_base": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render():
    _init_defaults()

    st.header("HISTORIA CLÍNICA - ADAPTACIÓN NEONATAL")

    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre RN", key=f"{PREFIX}_nombre")
        fecha_nacimiento = st.date_input(
            "Fecha nacimiento",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key=f"{PREFIX}_fecha_nacimiento",
        )
        sexo = st.selectbox(
            "Sexo",
            ["Masculino", "Femenino"],
            index=None,
            placeholder="Seleccione sexo",
            key=f"{PREFIX}_sexo",
        )
    with col2:
        peso = st.text_input("Peso (g)", key=f"{PREFIX}_peso")
        talla = st.text_input("Talla (cm)", key=f"{PREFIX}_talla")
        edad_gestacional = st.text_input("Edad gestacional (semanas)", key=f"{PREFIX}_edad_gestacional")

    st.subheader("APGAR")
    col_apgar1, col_apgar2 = st.columns(2)
    with col_apgar1:
        apgar1 = st.text_input("APGAR 1 min", key=f"{PREFIX}_apgar1")
    with col_apgar2:
        apgar5 = st.text_input("APGAR 5 min", key=f"{PREFIX}_apgar5")

    st.subheader("Adaptación neonatal")
    nacimiento_editable = st.text_area("", key=f"{PREFIX}_nacimiento", height=200, label_visibility="collapsed")

    st.subheader("Examen físico")
    examen = st.text_area("", key=f"{PREFIX}_examen", height=220, label_visibility="collapsed")

    st.subheader("Signos vitales")
    col_sv1, col_sv2, col_sv3 = st.columns(3)
    with col_sv1:
        ta = st.text_input("TA (mmHg)", key=f"{PREFIX}_ta")
    with col_sv2:
        fc = st.text_input("FC (lpm)", key=f"{PREFIX}_fc")
    with col_sv3:
        sat = st.text_input("SpO2 (%)", key=f"{PREFIX}_sat")

    col_sv4, col_sv5, col_sv6 = st.columns(3)
    with col_sv4:
        fr = st.text_input("FR (rpm)", key=f"{PREFIX}_fr")
    with col_sv5:
        glucometria = st.text_input("Glucometría (mg/dl)", key=f"{PREFIX}_glucometria")
    with col_sv6:
        temp = st.text_input("Temperatura (°C)", key=f"{PREFIX}_temp")

    st.subheader("Paraclínicos")
    col_pdf_1, col_pdf_2 = st.columns(2)
    with col_pdf_1:
        pdf_labs = st.file_uploader(
            "Subir PDF de laboratorios",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"{PREFIX}_paraclinicos_pdf_v1",
        )
    with col_pdf_2:
        pdf_imgs = st.file_uploader(
            "Subir PDF de imágenes",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"{PREFIX}_imagenes_pdf_v1",
        )

    if pdf_labs:
        actualizar_texto_extraido(
            f"{PREFIX}_paraclinicos_texto",
            f"{PREFIX}_paraclinicos_auto",
            f"{PREFIX}_paraclinicos_pdf_sig",
            pdf_labs,
            "laboratorios",
        )
    if pdf_imgs:
        actualizar_texto_extraido(
            f"{PREFIX}_imagenes_texto",
            f"{PREFIX}_imagenes_auto",
            f"{PREFIX}_imagenes_pdf_sig",
            pdf_imgs,
            "imagenes",
        )

    paraclinicos_texto = st.text_area("Laboratorios", key=f"{PREFIX}_paraclinicos_texto", height=150)
    imagenes_texto = st.text_area("Imágenes", key=f"{PREFIX}_imagenes_texto", height=120)

    resumen_examen_analisis = extraer_resumen_examen_para_analisis(examen)
    resumen_signos_analisis = construir_resumen_signos_para_analisis(
        _float_or_none(fc),
        _float_or_none(fr),
        _float_or_none(sat),
        _float_or_none(temp),
        _float_or_none(glucometria),
        None,
        "RECIÉN NACIDO",
    )
    resumen_paraclinicos_analisis = construir_resumen_paraclinicos_para_analisis(paraclinicos_texto)
    enfermedad_auto = (
        f"RECIÉN NACIDO DE {edad_gestacional} SEMANAS, QUIEN SE ENCUENTRA EN PROCESO DE ADAPTACIÓN NEONATAL"
    ).strip()
    analisis_default = generar_analisis_asistido_urgencias(
        enfermedad_auto,
        resumen_examen_analisis,
        resumen_signos_analisis,
        resumen_paraclinicos_analisis,
    )
    contexto_analisis_ia = {
        "titulo": "HISTORIA CLÍNICA - ADAPTACIÓN NEONATAL",
        "nacimiento": nacimiento_editable,
        "edad_gestacional": edad_gestacional,
        "apgar_1": apgar1,
        "apgar_5": apgar5,
        "examen_fisico": examen,
        "signos_vitales": {
            "ta": ta,
            "fc": fc,
            "fr": fr,
            "spo2": sat,
            "glucometria": glucometria,
            "temperatura": temp,
        },
        "paraclinicos": paraclinicos_texto,
        "imagenes": imagenes_texto,
    }
    fingerprint_analisis_ia = hashlib.md5(
        json.dumps(contexto_analisis_ia, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    analisis_default = complementar_analisis_con_ia(
        analisis_default,
        contexto_analisis_ia,
        fingerprint_analisis_ia,
        instrucciones=(
            "Eres un asistente clínico que redacta análisis neonatales en español. "
            "Usa únicamente la información entregada. No inventes diagnósticos ni conductas. "
            "Redacta un solo párrafo en MAYÚSCULAS, coherente y profesional, integrando datos perinatales, adaptación, "
            "examen físico, signos vitales y paraclínicos cuando existan."
        ),
    )

    st.subheader("Análisis")
    if st.session_state.get(f"{PREFIX}_analisis_base") != analisis_default:
        if st.session_state.get(f"{PREFIX}_analisis") == st.session_state.get(f"{PREFIX}_analisis_base", ""):
            st.session_state[f"{PREFIX}_analisis"] = analisis_default
        st.session_state[f"{PREFIX}_analisis_base"] = analisis_default
    analisis = st.text_area("", key=f"{PREFIX}_analisis", height=180, label_visibility="collapsed")

    if st.button("Generar Historia Neonatal"):
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

PARACLÍNICOS:
{paraclinicos_texto}

IMÁGENES:
{imagenes_texto}

ANÁLISIS:
{analisis}
""".strip()

        st.success("Historia generada")
        st.text_area("Resultado", historia, height=500)
