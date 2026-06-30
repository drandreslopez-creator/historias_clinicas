from servicios.consulta_externa_base import (
    REVISION_HOMEOPATIA_PEDIATRICA_DEFAULT,
    SINTOMAS_GENERALES_HOMEOPATIA_PEDIATRICA_DEFAULT,
    render_consulta_externa,
)


def render():
    render_consulta_externa(
        prefix="homeo_ped",
        titulo="CONSULTA EXTERNA - MEDICINA ALTERNATIVA - HOMEOPATÍA PEDIÁTRICA",
        history_filename="historias_homeopatia_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=True,
        mostrar_pb=True,
        modo_pediatrico_urgencias_primera_vez=True,
        revision_default=REVISION_HOMEOPATIA_PEDIATRICA_DEFAULT,
        revision_before_antecedentes=True,
        revision_auto_depende_enfermedad=True,
        enfermedad_actual_auto_homeopatia_pediatrica=False,
        mostrar_sintomas_generales=True,
        sintomas_generales_default=SINTOMAS_GENERALES_HOMEOPATIA_PEDIATRICA_DEFAULT,
    )
