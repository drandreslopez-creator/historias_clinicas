import hashlib
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
    actualizar_texto_extraido,
    aplanar_grupos_busqueda,
    cargar_cie10,
    coincide_grupos,
    complementar_analisis_con_ia,
    complementar_plan_con_ia,
    construir_conducta_final_analisis,
    construir_observacion_diagnostica_base,
    construir_conducta_sugerida_analisis,
    construir_resumen_paraclinicos_para_analisis,
    construir_resumen_signos_para_analisis,
    construir_nombre_base_docx,
    construir_grupos_busqueda,
    eliminar_historia_guardada,
    expandir_terminos_busqueda,
    extraer_destinatario_informacion,
    extraer_resumen_antecedentes_para_analisis,
    extraer_resumen_examen_para_analisis,
    fusionar_analisis_editado_con_base_nueva,
    complementar_observacion_diagnostica_con_ia,
    generar_docx_informe,
    generar_analisis_asistido_urgencias,
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

SINTOMAS_GENERALES_HOMEOPATIA_PEDIATRICA_DEFAULT = """- APETITO:
- SED:
- DESEOS:
- AVERSIONES:
- AGRAVACIONES:
- EMPEORA:
- CALOR VITAL:
- TRANSPIRACIÓN:
- SUEÑO:
- SUEÑOS:
- SEXUALIDAD:
- ESTADO DEL TIEMPO:"""

REVISION_HOMEOPATIA_PEDIATRICA_DEFAULT = """-SÍNTOMAS CARDIOVASCULARES: NIEGA CANSANCIO, NO FATIGA AL COMER, NO CIANOSIS.
-DIGESTIVO: SIN NAUSEA NI EMESIS, DEPOSICIONES 3 VEZ CADA DÍA, BRISTOL 3.
-ALIMENTARIOS: ADECUADA PARA LA EDAD.
-URINARIO: HÁBITO NORMAL, 4 VECES AL DÍA, SIN SÍNTOMAS IRRITATIVOS URINARIO, NO COLURIA, SIN HEMATURIA.
-SÍNTOMAS RESPIRATORIOS ALTOS: ESTORNUDO 0/7, RINORREA: 0/7, CONGESTIÓN: 0/7, RONQUIDO EN LA NOCHE: 0/7, PRURITO NASAL 0/7, PRURITO OCULAR: 0/7.
-SÍNTOMAS RESPIRATORIOS BAJOS: TOS DIURNA 0/7, TOS NOCTURNA: 0/7, TOS CON EL FRIO: 0/7, TOS RISA: 0/7, TOS LLANTO: 0/7, TOS MIENTRAS COME: 0/7 TOS EJERCICIO: 0/7."""


def _float_or_none(valor):
    texto = str(valor or "").strip().replace(",", ".")
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def _normalizar_texto_simple(texto):
    return (
        str(texto or "")
        .upper()
        .replace("Á", "A")
        .replace("É", "E")
        .replace("Í", "I")
        .replace("Ó", "O")
        .replace("Ú", "U")
    )


def _revision_homeopatia_pediatrica_desde_enfermedad_actual(enfermedad_actual):
    texto = _normalizar_texto_simple(enfermedad_actual)
    def mencionado(*terminos):
        return any(termino in texto for termino in terminos)

    cardiovascular = ["NIEGA CANSANCIO", "NO FATIGA AL COMER", "NO CIANOSIS"]
    if mencionado("CIANOSIS"):
        cardiovascular = [item for item in cardiovascular if "CIANOSIS" not in item]

    digestivo = ["SIN NAUSEA NI EMESIS", "DEPOSICIONES 3 VEZ CADA DÍA", "BRISTOL 3"]
    if mencionado("NAUSEA", "NAUSEAS", "EMESIS", "VOMITO", "VOMITOS"):
        digestivo = [item for item in digestivo if item != "SIN NAUSEA NI EMESIS"]
    if mencionado("DIARREA", "DIARREICA", "DIARREICAS"):
        digestivo = [item for item in digestivo if item != "DEPOSICIONES 3 VEZ CADA DÍA"]
        digestivo = [item for item in digestivo if item != "BRISTOL 3"]

    urinario = [
        "HÁBITO NORMAL",
        "4 VECES AL DÍA",
        "SIN SÍNTOMAS IRRITATIVOS URINARIO",
        "NO COLURIA",
        "SIN HEMATURIA",
    ]
    if mencionado("COLURIA"):
        urinario = [item for item in urinario if "COLURIA" not in item]
    if mencionado("HEMATURIA"):
        urinario = [item for item in urinario if "HEMATURIA" not in item]

    respiratorios_altos = [
        "ESTORNUDO 0/7",
        "RINORREA: 0/7",
        "CONGESTIÓN: 0/7",
        "RONQUIDO EN LA NOCHE: 0/7",
        "PRURITO NASAL 0/7",
        "PRURITO OCULAR: 0/7",
    ]
    if mencionado("ESTORNUDO"):
        respiratorios_altos = [item for item in respiratorios_altos if "ESTORNUDO" not in item]
    if mencionado("RINORREA"):
        respiratorios_altos = [item for item in respiratorios_altos if "RINORREA" not in item]
    if mencionado("CONGESTION"):
        respiratorios_altos = [item for item in respiratorios_altos if "CONGESTIÓN" not in item]
    if mencionado("RONQUIDO"):
        respiratorios_altos = [item for item in respiratorios_altos if "RONQUIDO" not in item]
    if mencionado("PRURITO NASAL"):
        respiratorios_altos = [item for item in respiratorios_altos if "PRURITO NASAL" not in item]
    if mencionado("PRURITO OCULAR"):
        respiratorios_altos = [item for item in respiratorios_altos if "PRURITO OCULAR" not in item]

    respiratorios_bajos = [
        "TOS DIURNA 0/7",
        "TOS NOCTURNA: 0/7",
        "TOS CON EL FRIO: 0/7",
        "TOS RISA: 0/7",
        "TOS LLANTO: 0/7",
        "TOS MIENTRAS COME: 0/7",
        "TOS EJERCICIO: 0/7",
    ]
    if mencionado("TOS"):
        respiratorios_bajos = []

    lineas = []
    if cardiovascular:
        lineas.append(f"-SÍNTOMAS CARDIOVASCULARES: {', '.join(cardiovascular)}.")
    if digestivo:
        lineas.append(f"-DIGESTIVO: {', '.join(digestivo)}.")
    lineas.append("-ALIMENTARIOS: ADECUADA PARA LA EDAD.")
    if urinario:
        lineas.append(f"-URINARIO: {', '.join(urinario)}.")
    if respiratorios_altos:
        lineas.append(f"-SÍNTOMAS RESPIRATORIOS ALTOS: {', '.join(respiratorios_altos)}.")
    if respiratorios_bajos:
        lineas.append(f"-SÍNTOMAS RESPIRATORIOS BAJOS: {', '.join(respiratorios_bajos)}.")
    return "\n".join(lineas)


def _construir_enfermedad_actual_homeopatia_pediatrica(texto_libre, sexo, grupo, edad_resumen):
    encabezado = _construir_encabezado_enfermedad_actual(sexo, grupo, edad_resumen)
    texto_caso = str(texto_libre or "").strip()
    texto_norm = _normalizar_texto_simple(texto_caso)

    if not texto_caso:
        return encabezado, ""

    def mencionado(*terminos):
        return any(termino in texto_norm for termino in terminos)

    habitos = []
    if not mencionado("APETITO", "ALIMENTA", "COME", "INGESTA", "ALIMENTACION"):
        habitos.append("REFIERE BUEN APETITO")
    if not mencionado("DEPOSICION", "DIARREA", "ESTREÑ", "ESTREN", "BRISTOL"):
        habitos.append("DEPOSICIONES SON NORMALES")
    if not mencionado("ORINA", "DIURESIS", "URINAR", "HEMATURIA", "COLURIA", "URINARI"):
        habitos.append("ORINA ES NORMAL")
    if not mencionado("SUEÑO", "SUENO", "DUERME", "INSOMNIO", "DESPIERTA"):
        habitos.append("SUEÑO ES TRANQUILO")

    negaciones = []
    if not mencionado("FIEBRE", "FEBRIL", "HIPERTERMIA", "TEMPERATURA"):
        negaciones.append("FIEBRE")
    if not mencionado("DIFICULTAD RESPIRATORIA", "DISNEA", "TIRAJE", "TIRAJES", "RETRACCION", "RETRACCIONES", "ALETEO", "QUEJIDO"):
        negaciones.append("SIGNOS DE DIFICULTAD RESPIRATORIA")
    if not mencionado("CIANOSIS"):
        negaciones.append("CIANOSIS")

    bloques = []
    if habitos:
        bloques.append(", ".join(habitos) + ".")
    if negaciones:
        if len(negaciones) == 1:
            bloques.append(f"NIEGA {negaciones[0]} U OTROS SIGNOS.")
        else:
            bloques.append(f"NIEGA {', '.join(negaciones[:-1])}, {negaciones[-1]} U OTROS SIGNOS.")
    else:
        bloques.append("NIEGA OTROS SIGNOS.")
    if not mencionado("CONTAGIO", "CONTACTO", "INFECCION RESPIRATORIA EN EL HOGAR", "INFECCIONES RESPIRATORIAS EN EL HOGAR", "GRIPA EN EL HOGAR", "TOS EN EL HOGAR"):
        bloques.append("NIEGA NOCIÓN DE CONTAGIO PARA INFECCIONES RESPIRATORIAS EN EL HOGAR.")

    cola = " ".join(bloques).strip()
    return encabezado, cola


def _etapa_vida_consulta_externa(es_pediatrica, grupo, años):
    if es_pediatrica and grupo:
        return grupo.upper()
    if años is None:
        return ""
    if años >= 65:
        return "ADULTO MAYOR"
    if años >= 18:
        return "ADULTO"
    if años >= 10:
        return "ADOLESCENTE"
    return ""


def _construir_encabezado_enfermedad_actual(sexo, etapa, edad_resumen):
    sexo_txt = (sexo or "").upper()
    etapa_txt = (etapa or "").upper()
    edad_txt = (edad_resumen or "").upper()
    partes = ["PACIENTE"]
    if sexo_txt:
        partes.append(sexo_txt)
    if etapa_txt:
        partes.append(etapa_txt)
    if edad_txt:
        partes.extend(["DE", edad_txt])
    encabezado = " ".join(partes).strip()
    return f"{encabezado} QUIEN CONSULTA POR".strip()


def _construir_enfermedad_actual_prefijo(texto_libre, sexo, etapa, edad_resumen):
    encabezado = _construir_encabezado_enfermedad_actual(sexo, etapa, edad_resumen)
    return encabezado, ""


def _construir_enfermedad_actual_render(texto_libre, sexo, etapa, edad_resumen):
    texto = str(texto_libre or "").strip().upper()
    if not texto:
        return ""
    encabezado = _construir_encabezado_enfermedad_actual(sexo, etapa, edad_resumen)
    return f"{encabezado} {texto}".strip()


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
    revision_default=None,
    revision_before_antecedentes=False,
    revision_auto_depende_enfermedad=False,
    enfermedad_actual_auto_prefijo=True,
    enfermedad_actual_auto_homeopatia_pediatrica=False,
    mostrar_sintomas_generales=False,
    sintomas_generales_default="",
):
    if modo_pediatrico_urgencias_primera_vez and es_pediatrica:
        antecedentes_default = antecedentes_default or ANTECEDENTES_URGENCIAS_DEFAULT
    else:
        antecedentes_default = antecedentes_default or (ANTECEDENTES_DEFAULT if es_pediatrica else ANTECEDENTES_ADULTO_DEFAULT)
    plan_default = plan_default or PLAN_DEFAULT
    revision_default = revision_default or "NIEGA OTROS SINTOMAS/SIGNOS A LOS YA MENCIONADOS."
    sintomas_generales_default = sintomas_generales_default or ""
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
        f"{prefix}_revision": revision_default,
        f"{prefix}_revision_auto_base": revision_default,
        f"{prefix}_sintomas_generales": sintomas_generales_default,
        f"{prefix}_fc": "",
        f"{prefix}_fr": "",
        f"{prefix}_ta": "",
        f"{prefix}_sat": "",
        f"{prefix}_glucometria": "",
        f"{prefix}_temp": "",
        f"{prefix}_pb": "",
        f"{prefix}_peso": "",
        f"{prefix}_talla": "",
        f"{prefix}_pc": "",
        f"{prefix}_imc_adulto": "",
        f"{prefix}_neuro": "",
        f"{prefix}_examen": EXAMEN_DEFAULT,
        f"{prefix}_paraclinicos_texto": "",
        f"{prefix}_paraclinicos_auto": "",
        f"{prefix}_paraclinicos_pdf_sig": "",
        f"{prefix}_imagenes_texto": "",
        f"{prefix}_imagenes_auto": "",
        f"{prefix}_imagenes_pdf_sig": "",
        f"{prefix}_analisis": "",
        f"{prefix}_analisis_base": "",
        f"{prefix}_diagnosticos": "",
        f"{prefix}_obs_dx": "",
        f"{prefix}_plan": plan_default,
        f"{prefix}_plan_base": plan_default,
        f"{prefix}_conducta_final_analisis": "PENDIENTE DEFINIR",
        f"{prefix}_historia_consulta_id": None,
        f"{prefix}_modalidad_consulta": modalidad_consulta_forzada or "PRIMERA VEZ",
    }

    if st.session_state.pop(f"{prefix}_clear_requested", False):
        _clear_state(prefix, defaults)
        st.rerun()

    _init_state(defaults)

    st.header(titulo)

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
    edad_resumen_auto = f"{años} AÑOS" if años > 0 else (f"{meses} MESES" if fecha_nacimiento else "")
    etapa_vida_auto = _etapa_vida_consulta_externa(es_pediatrica, grupo, años if fecha_nacimiento else None)
    enfermedad_actual_label = "Detalles enfermedad actual" if usar_modo_urgencias else "Enfermedad actual"
    enfermedad_actual = st.text_area(enfermedad_actual_label, key=f"{prefix}_enfermedad_actual")
    enfermedad_actual_historia = enfermedad_actual
    if enfermedad_actual_auto_homeopatia_pediatrica:
        encabezado_final, cola_final = _construir_enfermedad_actual_homeopatia_pediatrica(
            enfermedad_actual,
            sexo,
            etapa_vida_auto,
            edad_resumen_auto,
        )
        enfermedad_actual_historia = f"{encabezado_final} {str(enfermedad_actual or '').strip()}".strip()
        if enfermedad_actual and cola_final:
            if not enfermedad_actual_historia.rstrip().endswith((".", ":", ";")):
                enfermedad_actual_historia += "."
            enfermedad_actual_historia += f" {cola_final}"
    elif enfermedad_actual_auto_prefijo:
        enfermedad_actual_historia = _construir_enfermedad_actual_render(
            enfermedad_actual,
            sexo,
            etapa_vida_auto,
            edad_resumen_auto,
        )

    if revision_auto_depende_enfermedad:
        revision_auto = _revision_homeopatia_pediatrica_desde_enfermedad_actual(enfermedad_actual)
        revision_actual = st.session_state.get(f"{prefix}_revision", "")
        revision_auto_base_previa = st.session_state.get(f"{prefix}_revision_auto_base", revision_default)
        if revision_actual in ("", revision_default, revision_auto_base_previa):
            st.session_state[f"{prefix}_revision"] = revision_auto
        st.session_state[f"{prefix}_revision_auto_base"] = revision_auto

    if revision_before_antecedentes:
        st.subheader("Revisión por sistemas")
        if usar_modo_urgencias and st.session_state.get(f"{prefix}_revision") == revision_default:
            st.session_state[f"{prefix}_revision"] = REVISION_URGENCIAS_DEFAULT
        revision = st.text_area("Revisión", key=f"{prefix}_revision")
        if mostrar_sintomas_generales:
            st.subheader("Síntomas generales")
            sintomas_generales = st.text_area(
                "Síntomas generales",
                key=f"{prefix}_sintomas_generales",
                height=220,
            )
        else:
            sintomas_generales = ""

    st.subheader("Antecedentes")
    antecedentes = st.text_area("Antecedentes", key=f"{prefix}_antecedentes", height=220)

    neuro = ""
    if mostrar_neurodesarrollo and fecha_nacimiento:
        neuro_default = obtener_neurodesarrollo(años, meses)
        if not st.session_state.get(f"{prefix}_neuro"):
            st.session_state[f"{prefix}_neuro"] = neuro_default
        st.subheader("Neurodesarrollo")
        neuro = st.text_area("Neurodesarrollo", key=f"{prefix}_neuro", height=160)

    if not revision_before_antecedentes:
        st.subheader("Revisión por sistemas")
        if usar_modo_urgencias and st.session_state.get(f"{prefix}_revision") == revision_default:
            st.session_state[f"{prefix}_revision"] = REVISION_URGENCIAS_DEFAULT
        revision = st.text_area("Revisión", key=f"{prefix}_revision")
        if mostrar_sintomas_generales:
            st.subheader("Síntomas generales")
            sintomas_generales = st.text_area(
                "Síntomas generales",
                key=f"{prefix}_sintomas_generales",
                height=220,
            )
        else:
            sintomas_generales = ""

    st.subheader("Signos vitales")
    col_sv_1, col_sv_2, col_sv_3 = st.columns(3)
    with col_sv_1:
        ta = st.text_input("TA (mmHg)", key=f"{prefix}_ta")
    with col_sv_2:
        fc = st.text_input("FC (lpm)", key=f"{prefix}_fc")
    with col_sv_3:
        sat = st.text_input("SpO2 (%)", key=f"{prefix}_sat")

    col_sv_4, col_sv_5, col_sv_6 = st.columns(3)
    with col_sv_4:
        fr = st.text_input("FR (rpm)", key=f"{prefix}_fr")
    with col_sv_5:
        glucometria = st.text_input("Glucometría (mg/dl)", key=f"{prefix}_glucometria")
    with col_sv_6:
        temp = st.text_input("Temperatura (°C)", key=f"{prefix}_temp")

    if es_pediatrica:
        col_sv_7, col_sv_8 = st.columns(2)
        with col_sv_7:
            peso = st.text_input("Peso (kg)", key=f"{prefix}_peso")
        with col_sv_8:
            talla = st.text_input("Talla (cm)", key=f"{prefix}_talla")
    else:
        col_sv_7, col_sv_8, col_sv_9 = st.columns(3)
        with col_sv_7:
            peso = st.text_input("Peso (kg)", key=f"{prefix}_peso")
        with col_sv_8:
            talla = st.text_input("Talla (cm)", key=f"{prefix}_talla")
        with col_sv_9:
            imc_adulto = st.text_input("IMC (kg/m²)", key=f"{prefix}_imc_adulto")

    if es_pediatrica:
        col_sv_10, col_sv_11 = st.columns(2)
        with col_sv_10:
            pc = st.text_input("Perímetro cefálico (cm)", key=f"{prefix}_pc")
        with col_sv_11:
            if mostrar_pb:
                pb = st.text_input("PB (cm)", key=f"{prefix}_pb")
            else:
                pb = ""
    else:
        pc = ""
        pb = ""
        imc_adulto = st.session_state.get(f"{prefix}_imc_adulto", "")

    fc_num = _float_or_none(fc)
    fr_num = _float_or_none(fr)
    sat_num = _float_or_none(sat)
    glucometria_num = _float_or_none(glucometria)
    temp_num = _float_or_none(temp)
    peso_num = _float_or_none(peso)
    talla_num = _float_or_none(talla)
    pc_num = _float_or_none(pc)
    pb_num = _float_or_none(pb)

    st.subheader("Examen físico")
    if usar_modo_urgencias and st.session_state.get(f"{prefix}_examen") == EXAMEN_DEFAULT:
        st.session_state[f"{prefix}_examen"] = EXAMEN_URGENCIAS_DEFAULT
    examen = st.text_area("Examen físico", key=f"{prefix}_examen", height=300 if usar_modo_urgencias else 260)

    st.subheader("Paraclínicos")
    col_pdf_1, col_pdf_2 = st.columns(2)
    with col_pdf_1:
        pdf_labs = st.file_uploader(
            "Subir PDF de laboratorios",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"{prefix}_paraclinicos_pdf_v1",
        )
    with col_pdf_2:
        pdf_imgs = st.file_uploader(
            "Subir PDF de imágenes",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"{prefix}_imagenes_pdf_v1",
        )

    if pdf_labs:
        actualizar_texto_extraido(
            f"{prefix}_paraclinicos_texto",
            f"{prefix}_paraclinicos_auto",
            f"{prefix}_paraclinicos_pdf_sig",
            pdf_labs,
            "laboratorios",
        )
    if pdf_imgs:
        actualizar_texto_extraido(
            f"{prefix}_imagenes_texto",
            f"{prefix}_imagenes_auto",
            f"{prefix}_imagenes_pdf_sig",
            pdf_imgs,
            "imagenes",
        )

    paraclinicos_texto = st.text_area("Laboratorios", key=f"{prefix}_paraclinicos_texto", height=160)
    imagenes_texto = st.text_area("Imágenes", key=f"{prefix}_imagenes_texto", height=120)
    conducta_final_analisis = st.selectbox(
        "Conducta final",
        ["PENDIENTE DEFINIR", "OBSERVACIÓN", "HOSPITALIZACIÓN", "EGRESO", "REMISIÓN"],
        key=f"{prefix}_conducta_final_analisis",
    )
    permitir_generacion_analisis = conducta_final_analisis != "PENDIENTE DEFINIR"

    sexo_txt = (sexo or "").upper()
    grupo_txt = f" {grupo.upper()}" if grupo else ""
    edad_resumen = f"{años} AÑOS" if años > 0 else (f"{meses} MESES" if fecha_nacimiento else "")

    enfermedad_auto = enfermedad_actual_historia or f"PACIENTE {sexo_txt}{grupo_txt} DE {edad_resumen}, QUIEN CONSULTA POR {str(enfermedad_actual).upper()}".strip()
    resumen_antecedentes_analisis = extraer_resumen_antecedentes_para_analisis(antecedentes)
    destinatario_informacion = extraer_destinatario_informacion(informante)
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
    analisis_default = ""
    if permitir_generacion_analisis:
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
            "titulo": titulo,
            "modalidad_consulta": modalidad_consulta or "",
            "motivo_consulta": motivo,
            "enfermedad_actual": enfermedad_actual,
            "antecedentes": antecedentes,
            "parentesco_acompanante": destinatario_informacion,
            "conducta_final_definida": conducta_final_analisis,
            "conducta_sugerida_local": conducta_sugerida_analisis,
            "conducta_final_texto": conducta_final_texto,
            "revision_por_sistemas": revision,
            "sintomas_generales": sintomas_generales,
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
                "imc": imc_adulto if not es_pediatrica else "",
            },
            "examen_fisico": examen,
            "paraclinicos": paraclinicos_texto,
            "imagenes": imagenes_texto,
            "diagnosticos": st.session_state.get(f"{prefix}_diagnosticos", ""),
        }
        fingerprint_analisis_ia = hashlib.md5(
            json.dumps(contexto_analisis_ia, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        analisis_default = complementar_analisis_con_ia(
            analisis_default,
            contexto_analisis_ia,
            fingerprint_analisis_ia,
            instrucciones=(
                "Eres un asistente clínico que redacta análisis médicos en español. "
                "Usa únicamente la información entregada. No inventes diagnósticos, tratamientos, signos ni laboratorios. "
                "Redacta un solo párrafo claro, coherente y profesional, en MAYÚSCULAS. "
                "Debes tomar como fuente principal todo el contexto clínico ya consignado antes del análisis. "
                "Integra antecedentes relevantes cuando aporten al caso clínico. "
                "Si existe una conducta final definida en el contexto, úsala como marco principal del cierre y constrúyela de forma coherente con la historia, "
                "el examen físico, los signos vitales y los paraclínicos, sin contradecirla ni duplicar frases genéricas. "
                "Si la conducta final está PENDIENTE DEFINIR, no inventes una decisión final. "
                "En el cierre, usa el parentesco del acompañante si está disponible; si no, usa FAMILIAR."
            ),
        )

    st.subheader("Análisis")
    if permitir_generacion_analisis and st.session_state.get(f"{prefix}_analisis_base") != analisis_default:
        if st.session_state.get(f"{prefix}_analisis") == st.session_state.get(f"{prefix}_analisis_base", ""):
            st.session_state[f"{prefix}_analisis"] = analisis_default
        else:
            merge_fp = hashlib.md5(
                json.dumps(
                    {
                        "actual": st.session_state.get(f"{prefix}_analisis", ""),
                        "base_anterior": st.session_state.get(f"{prefix}_analisis_base", ""),
                        "base_nueva": analisis_default,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            st.session_state[f"{prefix}_analisis"] = fusionar_analisis_editado_con_base_nueva(
                st.session_state.get(f"{prefix}_analisis", ""),
                st.session_state.get(f"{prefix}_analisis_base", ""),
                analisis_default,
                merge_fp,
            )
        st.session_state[f"{prefix}_analisis_base"] = analisis_default

    analisis = st.text_area("Análisis clínico", key=f"{prefix}_analisis", height=180)

    st.subheader("Diagnósticos")
    if usar_modo_urgencias:
        diagnosticos = _construir_diagnostico_cie10(prefix)
    else:
        diagnosticos = st.text_area("Diagnósticos", key=f"{prefix}_diagnosticos", height=120)
    obs_dx_default = construir_observacion_diagnostica_base(
        diagnosticos,
        analisis_default,
        antecedentes,
        "",
    )
    contexto_obs_dx_ia = {
        "diagnostico_cie10_principal": diagnosticos,
        "analisis": analisis_default,
        "antecedentes": antecedentes,
        "enfermedad_actual": enfermedad_actual,
        "paraclinicos": paraclinicos_texto,
        "diagnostico_nutricional": "",
        "titulo": titulo,
    }
    fingerprint_obs_dx_ia = hashlib.md5(
        json.dumps(contexto_obs_dx_ia, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    obs_dx_default = complementar_observacion_diagnostica_con_ia(
        obs_dx_default,
        contexto_obs_dx_ia,
        fingerprint_obs_dx_ia,
    )
    if st.session_state.get(f"{prefix}_obs_dx_base") != obs_dx_default:
        if st.session_state.get(f"{prefix}_obs_dx", "") == st.session_state.get(f"{prefix}_obs_dx_base", ""):
            st.session_state[f"{prefix}_obs_dx"] = obs_dx_default
        elif f"{prefix}_obs_dx_base" not in st.session_state:
            st.session_state[f"{prefix}_obs_dx"] = obs_dx_default
        st.session_state[f"{prefix}_obs_dx_base"] = obs_dx_default
    observacion_dx = st.text_area("Observación diagnóstica", key=f"{prefix}_obs_dx", height=100)

    st.subheader("Plan")
    if usar_modo_urgencias and st.session_state.get(f"{prefix}_plan") == plan_default:
        st.session_state[f"{prefix}_plan"] = PLAN_URGENCIAS_DEFAULT
    plan_base_local = st.session_state.get(f"{prefix}_plan_base", plan_default) or plan_default
    contexto_plan_ia = {
        "titulo": titulo,
        "modalidad_consulta": modalidad_consulta or "",
        "diagnostico_cie10_principal": diagnosticos,
        "observacion_diagnostica": observacion_dx,
        "conducta_final_definida": conducta_final_analisis,
        "conducta_final_texto": conducta_final_texto,
        "analisis": analisis_default,
        "enfermedad_actual": enfermedad_actual,
        "antecedentes": antecedentes,
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
            "imc": imc_adulto if not es_pediatrica else "",
        },
        "examen_fisico": examen,
        "paraclinicos": paraclinicos_texto,
        "imagenes": imagenes_texto,
    }
    fingerprint_plan_ia = hashlib.md5(
        json.dumps(contexto_plan_ia, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    plan_sugerido = complementar_plan_con_ia(
        plan_base_local,
        contexto_plan_ia,
        fingerprint_plan_ia,
    )
    if st.session_state.get(f"{prefix}_plan_base") != plan_sugerido:
        if st.session_state.get(f"{prefix}_plan", "") == st.session_state.get(f"{prefix}_plan_base", ""):
            st.session_state[f"{prefix}_plan"] = plan_sugerido
        elif f"{prefix}_plan_base" not in st.session_state:
            st.session_state[f"{prefix}_plan"] = plan_sugerido
        st.session_state[f"{prefix}_plan_base"] = plan_sugerido
    plan = st.text_area("Plan", key=f"{prefix}_plan", height=220)

    col_btn_1, col_btn_2 = st.columns(2)
    generar = col_btn_1.button("Generar Historia Clínica", key=f"{prefix}_generar", use_container_width=True)
    if col_btn_2.button("Limpiar y empezar otra historia", key=f"{prefix}_limpiar", use_container_width=True):
        st.session_state[f"{prefix}_clear_requested"] = True
        st.rerun()

    if generar:
        fecha_str = fecha_nacimiento.strftime("%d/%m/%Y") if fecha_nacimiento else ""
        bloque_revision = f"""
REVISIÓN POR SISTEMAS:
{revision}
"""
        bloque_sintomas_generales = ""
        if mostrar_sintomas_generales:
            bloque_sintomas_generales = f"""
SÍNTOMAS GENERALES:
{sintomas_generales}
"""
        bloque_antecedentes = f"""
ANTECEDENTES:
{antecedentes}
"""
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
{enfermedad_actual_historia}
"""
        if revision_before_antecedentes:
            historia += bloque_revision
            if bloque_sintomas_generales:
                historia += bloque_sintomas_generales
            historia += bloque_antecedentes
        else:
            historia += bloque_antecedentes + bloque_revision
            if bloque_sintomas_generales:
                historia += bloque_sintomas_generales
        if mostrar_neurodesarrollo:
            historia += f"""

NEURODESARROLLO:
{neuro}
"""
        historia += f"""

SIGNOS VITALES:
TA {ta} mmHg FC: {fc} lpm SpO2: {sat}% FR: {fr} rpm GLUCOMETRÍA: {glucometria} mg/dl T: {temp} °C{f" PB: {pb} cm" if mostrar_pb else ""}

ANTROPOMETRÍA:
PESO: {peso} kg TALLA: {talla} cm"""

        if es_pediatrica:
            historia += f" PC: {pc} cm"
        elif imc_adulto:
            historia += f" IMC: {imc_adulto} kg/m²"

        historia += f"""

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
"""

        secciones = [
            ("MODALIDAD DE LA CONSULTA", modalidad_consulta or ""),
            ("DATOS DE IDENTIFICACIÓN", f"NOMBRES Y APELLIDOS: {nombre}\nTIPO DE DOCUMENTO: {tipo_documento}\nDOCUMENTO: {documento}\nFECHA DE NACIMIENTO: {fecha_str}\nEPS: {eps}\nTELEFONO: {telefono}\nINFORMANTE / ACOMPAÑANTE: {informante}"),
            ("MOTIVO DE CONSULTA", motivo),
            ("ENFERMEDAD ACTUAL", enfermedad_actual_historia),
        ]
        if revision_before_antecedentes:
            secciones.extend(
                [
                    ("REVISIÓN POR SISTEMAS", revision),
                    *((("SÍNTOMAS GENERALES", sintomas_generales),) if mostrar_sintomas_generales else ()),
                    ("ANTECEDENTES", antecedentes),
                ]
            )
        else:
            secciones.extend(
                [
                    ("ANTECEDENTES", antecedentes),
                    ("REVISIÓN POR SISTEMAS", revision),
                    *((("SÍNTOMAS GENERALES", sintomas_generales),) if mostrar_sintomas_generales else ()),
                ]
            )
        if mostrar_neurodesarrollo:
            secciones.append(("NEURODESARROLLO", neuro))
        secciones.extend(
            [
                ("SIGNOS VITALES", f"TA {ta} mmHg FC: {fc} lpm SpO2: {sat}% FR: {fr} rpm GLUCOMETRÍA: {glucometria} mg/dl T: {temp} °C" + (f" PB: {pb} cm" if mostrar_pb else "")),
                ("ANTROPOMETRÍA", f"PESO: {peso} kg TALLA: {talla} cm" + (f" PC: {pc} cm" if es_pediatrica else (f" IMC: {imc_adulto} kg/m²" if imc_adulto else ""))),
                ("EXAMEN FÍSICO", examen),
                ("PARACLÍNICOS", paraclinicos_texto),
                ("IMÁGENES", imagenes_texto),
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
