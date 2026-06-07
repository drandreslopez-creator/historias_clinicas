import streamlit as st


SILVERMAN_ITEMS = {
    "disociacion_toracoabdominal": {
        "label": "Disociación toracoabdominal",
        "options": [
            ("SINCRÓNICO", 0),
            ("RETRASO TORÁCICO LEVE", 1),
            ("BALANCEO / DISOCIACIÓN MARCADA", 2),
        ],
    },
    "tiraje_intercostal": {
        "label": "Tiraje intercostal",
        "options": [
            ("AUSENTE", 0),
            ("LEVE", 1),
            ("MARCADO", 2),
        ],
    },
    "retraccion_xifoidea": {
        "label": "Retracción xifoidea",
        "options": [
            ("AUSENTE", 0),
            ("LEVE", 1),
            ("MARCADA", 2),
        ],
    },
    "aleteo_nasal": {
        "label": "Aleteo nasal",
        "options": [
            ("AUSENTE", 0),
            ("LEVE", 1),
            ("MARCADO", 2),
        ],
    },
    "quejido_espiratorio": {
        "label": "Quejido espiratorio",
        "options": [
            ("AUSENTE", 0),
            ("AUDIBLE CON ESTETOSCOPIO", 1),
            ("AUDIBLE A DISTANCIA", 2),
        ],
    },
}

GLASGOW_OCULAR = [
    ("ESPONTÁNEA", 4),
    ("AL HABLA", 3),
    ("AL DOLOR", 2),
    ("NINGUNA", 1),
]

GLASGOW_VERBAL_NINO = [
    ("ORIENTADO / CONVERSA", 5),
    ("CONFUSO", 4),
    ("PALABRAS INAPROPIADAS", 3),
    ("SONIDOS INCOMPRENSIBLES", 2),
    ("NINGUNA", 1),
]

GLASGOW_VERBAL_LACTANTE = [
    ("SONRÍE, FIJA Y SIGUE / INTERACTÚA", 5),
    ("LLORA PERO CONSOLABLE", 4),
    ("LLANTO PERSISTENTE O GRITOS", 3),
    ("QUEJIDOS / AGITACIÓN AL DOLOR", 2),
    ("NINGUNA", 1),
]

GLASGOW_MOTORA = [
    ("OBEDECE / MOVIMIENTOS ESPONTÁNEOS NORMALES", 6),
    ("LOCALIZA EL DOLOR", 5),
    ("RETIRA AL DOLOR", 4),
    ("FLEXIÓN ANORMAL", 3),
    ("EXTENSIÓN ANORMAL", 2),
    ("NINGUNA", 1),
]

PTS_ITEMS = {
    "peso": {
        "label": "Peso",
        "options": [
            ("> 20 KG", 2),
            ("10-20 KG", 1),
            ("< 10 KG", -1),
        ],
    },
    "via_aerea": {
        "label": "Vía aérea",
        "options": [
            ("NORMAL", 2),
            ("MANTENIBLE", 1),
            ("NO MANTENIBLE / REQUIERE VÍA AÉREA AVANZADA", -1),
        ],
    },
    "pas": {
        "label": "Presión arterial sistólica",
        "options": [
            ("> 90 MMHG", 2),
            ("50-90 MMHG", 1),
            ("< 50 MMHG", -1),
        ],
    },
    "snc": {
        "label": "Sistema nervioso central",
        "options": [
            ("DESPIERTO", 2),
            ("OBNUBILADO / PÉRDIDA BREVE DE CONCIENCIA", 1),
            ("COMA / POSTURA ANORMAL", -1),
        ],
    },
    "heridas": {
        "label": "Heridas",
        "options": [
            ("NINGUNA", 2),
            ("MENOR", 1),
            ("MAYOR / PENETRANTE", -1),
        ],
    },
    "esqueletico": {
        "label": "Sistema esquelético",
        "options": [
            ("SIN FRACTURAS", 2),
            ("FRACTURA CERRADA", 1),
            ("FRACTURA ABIERTA / MÚLTIPLE", -1),
        ],
    },
}

WESTLEY_ITEMS = {
    "estridor": {
        "label": "Estridor",
        "options": [("AUSENTE", 0), ("CON AGITACIÓN", 1), ("EN REPOSO", 2)],
    },
    "retracciones": {
        "label": "Retracciones",
        "options": [("AUSENTES", 0), ("LEVES", 1), ("MODERADAS/SEVERAS", 2)],
    },
    "entrada_aire": {
        "label": "Entrada de aire",
        "options": [("NORMAL", 0), ("DISMINUIDA", 1), ("MARCADAMENTE DISMINUIDA", 2)],
    },
    "cianosis": {
        "label": "Cianosis",
        "options": [("AUSENTE", 0), ("CON AGITACIÓN", 4), ("EN REPOSO", 5)],
    },
    "conciencia": {
        "label": "Nivel de conciencia",
        "options": [("NORMAL", 0), ("ALTERADO", 5)],
    },
}

WOOD_DOWNES_ITEMS = {
    "sibilancias": {
        "label": "Sibilancias",
        "options": [("NO", 0), ("FIN ESPIRATORIO", 1), ("INSPIRATORIAS Y ESPIRATORIAS / AUDIBLES", 2)],
    },
    "tirajes": {
        "label": "Tirajes",
        "options": [("NO", 0), ("LEVE", 1), ("INTENSO", 2)],
    },
    "frecuencia_respiratoria": {
        "label": "Frecuencia respiratoria",
        "options": [("NORMAL", 0), ("TAQUIPNEA MODERADA", 1), ("TAQUIPNEA MARCADA", 2)],
    },
    "ventilacion": {
        "label": "Ventilación / entrada de aire",
        "options": [("NORMAL", 0), ("DISMINUIDA", 1), ("MUY DISMINUIDA", 2)],
    },
    "cianosis": {
        "label": "Cianosis",
        "options": [("NO", 0), ("CON AGITACIÓN", 1), ("EN REPOSO", 2)],
    },
}

TAL_ITEMS = {
    "frecuencia_respiratoria": {
        "label": "Frecuencia respiratoria",
        "options": [("NORMAL", 0), ("AUMENTADA", 1), ("MUY AUMENTADA", 2), ("SEVERAMENTE AUMENTADA / APNEAS", 3)],
    },
    "sibilancias": {
        "label": "Sibilancias",
        "options": [("NO", 0), ("ESPIRATORIAS", 1), ("INSPIRATORIAS Y ESPIRATORIAS", 2), ("AUDIBLES SIN ESTETOSCOPIO / MÍNIMA VENTILACIÓN", 3)],
    },
    "cianosis": {
        "label": "Cianosis",
        "options": [("NO", 0), ("PERIORAL / CON AGITACIÓN", 1), ("EN REPOSO", 2), ("GENERALIZADA", 3)],
    },
    "retracciones": {
        "label": "Retracciones",
        "options": [("NO", 0), ("LEVE", 1), ("MODERADA", 2), ("SEVERA", 3)],
    },
}

DESHIDRATACION_ITEMS = {
    "apariencia_general": {
        "label": "Apariencia general",
        "options": [("NORMAL", 0), ("SEDE / IRRITABLE", 1), ("LETÁRGICO / HIPOTÓNICO", 2)],
    },
    "ojos": {
        "label": "Ojos",
        "options": [("NORMALES", 0), ("LIGERAMENTE HUNDIDOS", 1), ("MUY HUNDIDOS", 2)],
    },
    "mucosas": {
        "label": "Mucosas",
        "options": [("HÚMEDAS", 0), ("PEGUJOSAS", 1), ("SECAS", 2)],
    },
    "lagrimas": {
        "label": "Lágrimas",
        "options": [("PRESENTES", 0), ("DISMINUIDAS", 1), ("AUSENTES", 2)],
    },
}

TEP_OPTIONS = [("NORMAL", 0), ("ANORMAL", 1)]

PEWS_BEHAVIOR = [
    ("JUEGA / APROPIADO", 0),
    ("IRRITABLE PERO CONSOLABLE", 1),
    ("IRRITABLE NO CONSOLABLE O LETÁRGICO", 2),
    ("REDUCE RESPUESTA AL DOLOR / CONFUSO", 3),
]

PEWS_CARDIO = [
    ("ROSADO, RELLENO CAPILAR 1-2 S", 0),
    ("PÁLIDO O RELLENO CAPILAR 3 S", 1),
    ("TAQUICARDIA 20 SOBRE LO NORMAL O RELLENO 4 S", 2),
    ("GRIS / MOTEADO O BRADICARDIA O RELLENO >=5 S", 3),
]

PEWS_RESP = [
    ("NORMAL SIN TIRAJES", 0),
    (">10 SOBRE LO NORMAL O USO LEVE DE ACCESORIOS", 1),
    (">20 SOBRE LO NORMAL O TIRAJES / O2 MODERADO", 2),
    ("APNEA / RETRACCIONES MARCADAS / ALTO REQUERIMIENTO DE O2", 3),
]


def _radio_score(label, options, key):
    seleccion = st.radio(
        label,
        [texto for texto, _ in options],
        key=key,
        horizontal=False,
    )
    return next(valor for texto, valor in options if texto == seleccion)


def _interpretar_silverman(total):
    if total <= 0:
        return "SIN DIFICULTAD RESPIRATORIA"
    if total <= 3:
        return "DIFICULTAD RESPIRATORIA LEVE"
    if total <= 6:
        return "DIFICULTAD RESPIRATORIA MODERADA"
    return "DIFICULTAD RESPIRATORIA SEVERA"


def _interpretar_glasgow(total):
    if total <= 8:
        return "TRAUMA CRANEOENCEFÁLICO SEVERO / Glasgow bajo"
    if total <= 12:
        return "COMPROMISO NEUROLÓGICO MODERADO"
    return "COMPROMISO LEVE O SIN DATOS DE GRAVEDAD MAYOR"


def _interpretar_pts(total):
    if total <= 8:
        return "TRAUMA PEDIÁTRICO MAYOR / ALTO RIESGO"
    return "TRAUMA PEDIÁTRICO NO MAYOR SEGÚN PTS"


def _interpretar_westley(total):
    if total <= 2:
        return "CRUP LEVE"
    if total <= 7:
        return "CRUP MODERADO"
    if total <= 11:
        return "CRUP SEVERO"
    return "FALLA RESPIRATORIA INMINENTE"


def _interpretar_wood_downes(total):
    if total <= 3:
        return "OBSTRUCCIÓN BRONQUIAL LEVE"
    if total <= 7:
        return "OBSTRUCCIÓN BRONQUIAL MODERADA"
    return "OBSTRUCCIÓN BRONQUIAL SEVERA"


def _interpretar_tal(total):
    if total <= 4:
        return "BRONQUIOLITIS / OBSTRUCCIÓN LEVE"
    if total <= 8:
        return "BRONQUIOLITIS / OBSTRUCCIÓN MODERADA"
    return "BRONQUIOLITIS / OBSTRUCCIÓN SEVERA"


def _interpretar_deshidratacion(total):
    if total == 0:
        return "SIN DESHIDRATACIÓN CLÍNICA"
    if total <= 4:
        return "ALGÚN GRADO DE DESHIDRATACIÓN"
    return "DESHIDRATACIÓN MODERADA A SEVERA"


def _interpretar_tep(apariencia, respiratorio, circulacion):
    if apariencia == 0 and respiratorio == 0 and circulacion == 0:
        return "TEP NORMAL"
    if apariencia == 0 and respiratorio == 1 and circulacion == 0:
        return "DIFICULTAD RESPIRATORIA"
    if apariencia == 1 and respiratorio == 1 and circulacion == 0:
        return "FALLA RESPIRATORIA"
    if apariencia == 0 and respiratorio == 0 and circulacion == 1:
        return "CHOQUE COMPENSADO"
    if apariencia == 1 and respiratorio == 0 and circulacion == 1:
        return "CHOQUE DESCOMPENSADO / FALLA CARDIOPULMONAR"
    if apariencia == 1 and respiratorio == 0 and circulacion == 0:
        return "DISFUNCIÓN DEL SNC / METABÓLICA"
    return "PACIENTE DE ALTO RIESGO - REQUIERE VALORACIÓN INMEDIATA"


def _interpretar_pews(total):
    if total <= 2:
        return "RIESGO BAJO"
    if total <= 4:
        return "RIESGO INTERMEDIO / REQUIERE VIGILANCIA"
    if total <= 6:
        return "RIESGO ALTO / REVALORACIÓN MÉDICA PRONTA"
    return "RIESGO MUY ALTO / ESCALAMIENTO INMEDIATO"


def _render_silverman():
    st.subheader("Silverman-Andersen")
    st.caption("Útil para valorar dificultad respiratoria neonatal.")
    total = 0
    for item_key, item in SILVERMAN_ITEMS.items():
        total += _radio_score(item["label"], item["options"], key=f"silverman_{item_key}")

    interpretacion = _interpretar_silverman(total)
    st.success(f"Puntaje total: {total}/10")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area(
        "Resumen del score",
        value=f"SILVERMAN-ANDERSEN: {total}/10 - {interpretacion}",
        height=90,
        key="silverman_resumen",
    )


def _render_glasgow():
    st.subheader("Glasgow pediátrico")
    st.caption("Versión práctica para niño verbal y lactante / preverbal.")
    grupo = st.selectbox(
        "Grupo etario para respuesta verbal",
        ["NIÑO VERBAL", "LACTANTE / PREVERBAL"],
        key="glasgow_grupo",
    )
    ocular = _radio_score("Respuesta ocular", GLASGOW_OCULAR, key="glasgow_ocular")
    verbal = _radio_score(
        "Respuesta verbal",
        GLASGOW_VERBAL_NINO if grupo == "NIÑO VERBAL" else GLASGOW_VERBAL_LACTANTE,
        key="glasgow_verbal",
    )
    motora = _radio_score("Respuesta motora", GLASGOW_MOTORA, key="glasgow_motora")

    total = ocular + verbal + motora
    interpretacion = _interpretar_glasgow(total)
    st.success(f"Glasgow total: {total}/15")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area(
        "Resumen del score",
        value=f"GLASGOW PEDIÁTRICO: {total}/15 - {interpretacion}",
        height=90,
        key="glasgow_resumen",
    )


def _render_pts():
    st.subheader("Pediatric Trauma Score")
    st.caption("Herramienta rápida para estimar gravedad del trauma pediátrico.")
    total = 0
    for item_key, item in PTS_ITEMS.items():
        total += _radio_score(item["label"], item["options"], key=f"pts_{item_key}")

    interpretacion = _interpretar_pts(total)
    st.success(f"PTS total: {total}")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area(
        "Resumen del score",
        value=f"PEDIATRIC TRAUMA SCORE: {total} - {interpretacion}",
        height=90,
        key="pts_resumen",
    )


def _render_westley():
    st.subheader("Westley")
    st.caption("Escala clínica para gravedad del crup.")
    total = sum(_radio_score(item["label"], item["options"], key=f"westley_{k}") for k, item in WESTLEY_ITEMS.items())
    interpretacion = _interpretar_westley(total)
    st.success(f"Westley total: {total}")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area("Resumen del score", value=f"WESTLEY: {total} - {interpretacion}", height=90, key="westley_resumen")


def _render_wood_downes():
    st.subheader("Wood-Downes-Ferrés")
    st.caption("Escala orientativa de obstrucción bronquial.")
    total = sum(_radio_score(item["label"], item["options"], key=f"wood_{k}") for k, item in WOOD_DOWNES_ITEMS.items())
    interpretacion = _interpretar_wood_downes(total)
    st.success(f"Wood-Downes-Ferrés total: {total}")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area("Resumen del score", value=f"WOOD-DOWNES-FERRÉS: {total} - {interpretacion}", height=90, key="wood_resumen")


def _render_tal():
    st.subheader("TAL")
    st.caption("Escala clínica orientativa para bronquiolitis / obstrucción.")
    total = sum(_radio_score(item["label"], item["options"], key=f"tal_{k}") for k, item in TAL_ITEMS.items())
    interpretacion = _interpretar_tal(total)
    st.success(f"TAL total: {total}")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area("Resumen del score", value=f"TAL: {total} - {interpretacion}", height=90, key="tal_resumen")


def _render_deshidratacion():
    st.subheader("Deshidratación clínica")
    st.caption("Basada en apariencia, ojos, mucosas y lágrimas.")
    total = sum(_radio_score(item["label"], item["options"], key=f"desh_{k}") for k, item in DESHIDRATACION_ITEMS.items())
    interpretacion = _interpretar_deshidratacion(total)
    st.success(f"Score de deshidratación: {total}/8")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area("Resumen del score", value=f"DESHIDRATACIÓN CLÍNICA: {total}/8 - {interpretacion}", height=90, key="desh_resumen")


def _render_tep():
    st.subheader("Triángulo de Evaluación Pediátrica (TEP)")
    st.caption("Evaluación visual rápida: apariencia, trabajo respiratorio y circulación cutánea.")
    apariencia = _radio_score("Apariencia", TEP_OPTIONS, key="tep_apariencia")
    respiratorio = _radio_score("Trabajo respiratorio", TEP_OPTIONS, key="tep_respiratorio")
    circulacion = _radio_score("Circulación cutánea", TEP_OPTIONS, key="tep_circulacion")
    interpretacion = _interpretar_tep(apariencia, respiratorio, circulacion)
    st.success("TEP completado")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area("Resumen del score", value=f"TEP: {interpretacion}", height=90, key="tep_resumen")


def _render_pews():
    st.subheader("PEWS")
    st.caption("Versión práctica por comportamiento, cardiovascular y respiratorio.")
    conducta = _radio_score("Comportamiento", PEWS_BEHAVIOR, key="pews_behavior")
    cardio = _radio_score("Cardiovascular", PEWS_CARDIO, key="pews_cardio")
    respiratorio = _radio_score("Respiratorio", PEWS_RESP, key="pews_resp")
    total = conducta + cardio + respiratorio
    interpretacion = _interpretar_pews(total)
    st.success(f"PEWS total: {total}")
    st.info(f"Interpretación: {interpretacion}")
    st.text_area("Resumen del score", value=f"PEWS: {total} - {interpretacion}", height=90, key="pews_resumen")


def render():
    st.header("📏 Scores pediátricos")
    st.caption("Módulo independiente de las historias clínicas para cálculos rápidos.")

    score = st.selectbox(
        "Score pediátrico",
        [
            "Silverman-Andersen",
            "Glasgow pediátrico",
            "Pediatric Trauma Score",
            "Westley",
            "Wood-Downes-Ferrés",
            "TAL",
            "Deshidratación clínica",
            "Triángulo de Evaluación Pediátrica (TEP)",
            "PEWS",
        ],
        key="score_pediatrico_selector",
    )

    if score == "Silverman-Andersen":
        _render_silverman()
    elif score == "Glasgow pediátrico":
        _render_glasgow()
    elif score == "Pediatric Trauma Score":
        _render_pts()
    elif score == "Westley":
        _render_westley()
    elif score == "Wood-Downes-Ferrés":
        _render_wood_downes()
    elif score == "TAL":
        _render_tal()
    elif score == "Deshidratación clínica":
        _render_deshidratacion()
    elif score == "Triángulo de Evaluación Pediátrica (TEP)":
        _render_tep()
    elif score == "PEWS":
        _render_pews()

    st.caption("PRISM no está incluida por ahora porque requiere muchas variables fisiológicas y de laboratorio tipo UCI; prefiero dejarla bien hecha en un siguiente paso.")
