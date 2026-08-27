"""Rutas de trazabilidad clínica para pediatría.

Este módulo apoya la documentación de conductas. No sustituye el juicio del
pediatra ni los protocolos institucionales vigentes.
"""

from __future__ import annotations

import re
import unicodedata


def _normalizar(texto: object) -> str:
    texto = unicodedata.normalize("NFD", str(texto or ""))
    texto = "".join(char for char in texto if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", texto).strip().upper()


RUTAS_GPC = {
    "BRONQUIOLITIS": {
        "codigos": ("J21",),
        "terminos": ("BRONQUIOLITIS",),
        "nombre": "BRONQUIOLITIS EN MENORES DE 2 AÑOS",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Bronquiolitis",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-6/bronquiolitis/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "CLASIFICACIÓN DE SEVERIDAD Y FACTORES DE RIESGO",
            "TRABAJO RESPIRATORIO, FRECUENCIA RESPIRATORIA Y SATURACIÓN",
            "TOLERANCIA A LA VÍA ORAL, HIDRATACIÓN Y PLAN DE ALIMENTACIÓN",
            "CRITERIOS DE OBSERVACIÓN, HOSPITALIZACIÓN O EGRESO",
            "SIGNOS DE ALARMA Y RECONSULTA",
        ),
        "alertas": (
            "EL DIAGNÓSTICO ES PRINCIPALMENTE CLÍNICO; DOCUMENTE LA JUSTIFICACIÓN SI SOLICITA PARACLÍNICOS O IMÁGENES FUERA DE LA VALORACIÓN RUTINARIA.",
            "DOCUMENTE EL CRITERIO CLÍNICO SI INDICA ANTIBIÓTICO O BRONCODILATADOR.",
        ),
        "verificaciones": {
            "SEVERIDAD RESPIRATORIA": ("SEVERIDAD", "TIRAJE", "TRABAJO RESPIRATORIO", "FRECUENCIA RESPIRATORIA", "FR"),
            "OXIMETRÍA DOCUMENTADA": ("SATUR", "SPO2", "OXIMETR"),
            "HIDRATACIÓN / TOLERANCIA ORAL": ("HIDRAT", "VIA ORAL", "VÍA ORAL", "INGESTA", "LACTANC"),
            "SIGNOS DE ALARMA / RECONSULTA": ("SIGNOS DE ALARMA", "RECONSULT", "URGENCIAS"),
        },
    },
    "NEUMONIA": {
        "codigos": ("J18", "J15", "J12", "J13", "J14"),
        "terminos": ("NEUMONIA", "NEUMONÍA"),
        "nombre": "NEUMONÍA PEDIÁTRICA",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Neumonía",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-6/neumonia/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "TAQUIPNEA, TIRAJE, SATURACIÓN Y SIGNOS DE GRAVEDAD",
            "CLASIFICACIÓN DE SEVERIDAD Y DECISIÓN DE SITIO DE MANEJO",
            "ANTIBIÓTICO, VÍA, DOSIS, INTERVALO Y DURACIÓN CUANDO ESTÉ INDICADO",
            "OXÍGENO Y METAS CLÍNICAS CUANDO ESTÉ INDICADO",
            "SIGNOS DE ALARMA, CONTROL Y RECONSULTA",
        ),
        "alertas": (
            "DOCUMENTE LA JUSTIFICACIÓN CLÍNICA DE PARACLÍNICOS, IMÁGENES, ANTIBIÓTICOS Y SITIO DE MANEJO.",
        ),
        "verificaciones": {
            "SEVERIDAD RESPIRATORIA": ("TAQUIP", "TIRAJE", "SEVERIDAD", "TRABAJO RESPIRATORIO", "FRECUENCIA RESPIRATORIA"),
            "OXIMETRÍA DOCUMENTADA": ("SATUR", "SPO2", "OXIMETR"),
            "DECISIÓN DE SITIO DE MANEJO": ("OBSERV", "HOSPITAL", "EGRESO", "REMISI"),
            "SIGNOS DE ALARMA / CONTROL": ("SIGNOS DE ALARMA", "RECONSULT", "CONTROL", "SEGUIMIENTO"),
        },
    },
    "ASMA": {
        "codigos": ("J45",),
        "terminos": ("ASMA", "SIBILANCIAS", "BRONCOESPASMO", "EXACERBACION ASM"),
        "nombre": "ASMA Y EXACERBACIÓN BRONCOOBSTRUCTIVA",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Asma",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-6/asma/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "SEVERIDAD, TRABAJO RESPIRATORIO, SATURACIÓN Y RESPUESTA AL TRATAMIENTO",
            "TRATAMIENTO INDICADO, VÍA, DOSIS, FRECUENCIA Y RESPUESTA CLÍNICA",
            "CRITERIOS DE OBSERVACIÓN, HOSPITALIZACIÓN, REMISIÓN O EGRESO",
            "PLAN DE CONTROL, TÉCNICA INHALATORIA Y SIGNOS DE ALARMA",
        ),
        "alertas": (
            "REGISTRE LA RESPUESTA OBJETIVA AL BRONCODILATADOR Y LA EDUCACIÓN SOBRE TÉCNICA INHALATORIA CUANDO APLIQUE.",
        ),
        "verificaciones": {
            "SEVERIDAD / RESPUESTA": ("SEVERIDAD", "WDF", "WOOD", "RESPUESTA", "TIRAJE", "SIBILAN"),
            "OXIMETRÍA DOCUMENTADA": ("SATUR", "SPO2", "OXIMETR"),
            "TÉCNICA O PLAN INHALATORIO": ("INHAL", "ESPACIADOR", "SALBUTAMOL"),
            "SIGNOS DE ALARMA / CONTROL": ("SIGNOS DE ALARMA", "RECONSULT", "CONTROL", "SEGUIMIENTO"),
        },
    },
    "CRUP": {
        "codigos": ("J05", "J04"),
        "terminos": ("CRUP", "LARINGITIS", "LARINGOTRAQUEITIS", "ESTRIDOR"),
        "nombre": "LARINGOTRAQUEITIS / CRUP",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Laringotraqueitis/Crup",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-6/laringotraqueitis-crup/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "ESTRIDOR, TIRAJE, SATURACIÓN Y CLASIFICACIÓN DE SEVERIDAD",
            "RESPUESTA CLÍNICA A LAS INTERVENCIONES",
            "PERÍODO DE OBSERVACIÓN CUANDO ESTÉ INDICADO",
            "SIGNOS DE ALARMA Y RECONSULTA",
        ),
        "alertas": (
            "DOCUMENTE LA SEVERIDAD Y LA REVALORACIÓN POSTERIOR A LAS INTERVENCIONES RESPIRATORIAS.",
        ),
        "verificaciones": {
            "SEVERIDAD RESPIRATORIA": ("ESTRIDOR", "TIRAJE", "SEVERIDAD", "TRABAJO RESPIRATORIO"),
            "OXIMETRÍA DOCUMENTADA": ("SATUR", "SPO2", "OXIMETR"),
            "REVALORACIÓN": ("REVALOR", "EVOLUCI", "RESPUESTA"),
            "SIGNOS DE ALARMA / RECONSULTA": ("SIGNOS DE ALARMA", "RECONSULT", "URGENCIAS"),
        },
    },
    "EDA": {
        "codigos": ("A09",),
        "terminos": ("GASTROENTERITIS", "ENFERMEDAD DIARREICA", "DIARREA", "DESHIDRAT"),
        "nombre": "ENFERMEDAD DIARREICA AGUDA / DESHIDRATACIÓN",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Enfermedad diarreica aguda",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-7/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "CLASIFICACIÓN DE HIDRATACIÓN Y SIGNOS DE PELIGRO",
            "TOLERANCIA A VÍA ORAL, PLAN DE HIDRATACIÓN Y DIURESIS",
            "JUSTIFICACIÓN DE FLUIDOTERAPIA, PARACLÍNICOS O HOSPITALIZACIÓN CUANDO APLIQUE",
            "SIGNOS DE ALARMA, CONTINUIDAD DE LA ALIMENTACIÓN Y RECONSULTA",
        ),
        "alertas": (
            "DOCUMENTE EL ESTADO DE HIDRATACIÓN Y LA TOLERANCIA ORAL ANTES DE DEFINIR EL SITIO DE MANEJO.",
        ),
        "verificaciones": {
            "ESTADO DE HIDRATACIÓN": ("DESHIDRAT", "HIDRAT", "PLIEGUE", "LLANTO", "MUCOSA"),
            "TOLERANCIA ORAL / DIURESIS": ("VIA ORAL", "VÍA ORAL", "SRO", "DIURES", "GASTO URINARIO"),
            "DECISIÓN DE SITIO DE MANEJO": ("OBSERV", "HOSPITAL", "EGRESO", "REMISI"),
            "SIGNOS DE ALARMA / RECONSULTA": ("SIGNOS DE ALARMA", "RECONSULT", "URGENCIAS"),
        },
    },
}


def detectar_ruta_gpc(diagnostico: object, texto_clinico: object = "") -> str:
    # La ruta se activa por el diagnóstico registrado, no por síntomas aislados
    # que pueden estar negados dentro de la revisión por sistemas.
    texto = _normalizar(diagnostico)
    codigo = _normalizar(diagnostico).split(" ", 1)[0]
    for clave, ruta in RUTAS_GPC.items():
        if any(codigo.startswith(prefijo) for prefijo in ruta["codigos"]):
            return clave
        if any(termino in texto for termino in ruta["terminos"]):
            return clave
    return ""


def obtener_ruta_gpc(clave: str) -> dict:
    return RUTAS_GPC.get(clave, {})


def resumen_gpc_para_ia(clave: str) -> str:
    ruta = obtener_ruta_gpc(clave)
    if not ruta:
        return "NO HAY RUTA GPC ESPECÍFICA DETECTADA; NO INVENTES RECOMENDACIONES."
    items = "; ".join(ruta["documentacion"])
    alertas = " ".join(ruta["alertas"])
    return f"RUTA GPC: {ruta['nombre']}. DEBE DOCUMENTAR: {items}. {alertas}"


def construir_trazabilidad_gpc(
    clave: str,
    texto_clinico: object,
    justificacion: object = "",
    registro_complementario: object = "",
) -> str:
    ruta = obtener_ruta_gpc(clave)
    if not ruta:
        return "NO SE DETECTÓ RUTA GPC ESPECÍFICA PARA EL DIAGNÓSTICO REGISTRADO."

    texto = _normalizar(f"{texto_clinico or ''}\n{registro_complementario or ''}")
    lineas = [
        f"RUTA APLICADA: {ruta['nombre']}",
        f"FUENTE: {ruta['fuente']}",
        f"REFERENCIA: {ruta['url']}",
        f"VERSIÓN/REVISIÓN: {ruta['version']}",
        "ELEMENTOS DE TRAZABILIDAD:",
    ]
    for etiqueta, terminos in ruta["verificaciones"].items():
        estado = "DOCUMENTADO" if any(_normalizar(termino) in texto for termino in terminos) else "PENDIENTE DE VERIFICAR"
        lineas.append(f"- {etiqueta}: {estado}")
    if str(registro_complementario or "").strip():
        lineas.append("REGISTRO CLÍNICO COMPLEMENTARIO GPC:")
        lineas.append(str(registro_complementario).strip())
    if str(justificacion or "").strip():
        lineas.append("JUSTIFICACIÓN CLÍNICA DE APARTAMIENTO O INDIVIDUALIZACIÓN:")
        lineas.append(str(justificacion).strip())
    return "\n".join(lineas)


def render_trazabilidad_gpc(
    st,
    *,
    clave: str,
    texto_clinico: object,
    justificacion_key: str,
    registro_key: str,
    selector_key: str,
) -> tuple[str, str, str, str]:
    opciones = [""] + list(RUTAS_GPC)
    clave_actual = st.session_state.get(selector_key, clave)
    if clave_actual not in opciones:
        clave_actual = clave
    ruta_seleccionada = st.selectbox(
        "Ruta GPC aplicable",
        opciones,
        index=opciones.index(clave_actual),
        key=selector_key,
        format_func=lambda opcion: (
            "SIN RUTA GPC ESPECÍFICA" if not opcion else RUTAS_GPC[opcion]["nombre"]
        ),
        help="Confirma la ruta según el diagnóstico clínico. La sugerencia automática se basa únicamente en el diagnóstico registrado.",
    )
    ruta = obtener_ruta_gpc(ruta_seleccionada)
    st.subheader("Apoyo GPC")
    if not ruta:
        st.caption("Seleccione una ruta cuando exista una guía aplicable. El análisis no incluirá referencias GPC automáticamente.")
        return "", "", "", ""

    st.caption(f"Ruta detectada: {ruta['nombre']}")
    st.caption(f"Fuente: {ruta['fuente']}")
    st.link_button("Consultar fuente de la ruta", ruta["url"], use_container_width=False)
    st.caption("Para esta ruta, deje documentado según corresponda:")
    for item in ruta["documentacion"]:
        st.caption(f"- {item}")
    for alerta in ruta["alertas"]:
        st.info(alerta)

    registro_previo = str(st.session_state.get(registro_key, "") or "")
    texto = _normalizar(f"{texto_clinico or ''}\n{registro_previo}")
    for etiqueta, terminos in ruta["verificaciones"].items():
        estado = "DOCUMENTADO" if any(_normalizar(termino) in texto for termino in terminos) else "PENDIENTE DE VERIFICAR"
        st.caption(f"{etiqueta}: {estado}")

    registro_complementario = st.text_area(
        "Registro clínico complementario GPC",
        key=registro_key,
        height=110,
        placeholder=(
            "Documente aquí los elementos pendientes: severidad, revaloración, "
            "tolerancia oral, diuresis, educación de signos de alarma u otros hallazgos relevantes."
        ),
        help="Este registro se integra al análisis, al plan y al informe final.",
    )
    justificacion = st.text_area(
        "Justificación clínica si se individualiza o se aparta de la ruta",
        key=justificacion_key,
        height=90,
        help="Registre el motivo clínico, contraindicación, comorbilidad o decisión individual que modifique la conducta sugerida.",
    )
    return (
        ruta_seleccionada,
        construir_trazabilidad_gpc(
            ruta_seleccionada,
            f"{texto_clinico or ''}\n{registro_complementario or ''}",
            justificacion,
            registro_complementario,
        ),
        resumen_gpc_para_ia(ruta_seleccionada),
        registro_complementario,
    )
