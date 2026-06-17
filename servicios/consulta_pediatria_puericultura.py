import hashlib
import json
from datetime import date, datetime

import streamlit as st

from core.calculos import calcular_edad
from herramientas.neurodesarrollo import obtener_neurodesarrollo
from servicios.consulta_externa_base import (
    _clear_state,
    _construir_diagnostico_cie10,
    _historia_path,
    _init_state,
    _load_histories,
    _save_history,
)
from servicios.pediatria_urgencias import (
    ANTECEDENTES_DEFAULT as ANTECEDENTES_URGENCIAS_DEFAULT,
    EXAMEN_DEFAULT as EXAMEN_URGENCIAS_DEFAULT,
    PLAN_DEFAULT as PLAN_URGENCIAS_DEFAULT,
    REVISION_DEFAULT as REVISION_URGENCIAS_DEFAULT,
    BOGOTA_TZ,
    actualizar_texto_extraido,
    complementar_analisis_con_ia,
    construir_conducta_final_analisis,
    construir_conducta_sugerida_analisis,
    construir_resumen_paraclinicos_para_analisis,
    construir_resumen_signos_para_analisis,
    construir_nombre_base_docx,
    extraer_destinatario_informacion,
    extraer_resumen_antecedentes_para_analisis,
    extraer_resumen_examen_para_analisis,
    fusionar_analisis_editado_con_base_nueva,
    eliminar_historia_guardada,
    generar_analisis_asistido_urgencias,
    generar_docx_informe,
    guardar_docx_exportado,
    render_informe_html,
    subir_docx_a_google_drive,
)


PREFIX = "ped_pueri"
TITULO = "CONSULTA EXTERNA - PEDIATRÍA Y PUERICULTURA"
HISTORY_FILENAME = "historias_pediatria_puericultura.jsonl"

MOTIVO_PRIMERA_VEZ_DEFAULT = "VALORACIÓN INTEGRAL PEDIÁTRICA / INGRESO A CONTROL DE CRECIMIENTO Y DESARROLLO."
MOTIVO_CONTROL_DEFAULT = "CITA DE CONTROL DE CRECIMIENTO, DESARROLLO Y PUERICULTURA."

ALIMENTACION_PRIMERA_VEZ_DEFAULT = """LACTANCIA / ALIMENTACIÓN ACTUAL:
FRECUENCIA:
TOLERANCIA:
ALIMENTACIÓN COMPLEMENTARIA:
SUPLEMENTACIÓN / MICRONUTRIENTES:"""

ALIMENTACION_CONTROL_DEFAULT = """CAMBIOS DESDE EL ÚLTIMO CONTROL:
APETITO / ACEPTACIÓN:
TOLERANCIA:
SUPLEMENTACIÓN:
OBSERVACIONES:"""

SUENO_ELIMINACION_DEFAULT = """SUEÑO:
ELIMINACIÓN URINARIA:
ELIMINACIÓN INTESTINAL:
CONTROL DE ESFÍNTERES:
OTRAS OBSERVACIONES:"""

VACUNAS_DEFAULT = """ESQUEMA DE VACUNACIÓN:
PAI AL DÍA: SÍ / NO
VACUNAS PENDIENTES:
REACCIONES PREVIAS:
OBSERVACIONES:"""

ENTORNO_PRIMERA_VEZ_DEFAULT = """CUIDADOR PRINCIPAL:
DINÁMICA FAMILIAR:
ESCOLARIDAD / JARDÍN:
PANTALLAS:
ACTIVIDAD FÍSICA / JUEGO:
RIESGOS AMBIENTALES:
RED DE APOYO:"""

ENTORNO_CONTROL_DEFAULT = """CAMBIOS EN DINÁMICA FAMILIAR:
ESCOLARIDAD / RENDIMIENTO:
PANTALLAS:
ACTIVIDAD FÍSICA / JUEGO:
RIESGOS AMBIENTALES:
OBSERVACIONES:"""

ANTECEDENTES_CONTROL_DEFAULT = """ACTUALIZACIÓN DE ANTECEDENTES DESDE EL ÚLTIMO CONTROL:
PATOLÓGICOS:
HOSPITALARIOS:
FARMACOLÓGICOS:
ALÉRGICOS:
QUIRÚRGICOS:
FAMILIARES:"""

EXAMEN_PUERICULTURA_DEFAULT = """PACIENTE LUCE EN BUEN ESTADO GENERAL, ALERTA, REACTIVO, BIEN HIDRATADO, SIN SIGNOS DE DIFICULTAD RESPIRATORIA NI COMPROMISO AGUDO.

CABEZA: NORMOCÉFALA, SIN LESIONES.
OJOS: CONJUNTIVAS NORMALES, FIJA Y SIGUE SEGÚN EDAD.
OÍDOS: SIN ALTERACIONES EVIDENTES.
NARIZ: PERMEABLE.
OROFARINGE: MUCOSAS HÚMEDAS, SIN LESIONES.
CUELLO: MÓVIL, SIN ADENOPATÍAS.
TÓRAX: SIMÉTRICO, SIN TIRAJES.
CARDIOPULMONAR: RUIDOS CARDÍACOS RÍTMICOS, SIN SOPLOS, MURMULLO VESICULAR CONSERVADO.
ABDOMEN: BLANDO, NO DOLOROSO, SIN MASAS.
GENITALES: ACORDES PARA LA EDAD Y SEXO, SEGÚN VALORACIÓN.
EXTREMIDADES: SIMÉTRICAS, SIN EDEMAS NI DEFORMIDADES.
NEUROLÓGICO: ALERTA, INTERACTIVO, TONO Y FUERZA ACORDES.
PIEL: ÍNTEGRA, BIEN PERFUNDIDA, SIN LESIONES RELEVANTES."""

ANALISIS_PRIMERA_VEZ_DEFAULT = """PACIENTE EN VALORACIÓN INTEGRAL DE PRIMERA VEZ PARA PEDIATRÍA Y PUERICULTURA. AL MOMENTO DE LA CONSULTA SE ENCUENTRA HEMODINÁMICAMENTE ESTABLE, SIN SIGNOS DE ENFERMEDAD AGUDA APARENTE. SE CORRELACIONAN ANTECEDENTES, ESTADO NUTRICIONAL, CRECIMIENTO, DESARROLLO, ESQUEMA DE VACUNACIÓN, HÁBITOS Y ENTORNO PARA DEFINIR CONDUCTA, EDUCACIÓN Y SEGUIMIENTO."""

ANALISIS_CONTROL_DEFAULT = """PACIENTE EN CITA DE CONTROL DE PEDIATRÍA Y PUERICULTURA. SE VALORA EVOLUCIÓN CLÍNICA, CRECIMIENTO, DESARROLLO, ALIMENTACIÓN, VACUNACIÓN Y HÁBITOS DESDE EL ÚLTIMO CONTROL. AL MOMENTO SE ENCUENTRA ESTABLE Y SE DEFINE CONDUCTA SEGÚN HALLAZGOS."""

PLAN_PUERICULTURA_DEFAULT = """- EDUCACIÓN A CUIDADORES SEGÚN EDAD
- ORIENTACIÓN EN ALIMENTACIÓN Y HÁBITOS SALUDABLES
- FORTALECER ESTIMULACIÓN DEL DESARROLLO
- VIGILAR SIGNOS DE ALARMA
- CONTROL SEGÚN HALLAZGOS Y EDAD"""


def _float_or_none_local(valor):
    texto = str(valor or "").strip().replace(",", ".")
    if not texto:
        return None
    try:
        return float(texto)
    except Exception:
        return None

TAMIZAJES_LACTANTE_DEFAULT = """TAMIZ VISUAL:
TAMIZ AUDITIVO:
SALUD ORAL:
ANEMIA / MICRONUTRIENTES:
RIESGO PSICOSOCIAL:
OTROS TAMIZAJES SEGÚN EDAD:"""

TAMIZAJES_PREESCOLAR_ESCOLAR_DEFAULT = """TAMIZ VISUAL:
TAMIZ AUDITIVO:
SALUD ORAL:
RENDIMIENTO / ADAPTACIÓN ESCOLAR:
ALTERACIONES DEL SUEÑO:
RIESGO PSICOSOCIAL / VIOLENCIAS:
OTROS TAMIZAJES SEGÚN EDAD:"""

TAMIZAJES_ADOLESCENTE_DEFAULT = """TAMIZ VISUAL:
TAMIZ AUDITIVO:
SALUD ORAL:
SALUD MENTAL / RIESGO EMOCIONAL:
CONSUMO DE SUSTANCIAS:
RIESGO SEXUAL Y REPRODUCTIVO:
RIESGO PSICOSOCIAL / VIOLENCIAS:
OTROS TAMIZAJES SEGÚN EDAD:"""

PUBERAL_DEFAULT = """DESARROLLO PUBERAL / TANNER:
MENARQUIA / ESPERMARQUIA:
CICLOS MENSTRUALES / SÍNTOMAS ASOCIADOS:
EDUCACIÓN EN CAMBIOS PUBERALES:
OBSERVACIONES:"""


def _obtener_tamizajes_default(años, meses):
    edad_meses = años * 12 + meses
    if edad_meses < 24:
        return TAMIZAJES_LACTANTE_DEFAULT
    if edad_meses < 120:
        return TAMIZAJES_PREESCOLAR_ESCOLAR_DEFAULT
    return TAMIZAJES_ADOLESCENTE_DEFAULT


def _obtener_plan_puericultura_default(años, meses, modalidad):
    edad_meses = años * 12 + meses
    base = []
    if modalidad == "PRIMERA VEZ":
        base.append("- VALORACIÓN INTEGRAL DE INGRESO A PEDIATRÍA Y PUERICULTURA")
    else:
        base.append("- VALORAR EVOLUCIÓN DESDE EL ÚLTIMO CONTROL")

    if edad_meses < 6:
        base.extend(
            [
                "- FORTALECER LACTANCIA MATERNA Y TÉCNICA DE ALIMENTACIÓN",
                "- ORIENTAR SIGNOS DE ALARMA DEL LACTANTE MENOR",
                "- FOMENTAR ESTIMULACIÓN TEMPRANA ACORDE A LA EDAD",
            ]
        )
    elif edad_meses < 24:
        base.extend(
            [
                "- REFORZAR ALIMENTACIÓN COMPLEMENTARIA Y HÁBITOS SALUDABLES",
                "- PROMOVER ESTIMULACIÓN DEL DESARROLLO Y LENGUAJE",
                "- EDUCACIÓN SOBRE PREVENCIÓN DE ACCIDENTES EN CASA",
            ]
        )
    elif edad_meses < 120:
        base.extend(
            [
                "- ORIENTAR HÁBITOS DE SUEÑO, PANTALLAS Y ACTIVIDAD FÍSICA",
                "- PROMOVER HIGIENE ORAL Y CONTROLES VISUAL/AUDITIVO SEGÚN EDAD",
                "- EDUCACIÓN EN ESCOLARIDAD, CONDUCTA Y REDES DE APOYO",
            ]
        )
    else:
        base.extend(
            [
                "- ORIENTAR HÁBITOS SALUDABLES, SUEÑO Y ACTIVIDAD FÍSICA",
                "- EDUCACIÓN EN SALUD MENTAL, CAMBIOS PUBERALES Y ENTORNO SEGURO",
                "- CONSEJERÍA EN PREVENCIÓN DE VIOLENCIAS, CONSUMO Y RIESGOS SEXUALES SEGÚN EDAD",
            ]
        )

    base.extend(
        [
            "- REVISAR Y ACTUALIZAR ESQUEMA DE VACUNACIÓN SEGÚN PAI",
            "- VIGILAR SIGNOS DE ALARMA",
            "- CONTROL SEGÚN EDAD Y HALLAZGOS",
        ]
    )
    return "\n".join(base)


def render():
    history_path = _historia_path(HISTORY_FILENAME)

    defaults = {
        f"{PREFIX}_nombre": "",
        f"{PREFIX}_tipo_documento": None,
        f"{PREFIX}_documento": "",
        f"{PREFIX}_fecha_nacimiento": None,
        f"{PREFIX}_sexo": None,
        f"{PREFIX}_eps": "",
        f"{PREFIX}_telefono": "",
        f"{PREFIX}_informante": "",
        f"{PREFIX}_modalidad_consulta": "PRIMERA VEZ",
        f"{PREFIX}_motivo": MOTIVO_PRIMERA_VEZ_DEFAULT,
        f"{PREFIX}_enfermedad_actual": "",
        f"{PREFIX}_antecedentes": ANTECEDENTES_URGENCIAS_DEFAULT,
        f"{PREFIX}_alimentacion": ALIMENTACION_PRIMERA_VEZ_DEFAULT,
        f"{PREFIX}_sueno_eliminacion": SUENO_ELIMINACION_DEFAULT,
        f"{PREFIX}_vacunas": VACUNAS_DEFAULT,
        f"{PREFIX}_entorno": ENTORNO_PRIMERA_VEZ_DEFAULT,
        f"{PREFIX}_revision": REVISION_URGENCIAS_DEFAULT,
        f"{PREFIX}_ta": "",
        f"{PREFIX}_fc": "",
        f"{PREFIX}_fr": "",
        f"{PREFIX}_sat": "",
        f"{PREFIX}_glucometria": "",
        f"{PREFIX}_temp": "",
        f"{PREFIX}_peso": "",
        f"{PREFIX}_talla": "",
        f"{PREFIX}_pc": "",
        f"{PREFIX}_pb": "",
        f"{PREFIX}_neuro": "",
        f"{PREFIX}_examen": EXAMEN_PUERICULTURA_DEFAULT,
        f"{PREFIX}_paraclinicos_texto": "",
        f"{PREFIX}_paraclinicos_auto": "",
        f"{PREFIX}_paraclinicos_pdf_sig": "",
        f"{PREFIX}_imagenes_texto": "",
        f"{PREFIX}_imagenes_auto": "",
        f"{PREFIX}_imagenes_pdf_sig": "",
        f"{PREFIX}_analisis": ANALISIS_PRIMERA_VEZ_DEFAULT,
        f"{PREFIX}_analisis_base": "",
        f"{PREFIX}_conducta_final_analisis": "PENDIENTE DEFINIR",
        f"{PREFIX}_diagnosticos": "",
        f"{PREFIX}_obs_dx": "",
        f"{PREFIX}_plan": PLAN_PUERICULTURA_DEFAULT,
        f"{PREFIX}_historia_consulta_id": None,
    }

    if st.session_state.pop(f"{PREFIX}_clear_requested", False):
        _clear_state(PREFIX, defaults)
        st.rerun()

    _init_state(defaults)

    st.header(TITULO)

    modalidad = st.selectbox(
        "Modalidad de la consulta",
        ["PRIMERA VEZ", "CITA DE CONTROL"],
        key=f"{PREFIX}_modalidad_consulta",
    )

    if st.session_state.get(f"{PREFIX}_modalidad_aplicada") != modalidad:
        if modalidad == "PRIMERA VEZ":
            st.session_state[f"{PREFIX}_motivo"] = MOTIVO_PRIMERA_VEZ_DEFAULT
            st.session_state[f"{PREFIX}_antecedentes"] = ANTECEDENTES_URGENCIAS_DEFAULT
            st.session_state[f"{PREFIX}_alimentacion"] = ALIMENTACION_PRIMERA_VEZ_DEFAULT
            st.session_state[f"{PREFIX}_entorno"] = ENTORNO_PRIMERA_VEZ_DEFAULT
        else:
            st.session_state[f"{PREFIX}_motivo"] = MOTIVO_CONTROL_DEFAULT
            st.session_state[f"{PREFIX}_antecedentes"] = ANTECEDENTES_CONTROL_DEFAULT
            st.session_state[f"{PREFIX}_alimentacion"] = ALIMENTACION_CONTROL_DEFAULT
            st.session_state[f"{PREFIX}_entorno"] = ENTORNO_CONTROL_DEFAULT
        st.session_state[f"{PREFIX}_modalidad_aplicada"] = modalidad

    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombres y apellidos", key=f"{PREFIX}_nombre")
    with col2:
        sexo = st.selectbox(
            "Sexo",
            ["Masculino", "Femenino"],
            index=None,
            placeholder="Seleccione sexo",
            key=f"{PREFIX}_sexo",
        )

    col3, col4 = st.columns(2)
    with col3:
        tipo_documento = st.selectbox(
            "Tipo de documento",
            ["NV", "RC", "TI", "CC", "CE", "PEP", "PS", "OTRO"],
            index=None,
            placeholder="Seleccione tipo de documento",
            key=f"{PREFIX}_tipo_documento",
        )
    with col4:
        documento = st.text_input("Documento", key=f"{PREFIX}_documento")

    col5, col6 = st.columns(2)
    with col5:
        fecha_nacimiento = st.date_input(
            "Fecha de nacimiento",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key=f"{PREFIX}_fecha_nacimiento",
        )
    with col6:
        informante = st.text_input("Informante / acompañante", key=f"{PREFIX}_informante")

    col7, col8 = st.columns(2)
    with col7:
        eps = st.text_input("EPS", key=f"{PREFIX}_eps")
    with col8:
        telefono = st.text_input("Telefono", key=f"{PREFIX}_telefono")

    años = meses = dias = 0
    if fecha_nacimiento:
        años, meses, dias = calcular_edad(fecha_nacimiento)
        st.info(f"Edad: {años} años, {meses} meses, {dias} días")
        neuro_default = obtener_neurodesarrollo(años, meses)
        if not st.session_state.get(f"{PREFIX}_neuro"):
            st.session_state[f"{PREFIX}_neuro"] = neuro_default

    st.subheader("Motivo de consulta")
    motivo = st.text_area("", key=f"{PREFIX}_motivo", height=90, label_visibility="collapsed")

    st.subheader("Enfermedad actual")
    enfermedad_actual = st.text_area("", key=f"{PREFIX}_enfermedad_actual", height=180, label_visibility="collapsed")

    st.subheader("Antecedentes")
    antecedentes = st.text_area("", key=f"{PREFIX}_antecedentes", height=230, label_visibility="collapsed")

    st.subheader("Alimentación")
    alimentacion = st.text_area("", key=f"{PREFIX}_alimentacion", height=180, label_visibility="collapsed")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Sueño y eliminación")
        sueno_eliminacion = st.text_area("", key=f"{PREFIX}_sueno_eliminacion", height=170, label_visibility="collapsed")
    with col_b:
        st.subheader("Vacunación")
        vacunas = st.text_area("", key=f"{PREFIX}_vacunas", height=170, label_visibility="collapsed")

    st.subheader("Entorno / hábitos")
    entorno = st.text_area("", key=f"{PREFIX}_entorno", height=180, label_visibility="collapsed")

    st.subheader("Neurodesarrollo")
    neuro = st.text_area("", key=f"{PREFIX}_neuro", height=180, label_visibility="collapsed")

    st.subheader("Revisión por sistemas")
    revision = st.text_area("", key=f"{PREFIX}_revision", height=150, label_visibility="collapsed")

    st.subheader("Signos vitales")
    col_sv_1, col_sv_2, col_sv_3 = st.columns(3)
    with col_sv_1:
        ta = st.text_input("TA (mmHg)", key=f"{PREFIX}_ta")
    with col_sv_2:
        fc = st.text_input("FC (lpm)", key=f"{PREFIX}_fc")
    with col_sv_3:
        sat = st.text_input("SpO2 (%)", key=f"{PREFIX}_sat")

    col_sv_4, col_sv_5, col_sv_6 = st.columns(3)
    with col_sv_4:
        fr = st.text_input("FR (rpm)", key=f"{PREFIX}_fr")
    with col_sv_5:
        glucometria = st.text_input("Glucometría (mg/dl)", key=f"{PREFIX}_glucometria")
    with col_sv_6:
        temp = st.text_input("Temperatura (°C)", key=f"{PREFIX}_temp")

    col_sv_7, col_sv_8 = st.columns(2)
    with col_sv_7:
        peso = st.text_input("Peso (kg)", key=f"{PREFIX}_peso")
    with col_sv_8:
        talla = st.text_input("Talla (cm)", key=f"{PREFIX}_talla")

    col_sv_9, col_sv_10 = st.columns(2)
    with col_sv_9:
        pc = st.text_input("Perímetro cefálico (cm)", key=f"{PREFIX}_pc")
    with col_sv_10:
        pb = st.text_input("PB (cm)", key=f"{PREFIX}_pb")

    st.subheader("Examen físico")
    examen = st.text_area("", key=f"{PREFIX}_examen", height=300, label_visibility="collapsed")

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

    paraclinicos_texto = st.text_area("Laboratorios", key=f"{PREFIX}_paraclinicos_texto", height=160)
    imagenes_texto = st.text_area("Imágenes", key=f"{PREFIX}_imagenes_texto", height=120)
    conducta_final_analisis = st.selectbox(
        "Conducta final",
        ["PENDIENTE DEFINIR", "OBSERVACIÓN", "HOSPITALIZACIÓN", "EGRESO", "REMISIÓN"],
        key=f"{PREFIX}_conducta_final_analisis",
    )

    grupo = grupo_etario(años) if fecha_nacimiento else ""
    resumen_antecedentes_analisis = extraer_resumen_antecedentes_para_analisis(antecedentes)
    destinatario_informacion = extraer_destinatario_informacion(informante)
    fc_num = _float_or_none_local(fc)
    fr_num = _float_or_none_local(fr)
    sat_num = _float_or_none_local(sat)
    glucometria_num = _float_or_none_local(glucometria)
    temp_num = _float_or_none_local(temp)
    peso_num = _float_or_none_local(peso)

    enfermedad_auto = (
        f"PACIENTE {(sexo or '').upper()} {grupo.upper() if grupo else ''} DE "
        f"{f'{años} AÑOS' if años > 0 else f'{meses} MESES' if fecha_nacimiento else ''}, "
        f"QUIEN CONSULTA POR {str(enfermedad_actual).upper()}"
    ).replace("  ", " ").strip(" ,")
    resumen_examen_analisis = extraer_resumen_examen_para_analisis(examen)
    resumen_signos_analisis = construir_resumen_signos_para_analisis(
        fc_num,
        fr_num,
        sat_num,
        temp_num,
        glucometria_num,
        peso_num,
        grupo,
    )
    resumen_paraclinicos_analisis = construir_resumen_paraclinicos_para_analisis(paraclinicos_texto)
    conducta_sugerida_analisis = construir_conducta_sugerida_analisis(
        enfermedad_actual,
        examen,
        paraclinicos_texto,
        resumen_signos_analisis,
    )
    conducta_final_texto = construir_conducta_final_analisis(
        conducta_final_analisis,
        conducta_sugerida_analisis,
    )
    analisis_default = generar_analisis_asistido_urgencias(
        enfermedad_auto,
        resumen_antecedentes_analisis,
        resumen_examen_analisis,
        resumen_signos_analisis,
        resumen_paraclinicos_analisis,
        conducta_final_texto,
        destinatario_informacion,
    )
    contexto_analisis_ia = {
        "titulo": TITULO,
        "modalidad_consulta": modalidad,
        "motivo_consulta": motivo,
        "enfermedad_actual": enfermedad_actual,
        "antecedentes": antecedentes,
        "parentesco_acompanante": destinatario_informacion,
        "conducta_final_definida": conducta_final_analisis,
        "conducta_sugerida_local": conducta_sugerida_analisis,
        "conducta_final_texto": conducta_final_texto,
        "alimentacion": alimentacion,
        "sueno_y_eliminacion": sueno_eliminacion,
        "vacunacion": vacunas,
        "entorno_habitos": entorno,
        "neurodesarrollo": neuro,
        "revision_por_sistemas": revision,
        "signos_vitales": {
            "ta": ta,
            "fc": fc,
            "fr": fr,
            "spo2": sat,
            "glucometria": glucometria,
            "temperatura": temp,
            "peso": peso,
            "talla": talla,
            "pc": pc,
            "pb": pb,
        },
        "examen_fisico": examen,
        "paraclinicos": paraclinicos_texto,
        "imagenes": imagenes_texto,
        "diagnosticos": st.session_state.get(f"{PREFIX}_diagnosticos", ""),
    }
    fingerprint_analisis_ia = hashlib.md5(
        json.dumps(contexto_analisis_ia, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    analisis_default = complementar_analisis_con_ia(
        analisis_default,
        contexto_analisis_ia,
        fingerprint_analisis_ia,
        instrucciones=(
            "Eres un asistente clínico que redacta análisis médicos pediátricos y de puericultura en español. "
            "Usa únicamente la información entregada. No inventes diagnósticos ni tratamientos. "
            "Redacta un solo párrafo en MAYÚSCULAS, claro, coherente y profesional, integrando motivo de consulta, "
            "enfermedad actual, antecedentes relevantes, estado general, crecimiento, desarrollo, hábitos y paraclínicos cuando existan. "
            "Formula una conducta coherente con la historia y usa el parentesco del acompañante en el cierre si está disponible."
        ),
    )

    st.subheader("Análisis")
    if st.session_state.get(f"{PREFIX}_analisis_base") != analisis_default:
        if st.session_state.get(f"{PREFIX}_analisis") == st.session_state.get(f"{PREFIX}_analisis_base", ""):
            st.session_state[f"{PREFIX}_analisis"] = analisis_default
        else:
            merge_fp = hashlib.md5(
                json.dumps(
                    {
                        "actual": st.session_state.get(f"{PREFIX}_analisis", ""),
                        "base_anterior": st.session_state.get(f"{PREFIX}_analisis_base", ""),
                        "base_nueva": analisis_default,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            st.session_state[f"{PREFIX}_analisis"] = fusionar_analisis_editado_con_base_nueva(
                st.session_state.get(f"{PREFIX}_analisis", ""),
                st.session_state.get(f"{PREFIX}_analisis_base", ""),
                analisis_default,
                merge_fp,
            )
        st.session_state[f"{PREFIX}_analisis_base"] = analisis_default
    analisis = st.text_area("", key=f"{PREFIX}_analisis", height=180, label_visibility="collapsed")

    st.subheader("Diagnósticos")
    diagnosticos = _construir_diagnostico_cie10(PREFIX)
    observacion_dx = st.text_area("Observación diagnóstica", key=f"{PREFIX}_obs_dx", height=110)

    st.subheader("Plan")
    plan = st.text_area("", key=f"{PREFIX}_plan", height=220, label_visibility="collapsed")

    col_btn_1, col_btn_2 = st.columns(2)
    generar = col_btn_1.button("Generar Historia Clínica", key=f"{PREFIX}_generar", use_container_width=True)
    if col_btn_2.button("Limpiar y empezar otra historia", key=f"{PREFIX}_limpiar", use_container_width=True):
        st.session_state[f"{PREFIX}_clear_requested"] = True
        st.rerun()

    if generar:
        fecha_str = fecha_nacimiento.strftime("%d/%m/%Y") if fecha_nacimiento else ""
        historia = f"""
{TITULO.upper()}

MODALIDAD DE LA CONSULTA:
{modalidad}

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

ALIMENTACIÓN:
{alimentacion}

SUEÑO Y ELIMINACIÓN:
{sueno_eliminacion}

VACUNACIÓN:
{vacunas}

ENTORNO / HÁBITOS:
{entorno}

NEURODESARROLLO:
{neuro}

REVISIÓN POR SISTEMAS:
{revision}

SIGNOS VITALES:
TA {ta} mmHg FC: {fc} lpm SpO2: {sat}% FR: {fr} rpm GLUCOMETRÍA: {glucometria} mg/dl T: {temp} °C

ANTROPOMETRÍA:
PESO: {peso} kg TALLA: {talla} cm PC: {pc} cm PB: {pb} cm

EXAMEN FÍSICO:
{examen}

PARACLÍNICOS:
{paraclinicos_texto}

IMÁGENES:
{imagenes_texto}

ANÁLISIS:
{analisis}

DIAGNÓSTICOS:
{diagnosticos}

OBSERVACIÓN DIAGNÓSTICA:
{observacion_dx}

PLAN:
{plan}
""".strip()

        secciones = [
            ("MODALIDAD DE LA CONSULTA", modalidad),
            ("DATOS DE IDENTIFICACIÓN", f"NOMBRES Y APELLIDOS: {nombre}\nTIPO DE DOCUMENTO: {tipo_documento}\nDOCUMENTO: {documento}\nFECHA DE NACIMIENTO: {fecha_str}\nEPS: {eps}\nTELEFONO: {telefono}\nINFORMANTE / ACOMPAÑANTE: {informante}"),
            ("MOTIVO DE CONSULTA", motivo),
            ("ENFERMEDAD ACTUAL", enfermedad_actual),
            ("ANTECEDENTES", antecedentes),
            ("ALIMENTACIÓN", alimentacion),
            ("SUEÑO Y ELIMINACIÓN", sueno_eliminacion),
            ("VACUNACIÓN", vacunas),
            ("ENTORNO / HÁBITOS", entorno),
            ("NEURODESARROLLO", neuro),
            ("REVISIÓN POR SISTEMAS", revision),
            ("SIGNOS VITALES", f"TA {ta} mmHg FC: {fc} lpm SpO2: {sat}% FR: {fr} rpm GLUCOMETRÍA: {glucometria} mg/dl T: {temp} °C"),
            ("ANTROPOMETRÍA", f"PESO: {peso} kg TALLA: {talla} cm PC: {pc} cm PB: {pb} cm"),
            ("EXAMEN FÍSICO", examen),
            ("PARACLÍNICOS", paraclinicos_texto),
            ("IMÁGENES", imagenes_texto),
            ("ANÁLISIS", analisis),
            ("DIAGNÓSTICOS", diagnosticos),
            ("OBSERVACIÓN DIAGNÓSTICA", observacion_dx),
            ("PLAN", plan),
        ]

        st.success("Historia clínica generada")
        fecha_guardado = datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        docx_bytes = generar_docx_informe(TITULO.upper(), secciones)
        nombre_base_docx = construir_nombre_base_docx(
            "CE",
            nombre=nombre,
            documento=documento,
            fecha_guardado=fecha_guardado,
        )
        ruta_docx_guardado = guardar_docx_exportado(
            docx_bytes,
            nombre_base_docx,
            subcarpeta=PREFIX,
        )
        nombre_docx = f"{nombre_base_docx}.docx"
        st.download_button(
            "Descargar informe en Word",
            data=docx_bytes,
            file_name=nombre_docx,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"{PREFIX}_download_docx",
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
        render_informe_html(TITULO.upper(), secciones, historia.upper())

    st.divider()
    with st.expander("Historias guardadas", expanded=False):
        historias_guardadas = _load_histories(history_path)
        if historias_guardadas:
            opciones = [h["id"] for h in historias_guardadas]
            historia_consulta_id = st.selectbox(
                "Consultar historia previa",
                opciones,
                key=f"{PREFIX}_historia_consulta_id",
            )
            historia_sel = next((h for h in historias_guardadas if h["id"] == historia_consulta_id), None)
            if historia_sel:
                st.text_area(
                    "Informe guardado",
                    historia_sel["historia"],
                    height=500,
                    key=f"{PREFIX}_historia_guardada_texto",
                )
                if st.button("Eliminar esta historia", key=f"{PREFIX}_eliminar_historia", use_container_width=True):
                    resultado_eliminacion = eliminar_historia_guardada(history_path, historia_consulta_id)
                    if resultado_eliminacion.get("ok"):
                        st.success("Historia eliminada correctamente.")
                        st.rerun()
                    else:
                        st.warning(resultado_eliminacion.get("message", "No se pudo eliminar la historia."))
        else:
            st.info("Aún no hay historias guardadas.")
