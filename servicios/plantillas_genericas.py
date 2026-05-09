from servicios.consulta_externa_base import render_consulta_externa


def render_telemedicina_pediatria():
    render_consulta_externa(
        prefix="tele_ped",
        titulo="HISTORIA CLÍNICA DE TELEMEDICINA - PEDIATRÍA",
        history_filename="historias_telemedicina_pediatria.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=True,
    )


def render_telemedicina_homeopatia_pediatrica():
    render_consulta_externa(
        prefix="tele_homeo_ped",
        titulo="HISTORIA CLÍNICA DE TELEMEDICINA - HOMEOPATÍA PEDIÁTRICA",
        history_filename="historias_telemedicina_homeopatia_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=True,
    )


def render_telemedicina_homeopatia_adultos():
    render_consulta_externa(
        prefix="tele_homeo_adult",
        titulo="HISTORIA CLÍNICA DE TELEMEDICINA - HOMEOPATÍA ADULTOS",
        history_filename="historias_telemedicina_homeopatia_adultos.jsonl",
        es_pediatrica=False,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=True,
    )


def render_consulta_neonatologia():
    render_consulta_externa(
        prefix="consulta_neonat",
        titulo="CONSULTA EXTERNA - NEONATOLOGÍA",
        history_filename="historias_consulta_neonatologia.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=True,
    )


def render_hospitalizacion_ingreso():
    render_consulta_externa(
        prefix="hosp_ingreso_ped",
        titulo="HISTORIA CLINICA DE INGRESO A HOSPITALIZACIÓN PEDIÁTRICA",
        history_filename="historias_hospitalizacion_ingreso_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=False,
    )


def render_hospitalizacion_evolucion():
    render_consulta_externa(
        prefix="hosp_evol_ped",
        titulo="NOTA DE EVOLUCIÓN DE HOSPITALIZACIÓN PEDIÁTRICA",
        history_filename="historias_hospitalizacion_evolucion_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=False,
    )


def render_hospitalizacion_interconsulta():
    render_consulta_externa(
        prefix="hosp_inter_ped",
        titulo="RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA",
        history_filename="historias_hospitalizacion_interconsulta_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=False,
    )


def render_neonatologia_evolucion_alojamiento():
    render_consulta_externa(
        prefix="neo_alojamiento",
        titulo="EVOLUCIÓN DEL RECIÉN NACIDO EN ALOJAMIENTO CONJUNTO",
        history_filename="historias_neonatologia_alojamiento_conjunto.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
    )


def render_neonatologia_interconsulta():
    render_consulta_externa(
        prefix="neo_interconsulta",
        titulo="RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA PERINATAL Y NEONATOLOGÍA",
        history_filename="historias_neonatologia_interconsulta.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
    )


def render_neonatologia_evolucion_urgencias():
    render_consulta_externa(
        prefix="neo_urgencias",
        titulo="EVOLUCIÓN DEL RECIÉN NACIDO EN SERVICIO DE URGENCIAS",
        history_filename="historias_neonatologia_urgencias.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
    )


def render_neonatologia_ingreso_unidad():
    render_consulta_externa(
        prefix="neo_ingreso_unidad",
        titulo="HISTORIA CLINICA DE INGRESO A UNIDAD DE RECIÉN NACIDOS",
        history_filename="historias_neonatologia_ingreso_unidad.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
    )


def render_neonatologia_evolucion_ucin():
    render_consulta_externa(
        prefix="neo_ucin",
        titulo="EVOLUCIÓN DEL RECIÉN NACIDO EN UCIN",
        history_filename="historias_neonatologia_ucin.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
    )
