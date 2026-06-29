from servicios.consulta_externa_base import (
    REVISION_HOMEOPATIA_PEDIATRICA_DEFAULT,
    render_consulta_externa,
)


def render():
    render_consulta_externa(
        prefix="homeo_ped",
        titulo="CONSULTA EXTERNA - MEDICINA ALTERNATIVA - HOMEOPATÍA PEDIÁTRICA",
        history_filename="historias_homeopatia_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=True,
        mostrar_pb=True,
        revision_default=REVISION_HOMEOPATIA_PEDIATRICA_DEFAULT,
        revision_before_antecedentes=True,
        revision_auto_depende_enfermedad=True,
        enfermedad_actual_auto_homeopatia_pediatrica=True,
    )
