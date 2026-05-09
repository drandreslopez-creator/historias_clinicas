import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from core.calculos import calcular_edad
from core.clasificacion import grupo_etario
from herramientas.neurodesarrollo import obtener_neurodesarrollo
from servicios.pediatria_urgencias import (
    generar_docx_informe,
    guardar_docx_exportado,
    subir_docx_a_google_drive,
    render_informe_html,
)


BASE_DIR = Path(__file__).resolve().parent.parent
BOGOTA_TZ = ZoneInfo("America/Bogota")

ANTECEDENTES_DEFAULT = """PERINATALES/NEONATALES: SEGUN REFIERE.
PATOLÓGICOS: NIEGA.
HOSPITALARIOS: NIEGA.
FARMACOLÓGICOS: NIEGA.
ALÉRGICOS: NIEGA.
QUIRÚRGICOS: NIEGA.
FAMILIARES: SIN DATOS PATOLÓGICOS RELEVANTES."""

ANTECEDENTES_ADULTO_DEFAULT = """PATOLÓGICOS: NIEGA.
HOSPITALARIOS: NIEGA.
FARMACOLÓGICOS: NIEGA.
ALÉRGICOS: NIEGA.
QUIRÚRGICOS: NIEGA.
GINECO-OBSTÉTRICOS: SEGUN CORRESPONDA.
FAMILIARES: SIN DATOS PATOLÓGICOS RELEVANTES."""

EXAMEN_DEFAULT = """PACIENTE EN BUEN ESTADO GENERAL, ALERTA, BUEN ESTADO DE HIDRATACIÓN.

CABEZA Y CUELLO: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
CARDIOPULMONAR: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
ABDOMEN: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
EXTREMIDADES: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
NEUROLÓGICO: SIN FOCALIZACIONES CLÍNICAS."""

PLAN_DEFAULT = """- MANEJO SEGUN HALLAZGOS CLÍNICOS
- EDUCACIÓN A PACIENTE Y/O CUIDADOR
- SIGNOS DE ALARMA
- CONTROL SEGUN EVOLUCIÓN"""


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


def render_consulta_externa(
    *,
    prefix,
    titulo,
    history_filename,
    es_pediatrica=False,
    mostrar_neurodesarrollo=False,
    antecedentes_default=None,
    plan_default=None,
):
    antecedentes_default = antecedentes_default or (ANTECEDENTES_DEFAULT if es_pediatrica else ANTECEDENTES_ADULTO_DEFAULT)
    plan_default = plan_default or PLAN_DEFAULT
    history_path = _historia_path(history_filename)

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
        f"{prefix}_antecedentes": antecedentes_default,
        f"{prefix}_revision": "NIEGA OTROS SINTOMAS/SIGNOS A LOS YA MENCIONADOS.",
        f"{prefix}_fc": 0.0,
        f"{prefix}_fr": 0.0,
        f"{prefix}_ta": "",
        f"{prefix}_sat": 0.0,
        f"{prefix}_temp": 0.0,
        f"{prefix}_peso": 0.0,
        f"{prefix}_talla": 0.0,
        f"{prefix}_pc": 0.0,
        f"{prefix}_neuro": "",
        f"{prefix}_examen": EXAMEN_DEFAULT,
        f"{prefix}_analisis": "",
        f"{prefix}_analisis_base": "",
        f"{prefix}_diagnosticos": "",
        f"{prefix}_obs_dx": "",
        f"{prefix}_plan": plan_default,
        f"{prefix}_plan_base": plan_default,
        f"{prefix}_historia_consulta_id": None,
    }

    if st.session_state.pop(f"{prefix}_clear_requested", False):
        _clear_state(prefix, defaults)
        st.rerun()

    _init_state(defaults)

    st.header(f"📌 {titulo}")

    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombres y apellidos", key=f"{prefix}_nombre")
        tipo_documento = st.selectbox(
            "Tipo de documento",
            ["NV", "RC", "TI", "CC", "CE", "PEP", "PS", "OTRO"],
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
        informante = st.text_input(
            "Informante / acompañante",
            key=f"{prefix}_informante",
        )

    edad_texto = ""
    años = meses = dias = 0
    grupo = ""
    if fecha_nacimiento:
        años, meses, dias = calcular_edad(fecha_nacimiento)
        edad_texto = f"{años} años, {meses} meses, {dias} días"
        if es_pediatrica:
            grupo = grupo_etario(años)
        st.info(f"Edad: {edad_texto}")

    motivo = st.text_area("Motivo de consulta", key=f"{prefix}_motivo")
    enfermedad_actual = st.text_area("Enfermedad actual", key=f"{prefix}_enfermedad_actual")

    st.subheader("Antecedentes")
    antecedentes = st.text_area("Antecedentes", key=f"{prefix}_antecedentes", height=220)

    neuro = ""
    if mostrar_neurodesarrollo and fecha_nacimiento:
        neuro_default = obtener_neurodesarrollo(años, meses)
        if not st.session_state.get(f"{prefix}_neuro"):
            st.session_state[f"{prefix}_neuro"] = neuro_default
        st.subheader("Neurodesarrollo")
        neuro = st.text_area("Neurodesarrollo", key=f"{prefix}_neuro", height=160)

    st.subheader("Revisión por sistemas")
    revision = st.text_area("Revisión", key=f"{prefix}_revision")

    st.subheader("Signos vitales")
    col_sv_1, col_sv_2 = st.columns(2)
    with col_sv_1:
        ta = st.text_input("TA (mmHg)", key=f"{prefix}_ta")
        fc = st.number_input("FC (lpm)", min_value=0.0, key=f"{prefix}_fc")
        fr = st.number_input("FR (rpm)", min_value=0.0, key=f"{prefix}_fr")
    with col_sv_2:
        sat = st.number_input("SpO2 (%)", min_value=0.0, key=f"{prefix}_sat")
        temp = st.number_input("Temperatura (°C)", min_value=0.0, key=f"{prefix}_temp")

    peso = st.number_input("Peso (kg)", min_value=0.0, key=f"{prefix}_peso")
    talla = st.number_input("Talla (cm)", min_value=0.0, key=f"{prefix}_talla")
    if es_pediatrica:
        pc = st.number_input("Perímetro cefálico (cm)", min_value=0.0, key=f"{prefix}_pc")
    else:
        pc = 0.0

    st.subheader("Examen físico")
    examen = st.text_area("Examen físico", key=f"{prefix}_examen", height=260)

    sexo_txt = (sexo or "").upper()
    grupo_txt = f" {grupo.upper()}" if grupo else ""
    edad_resumen = f"{años} AÑOS" if años > 0 else (f"{meses} MESES" if fecha_nacimiento else "")
    analisis_default = (
        f"PACIENTE {sexo_txt}{grupo_txt} DE {edad_resumen}, QUIEN CONSULTA POR {str(enfermedad_actual).upper()}. "
        f"AL MOMENTO DE LA VALORACIÓN SE ENCUENTRA EN CONDICIONES GENERALES ESTABLES. "
        f"SE CORRELACIONA CLÍNICA Y PARACLÍNICAMENTE PARA DEFINIR CONDUCTA."
    ).strip()

    st.subheader("Análisis")
    if st.session_state.get(f"{prefix}_analisis_base") != analisis_default:
        if st.session_state.get(f"{prefix}_analisis") == st.session_state.get(f"{prefix}_analisis_base", ""):
            st.session_state[f"{prefix}_analisis"] = analisis_default
        st.session_state[f"{prefix}_analisis_base"] = analisis_default

    analisis = st.text_area("Análisis clínico", key=f"{prefix}_analisis", height=180)

    st.subheader("Diagnósticos")
    diagnosticos = st.text_area("Diagnósticos", key=f"{prefix}_diagnosticos", height=120)
    observacion_dx = st.text_area("Observación diagnóstica", key=f"{prefix}_obs_dx", height=100)

    st.subheader("Plan")
    plan = st.text_area("Plan", key=f"{prefix}_plan", height=220)

    col_btn_1, col_btn_2 = st.columns(2)
    generar = col_btn_1.button("Generar Historia Clínica", key=f"{prefix}_generar", use_container_width=True)
    if col_btn_2.button("Limpiar y empezar otra historia", key=f"{prefix}_limpiar", use_container_width=True):
        st.session_state[f"{prefix}_clear_requested"] = True
        st.rerun()

    if generar:
        fecha_str = fecha_nacimiento.strftime("%d/%m/%Y") if fecha_nacimiento else ""
        historia = f"""
{titulo.upper()}

DATOS DE IDENTIFICACIÓN:
NOMBRES Y APELLIDOS: {nombre}
TIPO DE DOCUMENTO: {tipo_documento}
DOCUMENTO: {documento}
FECHA DE NACIMIENTO: {fecha_str}
EPS: {eps}
INFORMANTE / ACOMPAÑANTE: {informante}

MOTIVO DE CONSULTA:
{motivo}

ENFERMEDAD ACTUAL:
{enfermedad_actual}

ANTECEDENTES:
{antecedentes}
"""
        if mostrar_neurodesarrollo:
            historia += f"""

NEURODESARROLLO:
{neuro}
"""

        historia += f"""

REVISIÓN POR SISTEMAS:
{revision}

SIGNOS VITALES:
TA {ta} mmHg FC: {fc} lpm FR: {fr} rpm SpO2: {sat}% T: {temp} °C

ANTROPOMETRÍA:
PESO: {peso} kg TALLA: {talla} cm"""

        if es_pediatrica:
            historia += f" PC: {pc} cm"

        historia += f"""

EXAMEN FÍSICO:
{examen}

ANÁLISIS:
{analisis}

DIAGNÓSTICOS:
{diagnosticos}

OBSERVACIÓN DIAGNÓSTICA:
{observacion_dx}

PLAN:
{plan}
"""

        fecha_guardado = datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        identificador = f"{fecha_guardado} | {nombre or 'SIN NOMBRE'} | {documento or 'SIN DOCUMENTO'}"
        _save_history(
            history_path,
            {
                "id": identificador,
                "fecha_guardado": fecha_guardado,
                "nombre": nombre,
                "documento": documento,
                "historia": historia.upper(),
            },
        )

        secciones = [
            ("DATOS DE IDENTIFICACIÓN", f"NOMBRES Y APELLIDOS: {nombre}\nTIPO DE DOCUMENTO: {tipo_documento}\nDOCUMENTO: {documento}\nFECHA DE NACIMIENTO: {fecha_str}\nEPS: {eps}\nINFORMANTE / ACOMPAÑANTE: {informante}"),
            ("MOTIVO DE CONSULTA", motivo),
            ("ENFERMEDAD ACTUAL", enfermedad_actual),
            ("ANTECEDENTES", antecedentes),
        ]
        if mostrar_neurodesarrollo:
            secciones.append(("NEURODESARROLLO", neuro))
        secciones.extend(
            [
                ("REVISIÓN POR SISTEMAS", revision),
                ("SIGNOS VITALES", f"TA {ta} mmHg FC: {fc} lpm FR: {fr} rpm SpO2: {sat}% T: {temp} °C"),
                ("ANTROPOMETRÍA", f"PESO: {peso} kg TALLA: {talla} cm" + (f" PC: {pc} cm" if es_pediatrica else "")),
                ("EXAMEN FÍSICO", examen),
                ("ANÁLISIS", analisis),
                ("DIAGNÓSTICOS", diagnosticos),
                ("OBSERVACIÓN DIAGNÓSTICA", observacion_dx),
                ("PLAN", plan),
            ]
        )

        st.success("Historia clínica generada")
        docx_bytes = generar_docx_informe(titulo.upper(), secciones)
        ruta_docx_guardado = guardar_docx_exportado(
            docx_bytes,
            f"{nombre or 'historia'}_consulta",
            subcarpeta=prefix,
        )
        nombre_docx = f"{(nombre or 'historia').strip().replace(' ', '_')}_consulta.docx"
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
            st.info("Google Drive no está configurado aún. El Word sí quedó guardado localmente y disponible para descarga.")
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
        else:
            st.info("Aún no hay historias guardadas.")
