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
        "terminos": ("ASMA", "SIBILANCIAS", "BRONCOESPASMO", "EXACERBACION ASM", "SINDROME BRONCOOBSTRUCTIVO", "SÍNDROME BRONCOOBSTRUCTIVO", "SBO"),
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
            "REGISTRE LA RESPUESTA OBJETIVA AL BRONCODILATADOR Y LA CONSTANCIA DE INFORMACIÓN BRINDADA SOBRE TÉCNICA INHALATORIA CUANDO APLIQUE.",
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
    "FIEBRE": {
        "codigos": ("R50",),
        "terminos": ("SINDROME FEBRIL", "SÍNDROME FEBRIL", "FIEBRE SIN FOCO", "FIEBRE DE ORIGEN"),
        "nombre": "ENFERMEDAD FEBRIL / FIEBRE SIN FOCO",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Enfermedad febril",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-5/enfermedad-febril/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "DURACIÓN, TEMPERATURA, ESTADO GENERAL Y BÚSQUEDA DE FOCO CLÍNICO",
            "SIGNOS GENERALES DE PELIGRO Y HALLAZGOS DE ALARMA",
            "JUSTIFICACIÓN DE PARACLÍNICOS, OBSERVACIÓN, HOSPITALIZACIÓN O EGRESO",
            "ANTIPIRÉTICO, HIDRATACIÓN, SIGNOS DE ALARMA Y CONTROL",
        ),
        "alertas": (
            "DOCUMENTE LOS HALLAZGOS POSITIVOS Y NEGADOS DE FORMA CONCORDANTE; NO AFIRME UN FOCO NI UNA INFECCIÓN BACTERIANA SIN SUSTENTO CLÍNICO.",
        ),
        "verificaciones": {
            "ESTADO GENERAL, TIEMPO DE EVOLUCIÓN Y TEMPERATURA": ("ESTADO GENERAL", "EVOLUCI", "FIEBRE", "TEMPERATURA"),
            "BÚSQUEDA DE FOCO Y SIGNOS DE ALARMA": ("FOCO", "PETEQUI", "RIGIDEZ", "DIFICULTAD RESPIRATORIA", "CONVULS"),
            "PARACLÍNICOS Y SITIO DE MANEJO": ("PARACLIN", "UROANAL", "OBSERV", "HOSPITAL", "EGRESO"),
            "SIGNOS DE ALARMA / CONTROL": ("SIGNOS DE ALARMA", "RECONSULT", "CONTROL", "SEGUIMIENTO"),
        },
    },
    "DESNUTRICION": {
        "codigos": ("E44", "E43", "E45"),
        "terminos": ("DESNUTRICION AGUDA", "DESNUTRICIÓN AGUDA", "RIESGO DE DESNUTRICION", "RIESGO DE DESNUTRICIÓN", "MALNUTRICION", "MALNUTRICIÓN"),
        "nombre": "DESNUTRICIÓN AGUDA Y RIESGO NUTRICIONAL",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Desnutrición aguda",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-8/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "ANTROPOMETRÍA, PESO/TALLA, PERÍMETRO BRAQUIAL Y EDEMA BILATERAL",
            "APETITO, INGESTA, DIURESIS, COMORBILIDADES Y SIGNOS GENERALES DE PELIGRO",
            "CLASIFICACIÓN NUTRICIONAL Y JUSTIFICACIÓN DE MANEJO AMBULATORIO, OBSERVACIÓN O HOSPITALIZACIÓN",
            "PLAN ALIMENTARIO, SUPLEMENTACIÓN O REMISIÓN SEGÚN PROTOCOLO, CONTROL Y CONSEJERÍA",
        ),
        "alertas": (
            "CORROBORE LA CLASIFICACIÓN ANTROPOMÉTRICA CON LOS ESTÁNDARES OMS Y EL PROTOCOLO INSTITUCIONAL ANTES DE DEFINIR LA CONDUCTA.",
        ),
        "verificaciones": {
            "ANTROPOMETRÍA, PB Y EDEMA BILATERAL": ("PESO", "TALLA", "P/T", "PB", "EDEMA"),
            "APETITO, INGESTA, HIDRATACIÓN Y SIGNOS DE PELIGRO": ("APETITO", "INGESTA", "HIDRAT", "VIA ORAL", "VÍA ORAL", "PELIGRO"),
            "CLASIFICACIÓN Y SITIO DE MANEJO": ("DESNUTRIC", "RIESGO", "OBSERV", "HOSPITAL", "EGRESO", "NUTRIC"),
            "PLAN NUTRICIONAL / CONTROL": ("ALIMENT", "NUTRIC", "CONTROL", "SEGUIMIENTO", "RECONSULT"),
        },
    },
    "OTITIS": {
        "codigos": ("H66",),
        "terminos": ("OTITIS MEDIA", "OTITIS", "OTALGIA"),
        "nombre": "OTITIS MEDIA AGUDA",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Otitis media aguda",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-6/otitis-media-aguda/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "OTOSCOPIA, LATERALIDAD Y HALLAZGOS DE INFLAMACIÓN / DERRAME DEL OÍDO MEDIO",
            "DOLOR, FIEBRE, OTORREA, ESTADO GENERAL Y SIGNOS DE COMPLICACIÓN",
            "JUSTIFICACIÓN DE OBSERVACIÓN O ANTIBIÓTICO, CON VÍA, DOSIS, INTERVALO Y DURACIÓN CUANDO APLIQUE",
            "ANALGESIA, CONTROL Y SIGNOS DE ALARMA",
        ),
        "alertas": (
            "DOCUMENTE LA OTOSCOPIA Y LA LATERALIDAD. ANTE SOSPECHA DE MASTOIDITIS U OTRA COMPLICACIÓN, JUSTIFIQUE REMISIÓN O MANEJO HOSPITALARIO.",
        ),
        "verificaciones": {
            "OTOSCOPIA Y LATERALIDAD": ("OTOSCOP", "TIMPAN", "OIDO", "OÍDO", "DERECH", "IZQUIERD"),
            "DOLOR, FIEBRE, OTORREA Y SIGNOS DE COMPLICACIÓN": ("DOLOR", "FIEBRE", "OTORREA", "MASTOID", "ESTADO GENERAL"),
            "ANTIBIÓTICO / ANALGESIA Y SITIO DE MANEJO": ("AMOXICIL", "ANTIBIOT", "ANALGES", "OBSERV", "HOSPITAL", "EGRESO"),
            "SIGNOS DE ALARMA / CONTROL": ("SIGNOS DE ALARMA", "RECONSULT", "CONTROL", "SEGUIMIENTO"),
        },
    },
    "IVU": {
        "codigos": ("N39", "N10", "N12", "N30"),
        "terminos": ("INFECCION URINARIA", "INFECCIÓN URINARIA", "IVU", "PIELONEFRITIS", "CISTITIS"),
        "nombre": "INFECCIÓN DE VÍAS URINARIAS PEDIÁTRICA",
        "fuente": "Ministerio de Salud y Protección Social, Herramienta Clínica Primera Infancia - Infección de vías urinarias",
        "url": "https://herramientaclinicaprimerainfancia.minsalud.gov.co/modulo-5/infeccion-de-vias-urinarias/",
        "version": "Consulta institucional vigente",
        "documentacion": (
            "SÍNTOMAS URINARIOS, FIEBRE, ESTADO GENERAL Y FACTORES DE RIESGO",
            "UROANÁLISIS, TÉCNICA DE TOMA Y UROCULTIVO ANTES DEL ANTIBIÓTICO CUANDO SEA POSIBLE",
            "JUSTIFICACIÓN DE HOSPITALIZACIÓN, ANTIBIÓTICO EMPÍRICO, VÍA, DOSIS E INTERVALO",
            "SEGUIMIENTO DEL UROCULTIVO, RESPUESTA CLÍNICA Y AJUSTE SEGÚN ANTIBIOGRAMA",
            "SIGNOS DE ALARMA, CONTROL Y RECONSULTA",
        ),
        "alertas": (
            "DOCUMENTE LA TÉCNICA DE RECOLECCIÓN DE ORINA Y LA TOMA DEL UROCULTIVO ANTES DE INICIAR ANTIBIÓTICO, SI LA ESTABILIDAD CLÍNICA LO PERMITE.",
        ),
        "verificaciones": {
            "FIEBRE, SÍNTOMAS URINARIOS Y ESTADO GENERAL": ("FIEBRE", "DISURIA", "URIN", "ESTADO GENERAL"),
            "UROANÁLISIS, TÉCNICA DE TOMA Y UROCULTIVO": ("UROANALISIS", "UROANÁLISIS", "UROCULTIVO", "SONDA", "MICCION"),
            "ANTIBIÓTICO Y SITIO DE MANEJO": ("CEFAZOLINA", "ANTIBIOT", "ANTIBIÓT", "HOSPITAL", "EGRESO"),
            "SEGUIMIENTO DE CULTIVO / SIGNOS DE ALARMA": ("CULTIVO", "ANTIBIOGRAMA", "SIGNOS DE ALARMA", "RECONSULT"),
        },
    },
}


APOYOS_AIEPI = {
    "RESPIRATORIO": {
        "nombre": "EVALUACIÓN AIEPI: TOS O DIFICULTAD RESPIRATORIA",
        "criterios": (
            "SIGNOS GENERALES DE PELIGRO",
            "FRECUENCIA RESPIRATORIA Y TRABAJO RESPIRATORIO",
            "TIRAJE SUBCOSTAL, ESTRIDOR O SIBILANCIAS SEGÚN CORRESPONDA",
            "OXIMETRÍA Y RESPUESTA CLÍNICA",
            "CLASIFICACIÓN, SITIO DE MANEJO Y RECONSULTA",
        ),
    },
    "DIARREA": {
        "nombre": "EVALUACIÓN AIEPI: DIARREA / DESHIDRATACIÓN",
        "criterios": (
            "SIGNOS GENERALES DE PELIGRO",
            "DURACIÓN, CARACTERÍSTICAS DE LAS DEPOSICIONES Y SANGRE EN HECES",
            "ESTADO DE HIDRATACIÓN, TOLERANCIA ORAL Y DIURESIS",
            "PLAN DE HIDRATACIÓN, ALIMENTACIÓN Y REVALORACIÓN",
            "SIGNOS DE ALARMA Y RECONSULTA",
        ),
    },
    "FIEBRE": {
        "nombre": "EVALUACIÓN AIEPI: FIEBRE",
        "criterios": (
            "SIGNOS GENERALES DE PELIGRO Y ESTADO GENERAL",
            "TIEMPO DE EVOLUCIÓN, TEMPERATURA Y FOCO CLÍNICO",
            "EXANTEMA, RIGIDEZ DE CUELLO, PETEQUIAS U OTROS SIGNOS DE ALARMA SI APLICAN",
            "EXÁMENES COMPLEMENTARIOS O JUSTIFICACIÓN DE NO SOLICITARLOS",
            "CONDUCTA, SIGNOS DE ALARMA Y CONTROL",
        ),
    },
    "FIEBRE_URINARIA": {
        "nombre": "EVALUACIÓN AIEPI: FIEBRE CON SOSPECHA DE IVU",
        "criterios": (
            "SIGNOS GENERALES DE PELIGRO Y ESTADO GENERAL",
            "FIEBRE, SÍNTOMAS URINARIOS Y FOCO CLÍNICO",
            "UROANÁLISIS, TÉCNICA DE TOMA Y UROCULTIVO",
            "CRITERIOS DE HOSPITALIZACIÓN, ANTIBIÓTICO Y REVALORACIÓN",
            "SEGUIMIENTO DEL CULTIVO, SIGNOS DE ALARMA Y CONTROL",
        ),
    },
    "INTEGRAL": {
        "nombre": "EVALUACIÓN AIEPI INTEGRAL",
        "criterios": (
            "SIGNOS GENERALES DE PELIGRO Y ESTADO GENERAL",
            "ALIMENTACIÓN, HIDRATACIÓN Y DIURESIS",
            "CRECIMIENTO, DESARROLLO Y ESTADO NUTRICIONAL CUANDO APLIQUE",
            "INMUNIZACIÓN, CONSEJERÍA Y MEDIDAS DE PREVENCIÓN",
            "SIGNOS DE ALARMA, CONTROL Y RECONSULTA",
        ),
    },
}


def obtener_apoyo_aiepi(clave: str) -> dict:
    """Devuelve la definición del apoyo AIEPI seleccionado, si existe."""
    return APOYOS_AIEPI.get(clave, {})


def _apoyo_sin_ruta_gpc(diagnostico: object) -> tuple[str, tuple[str, ...]]:
    texto = _normalizar(diagnostico)
    if any(termino in texto for termino in ("TRAUMA CRANEO", "TCE", "TRAUMATISMO CRANEO")):
        return (
            "TRAUMA CRANEOENCEFÁLICO LEVE",
            (
                "MECANISMO, HORA DEL TRAUMA, PÉRDIDA DE CONOCIMIENTO, VÓMITO, CONVULSIONES Y AMNESIA",
                "ESCALA DE GLASGOW, EXAMEN NEUROLÓGICO, SIGNOS DE FRACTURA Y HALLAZGOS EN CUERO CABELLUDO",
                "JUSTIFICACIÓN DE OBSERVACIÓN, IMÁGENES, EGRESO O REMISIÓN SEGÚN RIESGO CLÍNICO",
                "INFORMACIÓN BRINDADA A PADRES O CUIDADOR RESPONSABLE, SIGNOS DE ALARMA NEUROLÓGICOS Y RECONSULTA INMEDIATA",
            ),
        )
    if any(termino in texto for termino in ("VOMITO", "VÓMITO", "EMETICO", "EMÉTICO")):
        return (
            "SÍNDROME EMÉTICO",
            (
                "FRECUENCIA, ASPECTO DEL VÓMITO, TOLERANCIA ORAL, DIURESIS Y ESTADO DE HIDRATACIÓN",
                "PRESENCIA O AUSENCIA DE VÓMITO BILIOSO, HEMATEMESIS, DOLOR INTENSO, DISTENSIÓN O SIGNOS NEUROLÓGICOS",
                "JUSTIFICACIÓN DE OBSERVACIÓN, PARACLÍNICOS, IMÁGENES O REMISIÓN SEGÚN HALLAZGOS",
                "PLAN DE HIDRATACIÓN, ALIMENTACIÓN, SIGNOS DE ALARMA Y CONTROL",
            ),
        )
    if any(termino in texto for termino in ("DOLOR ABDOMINAL", "ABDOMEN AGUDO")):
        return (
            "DOLOR ABDOMINAL PEDIÁTRICO",
            (
                "LOCALIZACIÓN, INTENSIDAD, EVOLUCIÓN, VÓMITO, DEPOSICIONES, DIURESIS Y RELACIÓN CON LA ALIMENTACIÓN",
                "EXAMEN ABDOMINAL SERIADO, SIGNOS PERITONEALES, MASAS, DISTENSIÓN Y EXAMEN GENITOURINARIO CUANDO APLIQUE",
                "JUSTIFICACIÓN DE OBSERVACIÓN, LABORATORIOS, ECOGRAFÍA, VALORACIÓN QUIRÚRGICA O EGRESO",
                "SIGNOS DE ALARMA ABDOMINAL, CONTROL Y RECONSULTA",
            ),
        )
    if any(termino in texto for termino in ("ESTRENIMIENTO", "CONSTIPACION", "CONSTIPACIÓN")):
        return (
            "ESTREÑIMIENTO / CONSTIPACIÓN",
            (
                "FRECUENCIA, CONSISTENCIA, BRISTOL, DOLOR, RETENCIÓN, SANGRE Y ENTRENAMIENTO ESFINTERIANO",
                "BÚSQUEDA DE BANDERAS ROJAS, IMPACTACIÓN, DISTENSIÓN, VÓMITO BILIOSO O ALTERACIÓN NEUROLÓGICA",
                "PLAN DE DESIMPACTACIÓN O MANTENIMIENTO, ALIMENTACIÓN, HÁBITO INTESTINAL Y ADHERENCIA",
                "SEGUIMIENTO, SIGNOS DE ALARMA Y CRITERIOS DE REMISIÓN",
            ),
        )
    if any(termino in texto for termino in ("RINOFARING", "RESFRIADO", "INFECCION RESPIRATORIA ALTA", "IRA ALTA")):
        return (
            "INFECCIÓN RESPIRATORIA ALTA / RINOFARINGITIS",
            (
                "DURACIÓN DEL CUADRO, ESTADO GENERAL Y TOLERANCIA A LA VÍA ORAL",
                "AUSENCIA O PRESENCIA DE SIGNOS DE DIFICULTAD RESPIRATORIA Y HALLAZGOS FOCALES",
                "JUSTIFICACIÓN CLÍNICA DE ANTIBIÓTICOS, PARACLÍNICOS O IMÁGENES SI SE INDICAN",
                "MANEJO SINTOMÁTICO, MEDIDAS GENERALES, SIGNOS DE ALARMA Y CONTROL",
            ),
        )
    if any(termino in texto for termino in ("FARING", "AMIGDAL", "ODINOFAG")):
        return (
            "FARINGITIS / FARINGOAMIGDALITIS",
            (
                "CRITERIOS CLÍNICOS, TOLERANCIA ORAL Y SIGNOS DE ALARMA",
                "EXPLORACIÓN DE EXUDADO, ADENOPATÍAS, EXANTEMA Y HALLAZGOS DIFERENCIALES",
                "JUSTIFICACIÓN DE PRUEBAS O ANTIBIÓTICO CUANDO APLIQUE",
                "ANALGESIA, HIDRATACIÓN, CONTROL Y RECONSULTA",
            ),
        )
    if any(termino in texto for termino in ("OTITIS", "OTALGIA")):
        return (
            "OTALGIA / OTITIS",
            (
                "OTOSCOPIA Y LATERALIDAD",
                "SEVERIDAD DEL DOLOR, FIEBRE, OTORREA Y ESTADO GENERAL",
                "JUSTIFICACIÓN DE OBSERVACIÓN O ANTIBIÓTICO CUANDO APLIQUE",
                "ANALGESIA, SIGNOS DE ALARMA Y CONTROL",
            ),
        )
    return (
        "APOYO CLÍNICO SEGÚN DIAGNÓSTICO",
        (
            "DIAGNÓSTICO PRINCIPAL, DIFERENCIALES Y HALLAZGOS QUE LO SUSTENTAN",
            "SEVERIDAD, ESTADO GENERAL, SIGNOS VITALES Y SIGNOS DE ALARMA",
            "CONDUCTA, TRATAMIENTO CON DOSIS/VÍA/DURACIÓN CUANDO APLIQUE Y JUSTIFICACIÓN CLÍNICA",
            "EDUCACIÓN, CONTROL Y CRITERIOS DE RECONSULTA",
        ),
    )


def detectar_apoyo_aiepi(diagnostico: object, texto_clinico: object = "") -> str:
    # La selección debe depender del diagnóstico, no de síntomas negados dentro
    # del relato clínico (p. ej. "niega diarrea" o "niega fiebre").
    texto = _normalizar(diagnostico)
    if any(termino in texto for termino in ("INFECCION URINARIA", "IVU", "PIELONEFRITIS", "CISTITIS", "UROCULTIVO")):
        return "FIEBRE_URINARIA"
    if any(termino in texto for termino in ("DIARREA", "GASTROENTERITIS", "DESHIDRAT")):
        return "DIARREA"
    if any(termino in texto for termino in ("TOS", "RINOFARING", "BRONQUI", "BRONCO", "NEUMON", "ASMA", "CRUP", "ESTRIDOR", "SIBILAN")):
        return "RESPIRATORIO"
    if any(termino in texto for termino in ("OTITIS", "OTALGIA")):
        return "FIEBRE"
    if any(termino in texto for termino in ("FIEBRE", "FEBRIL", "EXANTEMA")):
        return "FIEBRE"
    return "INTEGRAL"


def construir_apoyo_gpc_aiepi_automatico(
    diagnostico: object,
    texto_clinico: object,
) -> dict[str, str]:
    """Construye el contexto clínico automático para la redacción asistida.

    No emite una clasificación clínica nueva: orienta al modelo para que use
    exclusivamente los datos ya consignados en la historia.
    """
    ruta_clave = detectar_ruta_gpc(diagnostico, texto_clinico)
    apoyo_clave = detectar_apoyo_aiepi(diagnostico, texto_clinico)
    ruta = obtener_ruta_gpc(ruta_clave)
    apoyo = obtener_apoyo_aiepi(apoyo_clave)

    if ruta:
        instrucciones_gpc = resumen_gpc_para_ia(ruta_clave)
        fundamento_gpc = (
            f"SE REALIZÓ VALORACIÓN CLÍNICA ORIENTADA POR LA RUTA GPC DE {ruta['nombre']}, "
            "CON BASE EN LOS HALLAZGOS DOCUMENTADOS."
        )
    else:
        nombre_apoyo, recomendaciones = _apoyo_sin_ruta_gpc(diagnostico)
        instrucciones_gpc = (
            f"APOYO CLÍNICO AUTOMÁTICO SIN RUTA GPC ESPECÍFICA: {nombre_apoyo}. "
            f"CONSIDERAR: {'; '.join(recomendaciones)}. "
            "USA SOLO DATOS DOCUMENTADOS Y NO AFIRMES CUMPLIMIENTO DE UNA GPC ESPECÍFICA."
        )
        fundamento_gpc = ""

    criterios_aiepi = "; ".join(apoyo.get("criterios", ()))
    instrucciones_aiepi = (
        f"APOYO AIEPI AUTOMÁTICO: {apoyo.get('nombre', 'EVALUACIÓN PEDIÁTRICA INTEGRAL')}. "
        f"VALORA, SOLO CON LOS DATOS DOCUMENTADOS: {criterios_aiepi}. "
        "RESPETA LOS HALLAZGOS NEGADOS Y NO INVENTES CLASIFICACIONES, SIGNOS NI TRATAMIENTOS."
    )
    fundamento_aiepi = (
        f"SE INTEGRÓ LA {apoyo.get('nombre', 'EVALUACIÓN AIEPI INTEGRAL')} "
        "AL ANÁLISIS CLÍNICO SEGÚN LA INFORMACIÓN REGISTRADA."
    )
    return {
        "ruta_gpc": ruta_clave,
        "apoyo_aiepi": apoyo_clave,
        "instrucciones_gpc": instrucciones_gpc,
        "instrucciones_aiepi": instrucciones_aiepi,
        "fundamento": " ".join(item for item in (fundamento_gpc, fundamento_aiepi) if item),
    }


def render_apoyo_aiepi(st, *, diagnostico: object, texto_clinico: object, selector_key: str, registro_key: str) -> tuple[str, str, str, str]:
    sugerido = detectar_apoyo_aiepi(diagnostico, texto_clinico)
    opciones = list(APOYOS_AIEPI)
    actual = st.session_state.get(selector_key, sugerido)
    if actual not in opciones:
        actual = sugerido
    seleccionado = st.selectbox(
        "Apoyo AIEPI aplicable",
        opciones,
        index=opciones.index(actual),
        key=selector_key,
        format_func=lambda opcion: APOYOS_AIEPI[opcion]["nombre"],
        help="Apoyo para organizar la valoración pediátrica. Confirme siempre con AIEPI y el protocolo institucional vigente.",
    )
    apoyo = APOYOS_AIEPI[seleccionado]
    st.subheader("Apoyo AIEPI")
    st.caption("Registre cada criterio como PRESENTE, AUSENTE o con el hallazgo y conducta correspondiente.")
    respuestas_criterios = {}
    for indice, criterio in enumerate(apoyo["criterios"]):
        col_criterio, col_respuesta = st.columns([1.35, 2])
        with col_criterio:
            st.caption(criterio)
        with col_respuesta:
            respuestas_criterios[criterio] = st.text_input(
                criterio,
                key=f"{registro_key}_criterio_{indice}",
                label_visibility="collapsed",
                placeholder="PRESENTE, AUSENTE O HALLAZGO / CONDUCTA",
            )
    registro = st.text_area(
        "Registro clínico AIEPI",
        key=registro_key,
        height=110,
        placeholder="Amplíe clasificación, conducta, consejería, signos de alarma o control si es necesario.",
        help="Los registros AIEPI se integran de forma clínica al análisis y al plan final.",
    )
    lineas_registro = [
        f"{criterio}: {respuesta.strip()}"
        for criterio, respuesta in respuestas_criterios.items()
        if respuesta.strip()
    ]
    if registro.strip():
        lineas_registro.append(registro.strip())
    trazabilidad = (
        "\n".join([f"CLASIFICACIÓN AIEPI: {apoyo['nombre']}", *lineas_registro])
        if lineas_registro
        else ""
    )
    instrucciones = (
        f"APOYO AIEPI APLICABLE: {apoyo['nombre']}. "
        f"CONSIDERAR: {'; '.join(apoyo['criterios'])}. "
        f"REGISTRO AIEPI POR CRITERIOS: {'; '.join(lineas_registro) or 'SIN REGISTRO ADICIONAL.'}"
    )
    return seleccionado, trazabilidad, instrucciones, "\n".join(lineas_registro)


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
    respuestas_criterios: dict[str, str] | None = None,
) -> str:
    ruta = obtener_ruta_gpc(clave)
    if not ruta:
        return "NO SE DETECTÓ RUTA GPC ESPECÍFICA PARA EL DIAGNÓSTICO REGISTRADO."

    respuestas_criterios = respuestas_criterios or {}
    respuestas_texto = "\n".join(
        str(respuesta or "")
        for respuesta in respuestas_criterios.values()
        if str(respuesta or "").strip()
    )
    texto = _normalizar(f"{texto_clinico or ''}\n{registro_complementario or ''}\n{respuestas_texto}")
    lineas = []
    for etiqueta in ruta["verificaciones"]:
        respuesta = str(respuestas_criterios.get(etiqueta, "") or "").strip()
        if respuesta:
            lineas.append(f"{etiqueta}: {respuesta}")
    if str(registro_complementario or "").strip():
        lineas.append(str(registro_complementario).strip())
    if str(justificacion or "").strip():
        lineas.append("JUSTIFICACIÓN CLÍNICA DE APARTAMIENTO O INDIVIDUALIZACIÓN:")
        lineas.append(str(justificacion).strip())
    if not lineas:
        return ""
    return "\n".join([f"RUTA GPC APLICADA: {ruta['nombre']}", *lineas])


def render_trazabilidad_gpc(
    st,
    *,
    clave: str,
    diagnostico: object = "",
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
        nombre_apoyo, recomendaciones = _apoyo_sin_ruta_gpc(diagnostico)
        st.caption(f"No hay una ruta GPC específica seleccionada. Apoyo sugerido: {nombre_apoyo}.")
        st.caption("Registre los elementos que correspondan al diagnóstico y al protocolo institucional:")
        for recomendacion in recomendaciones:
            st.caption(f"- {recomendacion}")
        registro_complementario = st.text_area(
            "Registro clínico complementario",
            key=registro_key,
            height=110,
            placeholder="Documente hallazgos, conducta, recomendaciones, signos de alarma, control o justificación clínica.",
            help="Este registro apoya la coherencia del análisis y el plan, sin presentarse como una ruta GPC específica.",
        )
        justificacion = st.text_area(
            "Justificación clínica si se individualiza la conducta",
            key=justificacion_key,
            height=90,
        )
        lineas_registro = []
        if registro_complementario.strip():
            lineas_registro.append(registro_complementario.strip())
        if justificacion.strip():
            lineas_registro.extend(["JUSTIFICACIÓN CLÍNICA:", justificacion.strip()])
        trazabilidad = (
            "\n".join([f"APOYO CLÍNICO: {nombre_apoyo}", *lineas_registro])
            if lineas_registro
            else ""
        )
        instrucciones = (
            f"APOYO CLÍNICO SIN RUTA GPC ESPECÍFICA: {nombre_apoyo}. "
            f"CONSIDERAR: {'; '.join(recomendaciones)}. "
            f"REGISTRO CLÍNICO: {registro_complementario.strip() or 'SIN REGISTRO ADICIONAL.'}"
        )
        return "", trazabilidad, instrucciones, registro_complementario.strip()

    st.caption(f"Ruta detectada: {ruta['nombre']}")
    st.caption(f"Fuente: {ruta['fuente']}")
    st.link_button("Consultar fuente de la ruta", ruta["url"], use_container_width=False)
    st.caption("Para esta ruta, deje documentado según corresponda:")
    for item in ruta["documentacion"]:
        st.caption(f"- {item}")
    for alerta in ruta["alertas"]:
        st.info(alerta)

    respuestas_criterios = {}
    st.caption("Registro por criterios GPC:")
    for indice, etiqueta in enumerate(ruta["verificaciones"]):
        col_etiqueta, col_respuesta = st.columns([1.35, 2])
        with col_etiqueta:
            st.caption(etiqueta)
        with col_respuesta:
            respuestas_criterios[etiqueta] = st.text_input(
                etiqueta,
                key=f"{registro_key}_criterio_{indice}",
                label_visibility="collapsed",
                placeholder="REGISTRE HALLAZGOS, CONDUCTA O JUSTIFICACIÓN",
            )

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
            texto_clinico,
            justificacion,
            registro_complementario,
            respuestas_criterios,
        ),
        resumen_gpc_para_ia(ruta_seleccionada),
        "\n".join(
            [
                *(f"{etiqueta}: {respuesta}" for etiqueta, respuesta in respuestas_criterios.items() if respuesta.strip()),
                registro_complementario.strip(),
            ]
        ).strip(),
    )
