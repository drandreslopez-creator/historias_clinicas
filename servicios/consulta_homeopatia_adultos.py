from servicios.consulta_externa_base import render_consulta_externa


def render():
    render_consulta_externa(
        prefix="homeo_adult",
        titulo="CONSULTA EXTERNA - MEDICINA ALTERNATIVA - HOMEOPATÍA ADULTOS",
        history_filename="historias_homeopatia_adultos.jsonl",
        es_pediatrica=False,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=True,
    )
