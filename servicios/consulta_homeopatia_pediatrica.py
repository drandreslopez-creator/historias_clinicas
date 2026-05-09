from servicios.consulta_externa_base import render_consulta_externa


def render():
    render_consulta_externa(
        prefix="homeo_ped",
        titulo="CONSULTA EXTERNA - HOMEOPATÍA PEDIÁTRICA",
        history_filename="historias_homeopatia_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
    )
