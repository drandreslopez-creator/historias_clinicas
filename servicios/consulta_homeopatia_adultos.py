import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from core.calculos import calcular_edad
from servicios.consulta_externa_base import render_consulta_externa
from servicios.pediatria_urgencias import (
    construir_nombre_base_docx,
    eliminar_historia_guardada,
    generar_docx_informe,
    guardar_docx_exportado,
    render_informe_html,
    subir_docx_a_google_drive,
)


BASE_DIR = Path(__file__).resolve().parent.parent
BOGOTA_TZ = ZoneInfo("America/Bogota")
HISTORY_FILENAME = "historias_homeopatia_adultos.jsonl"

ANTECEDENTES_HOMEO_ADULTOS_DEFAULT = """PATOLÓGICOS: SEGÚN REFIERE.
HOSPITALARIOS: SEGÚN REFIERE.
FARMACOLÓGICOS: SEGÚN REFIERE.
ALÉRGICOS: SEGÚN REFIERE.
QUIRÚRGICOS: SEGÚN REFIERE.
GINECO-OBSTÉTRICOS: SEGÚN CORRESPONDA.
FAMILIARES: SEGÚN REFIERE."""

REVISION_HOMEO_DEFAULT = "NEGADOS."

BIOPATOGRAFIA_DEFAULT = """DINÁMICA FAMILIAR DE ORIGEN, VÍNCULOS AFECTIVOS, EVENTOS IMPORTANTES DE VIDA, DUELOS, CAMBIOS RELEVANTES Y RASGOS CONSTITUCIONALES SEGÚN REFIERA."""

SINTOMAS_GENERALES_DEFAULT = """SUEÑO, APETITO, SED, TERMIA, SUDORACIÓN, ANTOJOS/AVERSIONES, AGRAVANTES, MEJORÍAS, LATERALIDAD Y MODALIDADES SEGÚN REFIERA."""

SINTOMAS_MENTALES_DEFAULT = """ESTADO DE ÁNIMO, TEMORES, IRRITABILIDAD, RELACIONES INTERPERSONALES, RASGOS AFECTIVOS, RESPUESTA AL ESTRÉS Y OTROS DATOS MENTALES RELEVANTES SEGÚN REFIERA."""

EXAMEN_HOMEO_ADULTOS_DEFAULT = """PACIENTE EN BUEN ESTADO GENERAL, ALERTA, ORIENTADO, BUEN ESTADO DE HIDRATACIÓN.

CABEZA Y CUELLO: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
CARDIOPULMONAR: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
ABDOMEN: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
EXTREMIDADES: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
NEUROLÓGICO: SIN FOCALIZACIONES CLÍNICAS."""

PARACLINICOS_DEFAULT = "NO SE SOLICITAN."

ANALISIS_HOMEOPATICO_DEFAULT = """REALIZAR ANÁLISIS INTEGRATIVO DEL CASO DESDE EL ENFOQUE CLÍNICO Y HOMEOPÁTICO, CORRELACIONANDO TERRENO CONSTITUCIONAL, SÍNTOMAS GENERALES, SÍNTOMAS MENTALES Y RUBROS RELEVANTES."""

RUBROS_DEFAULT = """MENTE

GENERALES

PARTICULARES"""

TRATAMIENTO_DEFAULT = """HOMEOPATÍA:

ORTOMOLECULAR:

SUEROTERAPIA:

RECOMENDACIONES:

SEGUIMIENTO:"""


def _historia_path(nombre_archivo):
    return BASE_DIR / "data" / nombre_archivo


def _init_state(defaults):
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _clear_state(prefix, defaults):
    keys_to_clear = [key for key in st.session_state.keys() if key.startswith(prefix)]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
    for key, value in defaults.items():
        st.session_state[key] = value


def _load_histories(path):
    if not path.exists():
        return []
    historias = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                historias.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return list(reversed(historias))


def _save_history(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def render():
    prefix = "homeo_adult"
    titulo = "CONSULTA EXTERNA - MEDICINA ALTERNATIVA - HOMEOPATÍA ADULTOS"
    history_path = _historia_path(HISTORY_FILENAME)

    modalidad = st.selectbox(
        "Modalidad de la consulta",
        ["PRIMERA VEZ", "CITA DE CONTROL"],
        key=f"{prefix}_modalidad_consulta_selector",
    )

    if modalidad == "CITA DE CONTROL":
        render_consulta_externa(
            prefix=prefix,
            titulo=titulo,
            history_filename=HISTORY_FILENAME,
            es_pediatrica=False,
            mostrar_neurodesarrollo=False,
            mostrar_modalidad_consulta=False,
            mostrar_pb=False,
            modalidad_consulta_forzada="CITA DE CONTROL",
        )
        return

    defaults = {
        f"{prefix}_nombre": "",
        f"{prefix}_tipo_documento": None,
        f"{prefix}_documento": "",
        f"{prefix}_fecha_nacimiento": None,
        f"{prefix}_sexo": None,
        f"{prefix}_eps": "",
        f"{prefix}_informante": "",
        f"{prefix}_motivo": "",
        f"{prefix}_enfermedad_actual": "",
        f"{prefix}_antecedentes": ANTECEDENTES_HOMEO_ADULTOS_DEFAULT,
        f"{prefix}_revision": REVISION_HOMEO_DEFAULT,
        f"{prefix}_biopatografia": BIOPATOGRAFIA_DEFAULT,
        f"{prefix}_sintomas_generales": SINTOMAS_GENERALES_DEFAULT,
        f"{prefix}_sintomas_mentales": SINTOMAS_MENTALES_DEFAULT,
        f"{prefix}_ta": "",
        f"{prefix}_fc": 0.0,
        f"{prefix}_fr": 0.0,
        f"{prefix}_sat": 0.0,
        f"{prefix}_temp": 0.0,
        f"{prefix}_peso": 0.0,
        f"{prefix}_talla": 0.0,
        f"{prefix}_imc_manual": "",
        f"{prefix}_examen": EXAMEN_HOMEO_ADULTOS_DEFAULT,
        f"{prefix}_signos_positivos": "",
        f"{prefix}_diagnosticos": "",
        f"{prefix}_paraclinicos": PARACLINICOS_DEFAULT,
        f"{prefix}_analisis_homeopatico": ANALISIS_HOMEOPATICO_DEFAULT,
        f"{prefix}_rubros": RUBROS_DEFAULT,
        f"{prefix}_tratamiento": TRATAMIENTO_DEFAULT,
        f"{prefix}_historia_consulta_id": None,
    }

    if st.session_state.pop(f"{prefix}_clear_requested", False):
        _clear_state(prefix, defaults)
        st.rerun()

    _init_state(defaults)

    st.header(f"📌 {titulo}")
    st.info("Modalidad de la consulta: PRIMERA VEZ")

    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombres y apellidos", key=f"{prefix}_nombre")
        tipo_documento = st.selectbox(
            "Tipo de documento",
            ["CC", "CE", "PEP", "PS", "OTRO"],
            index=None,
            placeholder="Seleccione tipo de documento",
            key=f"{prefix}_tipo_documento",
        )
        fecha_nacimiento = st.date_input(
            "Fecha de nacimiento",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key=f"{prefix}_fecha_nacimiento",
        )
        eps = st.text_input("EPS", key=f"{prefix}_eps")

    with col2:
        sexo = st.selectbox(
            "Sexo",
            ["Masculino", "Femenino"],
            index=None,
            placeholder="Seleccione sexo",
            key=f"{prefix}_sexo",
        )
        documento = st.text_input("Documento", key=f"{prefix}_documento")
        informante = st.text_input("Informante / acompañante", key=f"{prefix}_informante")

    if fecha_nacimiento:
        años, meses, dias = calcular_edad(fecha_nacimiento)
        st.info(f"Edad: {años} años, {meses} meses, {dias} días")

    st.subheader("Motivo de consulta")
    motivo = st.text_area("Motivo de consulta", key=f"{prefix}_motivo", height=90)

    st.subheader("Enfermedad actual")
    enfermedad_actual = st.text_area(
        "Enfermedad actual (evolución y modalidades)",
        key=f"{prefix}_enfermedad_actual",
        height=220,
    )

    st.subheader("Antecedentes relevantes")
    antecedentes = st.text_area("Antecedentes relevantes", key=f"{prefix}_antecedentes", height=220)

    st.subheader("Revisión por sistemas")
    revision = st.text_area("Revisión por sistemas", key=f"{prefix}_revision", height=90)

    st.subheader("Resumen de biopatografía")
    biopatografia = st.text_area("Resumen de biopatografía", key=f"{prefix}_biopatografia", height=180)

    st.subheader("Síntomas generales")
    sintomas_generales = st.text_area("Síntomas generales", key=f"{prefix}_sintomas_generales", height=180)

    st.subheader("Síntomas mentales")
    sintomas_mentales = st.text_area("Síntomas mentales", key=f"{prefix}_sintomas_mentales", height=220)

    st.subheader("Examen físico")
    col_sv1, col_sv2 = st.columns(2)
    with col_sv1:
        ta = st.text_input("TA (mmHg)", key=f"{prefix}_ta")
        fc = st.number_input("FC (lpm)", min_value=0.0, key=f"{prefix}_fc")
        fr = st.number_input("FR (rpm)", min_value=0.0, key=f"{prefix}_fr")
    with col_sv2:
        sat = st.number_input("SpO2 (%)", min_value=0.0, key=f"{prefix}_sat")
        temp = st.number_input("Temperatura (°C)", min_value=0.0, key=f"{prefix}_temp")

    col_ant1, col_ant2, col_ant3 = st.columns(3)
    with col_ant1:
        peso = st.number_input("Peso (kg)", min_value=0.0, key=f"{prefix}_peso")
    with col_ant2:
        talla = st.number_input("Talla (cm)", min_value=0.0, key=f"{prefix}_talla")
    with col_ant3:
        imc_manual = st.text_input("IMC", key=f"{prefix}_imc_manual")

    examen = st.text_area("Examen físico", key=f"{prefix}_examen", height=220)
    signos_positivos = st.text_area("Signos positivos", key=f"{prefix}_signos_positivos", height=120)

    st.subheader("Diagnósticos médicos")
    diagnosticos = st.text_area("Diagnósticos médicos", key=f"{prefix}_diagnosticos", height=120)

    st.subheader("Exámenes paraclínicos")
    paraclinicos = st.text_area("Exámenes paraclínicos", key=f"{prefix}_paraclinicos", height=110)

    st.subheader("Análisis homeopático")
    analisis_homeopatico = st.text_area(
        "Análisis homeopático",
        key=f"{prefix}_analisis_homeopatico",
        height=280,
    )

    st.subheader("Rubros importantes")
    rubros = st.text_area("Rubros importantes", key=f"{prefix}_rubros", height=220)

    st.subheader("Análisis y tratamiento")
    tratamiento = st.text_area("Análisis y tratamiento", key=f"{prefix}_tratamiento", height=320)

    col_btn_1, col_btn_2 = st.columns(2)
    generar = col_btn_1.button("Generar Historia Clínica", key=f"{prefix}_generar", use_container_width=True)
    if col_btn_2.button("Limpiar y empezar otra historia", key=f"{prefix}_limpiar", use_container_width=True):
        st.session_state[f"{prefix}_clear_requested"] = True
        st.rerun()

    if generar:
        fecha_str = fecha_nacimiento.strftime("%d/%m/%Y") if fecha_nacimiento else ""
        antropometria = f"PESO {peso} KG TALLA {talla} CM"
        if imc_manual:
            antropometria += f" IMC {imc_manual}"

        historia = f"""
{titulo.upper()}

MODALIDAD DE LA CONSULTA:
PRIMERA VEZ

DATOS DE IDENTIFICACIÓN:
NOMBRES Y APELLIDOS: {nombre}
TIPO DE DOCUMENTO: {tipo_documento}
DOCUMENTO: {documento}
FECHA DE NACIMIENTO: {fecha_str}
EPS: {eps}
INFORMANTE / ACOMPAÑANTE: {informante}

MOTIVO DE CONSULTA:
{motivo}

ENFERMEDAD ACTUAL (EVOLUCIÓN Y MODALIDADES):
{enfermedad_actual}

ANTECEDENTES RELEVANTES:
{antecedentes}

REVISIÓN POR SISTEMAS:
{revision}

RESUMEN DE BIOPATOGRAFÍA:
{biopatografia}

SÍNTOMAS GENERALES:
{sintomas_generales}

SÍNTOMAS MENTALES:
{sintomas_mentales}

EXAMEN FÍSICO:
TA {ta} mmHg FC {fc} lpm SpO2 {sat}% FR {fr} rpm T {temp} °C
{antropometria}
{examen}

SIGNOS POSITIVOS:
{signos_positivos}

DIAGNÓSTICOS MÉDICOS:
{diagnosticos}

EXÁMENES PARACLÍNICOS:
{paraclinicos}

ANÁLISIS HOMEOPÁTICO:
{analisis_homeopatico}

RUBROS IMPORTANTES:
{rubros}

ANÁLISIS Y TRATAMIENTO:
{tratamiento}
""".strip()

        secciones = [
            ("MODALIDAD DE LA CONSULTA", "PRIMERA VEZ"),
            (
                "DATOS DE IDENTIFICACIÓN",
                f"NOMBRES Y APELLIDOS: {nombre}\nTIPO DE DOCUMENTO: {tipo_documento}\nDOCUMENTO: {documento}\nFECHA DE NACIMIENTO: {fecha_str}\nEPS: {eps}\nINFORMANTE / ACOMPAÑANTE: {informante}",
            ),
            ("MOTIVO DE CONSULTA", motivo),
            ("ENFERMEDAD ACTUAL (EVOLUCIÓN Y MODALIDADES)", enfermedad_actual),
            ("ANTECEDENTES RELEVANTES", antecedentes),
            ("REVISIÓN POR SISTEMAS", revision),
            ("RESUMEN DE BIOPATOGRAFÍA", biopatografia),
            ("SÍNTOMAS GENERALES", sintomas_generales),
            ("SÍNTOMAS MENTALES", sintomas_mentales),
            (
                "EXAMEN FÍSICO",
                f"TA {ta} mmHg FC {fc} lpm SpO2 {sat}% FR {fr} rpm T {temp} °C\n{antropometria}\n{examen}",
            ),
            ("SIGNOS POSITIVOS", signos_positivos),
            ("DIAGNÓSTICOS MÉDICOS", diagnosticos),
            ("EXÁMENES PARACLÍNICOS", paraclinicos),
            ("ANÁLISIS HOMEOPÁTICO", analisis_homeopatico),
            ("RUBROS IMPORTANTES", rubros),
            ("ANÁLISIS Y TRATAMIENTO", tratamiento),
        ]

        st.success("Historia clínica generada")
        fecha_guardado = datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        docx_bytes = generar_docx_informe(titulo.upper(), secciones)
        nombre_base_docx = construir_nombre_base_docx(
            "CE",
            nombre=nombre,
            documento=documento,
            fecha_guardado=fecha_guardado,
        )
        ruta_docx_guardado = guardar_docx_exportado(
            docx_bytes,
            nombre_base_docx,
            subcarpeta=prefix,
        )
        nombre_docx = f"{nombre_base_docx}.docx"
        st.download_button(
            "Descargar informe en Word",
            data=docx_bytes,
            file_name=nombre_docx,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"{prefix}_download_docx",
        )
        resultado_drive = subir_docx_a_google_drive(docx_bytes, nombre_docx)
        if resultado_drive.get("ok"):
            enlace_drive = resultado_drive.get("webViewLink")
            if enlace_drive:
                st.success(f"HC guardada en Drive. [VER]({enlace_drive})")
            else:
                st.success("HC guardada en Drive.")
        elif resultado_drive.get("configured"):
            st.warning(resultado_drive.get("message", "No se pudo guardar en Google Drive."))
        else:
            st.info("Google Drive no está configurado aún. El Word sí quedó disponible para descarga.")

        identificador = f"{fecha_guardado} | {nombre or 'SIN NOMBRE'} | {documento or 'SIN DOCUMENTO'}"
        _save_history(
            history_path,
            {
                "id": identificador,
                "fecha_guardado": fecha_guardado,
                "nombre": nombre,
                "documento": documento,
                "historia": historia.upper(),
                "docx_local_path": str(ruta_docx_guardado),
                "drive_file_id": resultado_drive.get("file_id"),
                "drive_webview_link": resultado_drive.get("webViewLink"),
            },
        )
        render_informe_html(titulo.upper(), secciones, historia.upper())

    st.divider()
    with st.expander("Historias guardadas", expanded=False):
        historias_guardadas = _load_histories(history_path)
        if historias_guardadas:
            opciones = [h["id"] for h in historias_guardadas]
            historia_consulta_id = st.selectbox(
                "Consultar historia previa",
                opciones,
                key=f"{prefix}_historia_consulta_id",
            )
            historia_sel = next((h for h in historias_guardadas if h["id"] == historia_consulta_id), None)
            if historia_sel:
                st.text_area(
                    "Informe guardado",
                    historia_sel["historia"],
                    height=500,
                    key=f"{prefix}_historia_guardada_texto",
                )
                if st.button("Eliminar esta historia", key=f"{prefix}_eliminar_historia", use_container_width=True):
                    resultado_eliminacion = eliminar_historia_guardada(history_path, historia_consulta_id)
                    if resultado_eliminacion.get("ok"):
                        st.success("Historia eliminada correctamente.")
                        st.rerun()
                    else:
                        st.warning(resultado_eliminacion.get("message", "No se pudo eliminar la historia."))
        else:
            st.info("Aún no hay historias guardadas.")
