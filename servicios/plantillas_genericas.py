from servicios.consulta_externa_base import render_consulta_externa


ANTECEDENTES_CONSULTA_NEONATOLOGIA_DEFAULT = """NEONATALES: PRODUCTO DE # GESTACIÓN, MADRE DE XX AÑOS, CONTROLADO, SIN COMPLICACIONES, STORCH NEGATIVO, ECOGRAFÍAS ANTENATALES NORMALES. NACE VÍA VAGINAL/ CESAREA A LAS XX SEMANAS, PESO XXXX GR - TALLA XX CM. NO REQUIRIÓ OXIGENO SUPLEMENTARIO, NO REQUIRIÓ HOSPITALIZACIÓN, EGRESO CONJUNTO.
INMUNOLÓGICOS: VACUNAS AL DÍA SEGÚN PAI (NO DOCUMENTADO); NO HA PRESENTADO REACCIONES ATRIBUIDAS A VACUNAS.
ALIMENTACIÓN: ACORDE A EDAD.
PATOLÓGICOS: NIEGA.
HOSPITALARIOS: NIEGA.
FARMACOLÓGICOS: NIEGA.
TRAUMÁTICOS: NIEGA.
TOXICOLÓGICO: NIEGA EXPOSICIÓN A HUMO DE LEÑA O CIGARRILLO.
ALÉRGICOS: NIEGA.
TRANSFUSIONALES: NIEGA.
QUIRÚRGICOS: NIEGA.
FAMILIARES: PADRE Y MADRE SANOS (NO CONSANGUÍNEOS), HERMANOS XX.
HEMOCLASIFICACIÓN: O POSITIVO.
PSICOSOCIALES: VIVIENDA CON TODOS LOS SERVICIOS, MASCOTAS XX."""


EXAMEN_CONSULTA_NEONATOLOGIA_DEFAULT = """PACIENTE LUCE EN BUEN ESTADO GENERAL, ALERTA, BUEN ESTADO DE HIDRATACIÓN, AFEBRIL.

CABEZA: NORMOCÉFALA, FONTANELA ANTERIOR NORMOTENSA, SIN LESIONES.
OJOS: CONJUNTIVAS ROSADAS, ESCLERAS ANICTÉRICAS.
OÍDOS: SIN ALTERACIONES.
NARIZ: PERMEABLE.
OROFARINGE: MUCOSAS HÚMEDAS, SIN LESIONES.
CUELLO: MÓVIL, SIN ADENOPATÍAS.
TÓRAX: SIMÉTRICO, NORMOEXPANSIBLE, SIN TIRAJES.
CARDIOPULMONAR: RUIDOS CARDIACOS RÍTMICOS, SIN SOPLOS, SIN AGREGADOS PULMONARES, OXIMETRIAS ADECUADAS AL AIRE AMBIENTE.
ABDOMEN: NO DISTENDIDO, RSHS PRESENTES, BLANDO, NO DOLOROSO, SIN SIGNOS DE IRRITACIÓN PERITONEAL.
GENITALES: INFANTILES ACORDES NORMOCONFIGURADOS.
EXTREMIDADES: EUTROFICAS, SIN EDEMAS.
NEUROLÓGICO: ALERTA, NO FOCALIZACIONES, SIN SIGNOS DE MENINGISMO, ROT NORMALES, FUERZA MUSCULAR CONSERVADA, MORO (+), SUCCION (+), BUSQUEDA (+), SIN DÉFICIT.
PIEL: ROSADA, BIEN PERFUNDIDA, SIN LESIONES."""


def render_telemedicina_pediatria():
    render_consulta_externa(
        prefix="tele_ped",
        titulo="HISTORIA CLÍNICA DE TELEMEDICINA - PEDIATRÍA",
        history_filename="historias_telemedicina_pediatria.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=True,
        mostrar_pb=True,
    )


def render_telemedicina_homeopatia_pediatrica():
    render_consulta_externa(
        prefix="tele_homeo_ped",
        titulo="HISTORIA CLÍNICA DE TELEMEDICINA - HOMEOPATÍA PEDIÁTRICA",
        history_filename="historias_telemedicina_homeopatia_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=True,
        mostrar_pb=True,
    )


def render_telemedicina_homeopatia_adultos():
    render_consulta_externa(
        prefix="tele_homeo_adult",
        titulo="HISTORIA CLÍNICA DE TELEMEDICINA - HOMEOPATÍA ADULTOS",
        history_filename="historias_telemedicina_homeopatia_adultos.jsonl",
        es_pediatrica=False,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=True,
        mostrar_pb=False,
    )


def render_consulta_neonatologia():
    render_consulta_externa(
        prefix="consulta_neonat",
        titulo="CONSULTA EXTERNA - NEONATOLOGÍA",
        history_filename="historias_consulta_neonatologia.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=True,
        mostrar_pb=False,
        antecedentes_default=ANTECEDENTES_CONSULTA_NEONATOLOGIA_DEFAULT,
        examen_default=EXAMEN_CONSULTA_NEONATOLOGIA_DEFAULT,
        mostrar_conducta_final=False,
        conducta_final_oculta="EGRESO",
        mostrar_diagnosticos_principales=False,
        usar_ia_analisis=False,
        usar_ia_plan=False,
        usar_ia_observacion_dx=False,
        mostrar_boton_ejemplo=False,
    )


def render_hospitalizacion_ingreso():
    render_consulta_externa(
        prefix="hosp_ingreso_ped",
        titulo="HISTORIA CLINICA DE INGRESO A HOSPITALIZACIÓN PEDIÁTRICA",
        history_filename="historias_hospitalizacion_ingreso_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=False,
        mostrar_pb=True,
    )


def render_hospitalizacion_evolucion():
    render_consulta_externa(
        prefix="hosp_evol_ped",
        titulo="NOTA DE EVOLUCIÓN DE HOSPITALIZACIÓN PEDIÁTRICA",
        history_filename="historias_hospitalizacion_evolucion_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=False,
        mostrar_pb=True,
    )


def render_hospitalizacion_interconsulta():
    render_consulta_externa(
        prefix="hosp_inter_ped",
        titulo="RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA",
        history_filename="historias_hospitalizacion_interconsulta_pediatrica.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=True,
        mostrar_modalidad_consulta=False,
        mostrar_pb=True,
    )


def render_neonatologia_evolucion_alojamiento():
    render_consulta_externa(
        prefix="neo_alojamiento",
        titulo="EVOLUCIÓN DEL RECIÉN NACIDO EN ALOJAMIENTO CONJUNTO",
        history_filename="historias_neonatologia_alojamiento_conjunto.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
        mostrar_pb=False,
    )


def render_neonatologia_interconsulta():
    render_consulta_externa(
        prefix="neo_interconsulta",
        titulo="RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA PERINATAL Y NEONATOLOGÍA",
        history_filename="historias_neonatologia_interconsulta.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
        mostrar_pb=False,
    )


def render_neonatologia_evolucion_urgencias():
    render_consulta_externa(
        prefix="neo_urgencias",
        titulo="EVOLUCIÓN DEL RECIÉN NACIDO EN SERVICIO DE URGENCIAS",
        history_filename="historias_neonatologia_urgencias.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
        mostrar_pb=False,
    )


def render_neonatologia_ingreso_unidad():
    render_consulta_externa(
        prefix="neo_ingreso_unidad",
        titulo="HISTORIA CLINICA DE INGRESO A UNIDAD DE RECIÉN NACIDOS",
        history_filename="historias_neonatologia_ingreso_unidad.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
        mostrar_pb=False,
    )


def render_neonatologia_evolucion_ucin():
    render_consulta_externa(
        prefix="neo_ucin",
        titulo="EVOLUCIÓN DEL RECIÉN NACIDO EN UCIN",
        history_filename="historias_neonatologia_ucin.jsonl",
        es_pediatrica=True,
        mostrar_neurodesarrollo=False,
        mostrar_modalidad_consulta=False,
        mostrar_pb=False,
    )
