from servicios.consulta_externa_base import render_consulta_externa


def render():
    render_consulta_externa(
        prefix="ped_pueri",
        titulo="CONSULTA EXTERNA - PEDIATRÍA Y PUERICULTURA",
        history_filename="historias_pediatria_puericultura.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=True,
        mostrar_pb=True,
        modo_pediatrico_urgencias_primera_vez=True,
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
            "Usa únicamente la información entregada. No inventes diagnósticos ni medicamentos no sustentados por el caso. "
            "Redacta el PLAN en MAYÚSCULAS, una indicación por línea, orientado a MANEJO AMBULATORIO. "
            "Puedes sugerir manejo sintomático, recomendaciones generales, educación a cuidadores, signos de alarma y seguimiento por consulta externa según la historia clínica y la patología. "
            "Si no hay datos para un medicamento específico, limita el plan a recomendaciones y seguimiento."
        ),
    )
