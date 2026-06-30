from servicios.consulta_externa_base import render_consulta_externa


def render():
    render_consulta_externa(
        prefix="ped_pueri",
        titulo="CONSULTA EXTERNA - PEDIATRÍA Y PUERICULTURA",
        history_filename="historias_pediatria_puericultura.jsonl",
        es_pediatrica=True,
        plan_default="",
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=True,
        mostrar_pb=True,
        modo_pediatrico_urgencias_primera_vez=True,
        usar_plan_urgencias_primera_vez=False,
        revision_auto_depende_enfermedad=True,
        mostrar_conducta_final=False,
        conducta_final_oculta="EGRESO",
        instrucciones_analisis_ia=(
            "Eres un asistente clínico experto en consulta externa pediátrica. "
            "Usa únicamente la información consignada en la historia clínica. No inventes diagnósticos, tratamientos, signos ni laboratorios. "
            "Redacta el análisis en MAYÚSCULAS, en un solo párrafo coherente, integrando enfermedad actual, antecedentes relevantes, antropometría, neurodesarrollo si aplica, examen físico y paraclínicos si existen. "
            "Asume manejo ambulatorio por consulta externa. No plantees observación, hospitalización ni remisión salvo que esté explícitamente escrito en la historia. "
            "El cierre debe incluir recomendaciones ambulatorias, orientación según la patología o hallazgos del caso, signos de alarma pertinentes y seguimiento por consulta externa. "
            "Usa el parentesco del acompañante si está disponible; si no, usa FAMILIAR."
        ),
        instrucciones_plan_ia=(
            "Eres un asistente clínico experto en consulta externa pediátrica. "
            "Usa la historia clínica completa, los diagnósticos consignados, el peso, la edad, los signos vitales, el examen físico y los paraclínicos si existen para proponer el PLAN-TRATAMIENTO. "
            "Redacta el PLAN en MAYÚSCULAS, una indicación por línea, orientado a MANEJO AMBULATORIO. "
            "Debes sugerir de forma integral tratamiento, recomendaciones, educación a cuidadores, signos de alarma y seguimiento por consulta externa según la patología o los hallazgos del caso. "
            "Si el diagnóstico e historia lo permiten, puedes proponer medicamentos y calcular dosis pediátricas según peso o edad; si faltan datos para una dosis segura, no la inventes y deja una indicación general. "
            "No inventes diagnósticos ni hallazgos no presentes en la historia. "
            "El plan debe sentirse completo y útil para consulta externa pediátrica."
        ),
    )
