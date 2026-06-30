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
    )
