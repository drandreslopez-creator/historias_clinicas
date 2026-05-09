import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from core.calculos import calcular_edad
from core.clasificacion import grupo_etario
from herramientas.neurodesarrollo import obtener_neurodesarrollo
from servicios.pediatria_urgencias import (
    ANTECEDENTES_DEFAULT as ANTECEDENTES_URGENCIAS_DEFAULT,
    EXAMEN_DEFAULT as EXAMEN_URGENCIAS_DEFAULT,
    PLAN_DEFAULT as PLAN_URGENCIAS_DEFAULT,
    REVISION_DEFAULT as REVISION_URGENCIAS_DEFAULT,
    aplanar_grupos_busqueda,
    cargar_cie10,
    coincide_grupos,
    construir_nombre_base_docx,
    construir_grupos_busqueda,
    eliminar_historia_guardada,
    expandir_terminos_busqueda,
    generar_docx_informe,
    guardar_docx_exportado,
    puntuar_diagnostico,
    subir_docx_a_google_drive,
    render_informe_html,
    traducir_cie10_descripcion,
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


def _construir_diagnostico_cie10(prefix):
    cie10 = cargar_cie10()
    busqueda_cie10 = st.text_input(
        "Buscar CIE-10 por código o descripción",
        key=f"{prefix}_consulta_cie10_busqueda",
    ).strip()

    if busqueda_cie10:
        grupos_busqueda = construir_grupos_busqueda(busqueda_cie10)
        if grupos_busqueda:
            terminos = aplanar_grupos_busqueda(grupos_busqueda)
        else:
            terminos = list(expandir_terminos_busqueda(busqueda_cie10))

        cie10_filtrado = cie10.copy()
        if grupos_busqueda:
            cie10_filtrado_estricto = cie10_filtrado[
                cie10_filtrado.apply(lambda row: coincide_grupos(row, grupos_busqueda), axis=1)
            ]
            if not cie10_filtrado_estricto.empty:
                cie10_filtrado = cie10_filtrado_estricto
        if cie10_filtrado.empty:
            cie10_filtrado = cie10.iloc[0:0].copy()
        else:
            cie10_filtrado["score_busqueda"] = cie10_filtrado.apply(
                lambda row: puntuar_diagnostico(row, terminos, grupos_busqueda),
                axis=1,
            )
            cie10_filtrado = cie10_filtrado[cie10_filtrado["score_busqueda"] > 0]
            cie10_filtrado = cie10_filtrado.sort_values(
                by=["score_busqueda", "code_normalized"],
                ascending=[False, True],
            ).head(20)
    else:
        cie10_filtrado = cie10.iloc[0:0]

    if cie10_filtrado.empty:
        if busqueda_cie10:
            st.caption("No se encontraron diagnósticos CIE-10 con esa búsqueda.")
        return ""

    cie10_filtrado = cie10_filtrado.copy()
    cie10_filtrado["description_es"] = cie10_filtrado["description"].map(traducir_cie10_descripcion)
    cie10_filtrado["label_es"] = cie10_filtrado["code"].astype(str) + " - " + cie10_filtrado["description_es"]

    with st.expander(f"Resultados de diagnóstico ({len(cie10_filtrado)})", expanded=False):
        diagnostico = st.selectbox(
            "Diagnóstico CIE-10",
            cie10_filtrado["label_es"].tolist(),
            index=None,
            placeholder="Seleccione un diagnóstico",
            key=f"{prefix}_consulta_cie10_dx",
        )
    return diagnostico or ""


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
    mostrar_modalidad_consulta=True,
    mostrar_pb=None,
    modo_pediatrico_urgencias_primera_vez=False,
    modalidad_consulta_forzada=None,
):
    if modo_pediatrico_urgencias_primera_vez and es_pediatrica:
        antecedentes_default = antecedentes_default or ANTECEDENTES_URGENCIAS_DEFAULT
    else:
        antecedentes_default = antecedentes_default or (ANTECEDENTES_DEFAULT if es_pediatrica else ANTECEDENTES_ADULTO_DEFAULT)
    plan_default = plan_default or PLAN_DEFAULT
    if mostrar_pb is None:
        mostrar_pb = es_pediatrica
    history_path = _historia_path(history_filename)

    defaults = {
        f"{prefix}_nombre": "",
        f"{prefix}_tipo_documento": None,
        f"{prefix}_documento": "",
        f"{prefix}_fecha_nacimiento": None,
        f"{prefix}_sexo": None,
        f"{prefix}_eps": "",
        f"{prefix}_telefono": "",
        f"{prefix}_informante": "",
        f"{prefix}_motivo": "",
        f"{prefix}_enfermedad_actual": "",
        f"{prefix}_antecedentes": antecedentes_default,
        f"{prefix}_revision": "NIEGA OTROS SINTOMAS/SIGNOS A LOS YA MENCIONADOS.",
        f"{prefix}_fc": 0.0,
        f"{prefix}_fr": 0.0,
        f"{prefix}_ta": "",
        f"{prefix}_sat": 0.0,
        f"{prefix}_glucometria": 0.0,
        f"{prefix}_temp": 0.0,
        f"{prefix}_pb": 0.0,
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
        f"{prefix}_modalidad_consulta": modalidad_consulta_forzada or "PRIMERA VEZ",
    }

    if st.session_state.pop(f"{prefix}_clear_requested", False):
        _clear_state(prefix, defaults)
        st.rerun()

    _init_state(defaults)

    st.header(f"📌 {titulo}")

    modalidad_consulta = modalidad_consulta_forzada
    if modalidad_consulta_forzada is not None:
        st.info(f"Modalidad de la consulta: {modalidad_consulta_forzada}")
    elif mostrar_modalidad_consulta:
        modalidad_consulta = st.selectbox(
            "Modalidad de la consulta",
            ["PRIMERA VEZ", "CITA DE CONTROL"],
            key=f"{prefix}_modalidad_consulta",
        )
    else:
        modalidad_consulta = "PRIMERA VEZ"

    usar_modo_urgencias = bool(
        modo_pediatrico_urgencias_primera_vez
        and es_pediatrica
        and modalidad_consulta == "PRIMERA VEZ"
    )

    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombres y apellidos", key=f"{prefix}_nombre")
    with col2:
        sexo = st.selectbox(
            "Sexo",
            ["Masculino", "Femenino"],
            index=None,
            placeholder="Seleccione sexo",
            key=f"{prefix}_sexo",
        )

    col3, col4 = st.columns(2)
    with col3:
        tipo_documento = st.selectbox(
            "Tipo de documento",
            ["NV", "RC", "TI", "CC", "CE", "PEP", "PS", "OTRO"],
            index=None,
            placeholder="Seleccione tipo de documento",
            key=f"{prefix}_tipo_documento",
        )
    with col4:
        documento = st.text_input("Documento", key=f"{prefix}_documento")

    col5, col6 = st.columns(2)
    with col5:
        fecha_nacimiento = st.date_input(
            "Fecha de nacimiento",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key=f"{prefix}_fecha_nacimiento",
        )
    with col6:
        informante = st.text_input(
            "Informante / acompañante",
            key=f"{prefix}_informante",
        )

    col7, col8 = st.columns(2)
    with col7:
        eps = st.text_input("EPS", key=f"{prefix}_eps")
    with col8:
        telefono = st.text_input("Telefono", key=f"{prefix}_telefono")

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
    if usar_modo_urgencias and st.session_state.get(f"{prefix}_revision") == "NIEGA OTROS SINTOMAS/SIGNOS A LOS YA MENCIONADOS.":
        st.session_state[f"{prefix}_revision"] = REVISION_URGENCIAS_DEFAULT
    revision = st.text_area("Revisión", key=f"{prefix}_revision")

    st.subheader("Signos vitales")
    col_sv_1, col_sv_2, col_sv_3 = st.columns(3)
    with col_sv_1:
        ta = st.text_input("TA (mmHg)", key=f"{prefix}_ta")
    with col_sv_2:
        fc = st.number_input("FC (lpm)", min_value=0.0, key=f"{prefix}_fc")
    with col_sv_3:
        sat = st.number_input("SpO2 (%)", min_value=0.0, key=f"{prefix}_sat")

    col_sv_4, col_sv_5, col_sv_6 = st.columns(3)
    with col_sv_4:
        fr = st.number_input("FR (rpm)", min_value=0.0, key=f"{prefix}_fr")
    with col_sv_5:
        glucometria = st.number_input("Glucometría (mg/dl)", min_value=0.0, key=f"{prefix}_glucometria")
    with col_sv_6:
        temp = st.number_input("Temperatura (°C)", min_value=0.0, key=f"{prefix}_temp")

    col_sv_7, col_sv_8 = st.columns(2)
    with col_sv_7:
        peso = st.number_input("Peso (kg)", min_value=0.0, key=f"{prefix}_peso")
    with col_sv_8:
        talla = st.number_input("Talla (cm)", min_value=0.0, key=f"{prefix}_talla")

    if es_pediatrica:
        col_sv_9, col_sv_10 = st.columns(2)
        with col_sv_9:
            pc = st.number_input("Perímetro cefálico (cm)", min_value=0.0, key=f"{prefix}_pc")
        with col_sv_10:
            if mostrar_pb:
                pb = st.number_input("PB (cm)", min_value=0.0, key=f"{prefix}_pb")
            else:
                pb = 0.0
    else:
        pc = 0.0
        pb = 0.0

    st.subheader("Examen físico")
    if usar_modo_urgencias and st.session_state.get(f"{prefix}_examen") == EXAMEN_DEFAULT:
        st.session_state[f"{prefix}_examen"] = EXAMEN_URGENCIAS_DEFAULT
    examen = st.text_area("Examen físico", key=f"{prefix}_examen", height=300 if usar_modo_urgencias else 260)

    sexo_txt = (sexo or "").upper()
    grupo_txt = f" {grupo.upper()}" if grupo else ""
    edad_resumen = f"{años} AÑOS" if años > 0 else (f"{meses} MESES" if fecha_nacimiento else "")
    if usar_modo_urgencias:
        analisis_default = (
            f"PACIENTE {sexo_txt}{grupo_txt} DE {edad_resumen}, QUIEN CONSULTA POR {str(enfermedad_actual).upper()}. "
            f"AL INGRESO PACIENTE QUE LUCE EN ACEPTABLES CONDICIONES GENERALES, BUEN ESTADO DE HIDRATACIÓN, "
            f"HEMODINÁMICAMENTE ESTABLE, BUEN PATRÓN RESPIRATORIO, SIN REQUERIMIENTO DE O2 SUPLEMENTARIO, "
            f"SIN SIGNOS DE ALARMA ABDOMINAL, SIN DISTERMIAS, NO ASPECTO TÓXICO, SIN EDEMAS, SIN DÉFICIT NEUROLÓGICO, "
            f"PIEL BIEN PERFUNDIDA SIN LESIONES. SE INDICA MANEJO... SE BRINDA INFORMACIÓN A FAMILIARES, SE ACLARAN DUDAS."
        ).strip()
    else:
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
    if usar_modo_urgencias:
        diagnosticos = _construir_diagnostico_cie10(prefix)
    else:
        diagnosticos = st.text_area("Diagnósticos", key=f"{prefix}_diagnosticos", height=120)
    observacion_dx = st.text_area("Observación diagnóstica", key=f"{prefix}_obs_dx", height=100)

    st.subheader("Plan")
    if usar_modo_urgencias and st.session_state.get(f"{prefix}_plan") == plan_default:
        st.session_state[f"{prefix}_plan"] = PLAN_URGENCIAS_DEFAULT
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

MODALIDAD DE LA CONSULTA:
{modalidad_consulta or ""}

DATOS DE IDENTIFICACIÓN:
NOMBRES Y APELLIDOS: {nombre}
TIPO DE DOCUMENTO: {tipo_documento}
DOCUMENTO: {documento}
FECHA DE NACIMIENTO: {fecha_str}
EPS: {eps}
TELEFONO: {telefono}
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
TA {ta} mmHg FC: {fc} lpm SpO2: {sat}% FR: {fr} rpm GLUCOMETRÍA: {glucometria} mg/dl T: {temp} °C{f" PB: {pb} cm" if mostrar_pb else ""}

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

        secciones = [
            ("MODALIDAD DE LA CONSULTA", modalidad_consulta or ""),
            ("DATOS DE IDENTIFICACIÓN", f"NOMBRES Y APELLIDOS: {nombre}\nTIPO DE DOCUMENTO: {tipo_documento}\nDOCUMENTO: {documento}\nFECHA DE NACIMIENTO: {fecha_str}\nEPS: {eps}\nTELEFONO: {telefono}\nINFORMANTE / ACOMPAÑANTE: {informante}"),
            ("MOTIVO DE CONSULTA", motivo),
            ("ENFERMEDAD ACTUAL", enfermedad_actual),
            ("ANTECEDENTES", antecedentes),
        ]
        if mostrar_neurodesarrollo:
            secciones.append(("NEURODESARROLLO", neuro))
        secciones.extend(
            [
                ("REVISIÓN POR SISTEMAS", revision),
                ("SIGNOS VITALES", f"TA {ta} mmHg FC: {fc} lpm SpO2: {sat}% FR: {fr} rpm GLUCOMETRÍA: {glucometria} mg/dl T: {temp} °C" + (f" PB: {pb} cm" if mostrar_pb else "")),
                ("ANTROPOMETRÍA", f"PESO: {peso} kg TALLA: {talla} cm" + (f" PC: {pc} cm" if es_pediatrica else "")),
                ("EXAMEN FÍSICO", examen),
                ("ANÁLISIS", analisis),
                ("DIAGNÓSTICOS", diagnosticos),
                ("OBSERVACIÓN DIAGNÓSTICA", observacion_dx),
                ("PLAN", plan),
            ]
        )

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
            st.info("Google Drive no está configurado aún. El Word sí quedó guardado localmente y disponible para descarga.")

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
