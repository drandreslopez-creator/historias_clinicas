import streamlit as st
from datetime import date

from core.calculos import calcular_edad, edad_en_meses
from core.clasificacion import grupo_etario
from core.texto import sexo_texto
from herramientas.neurodesarrollo import obtener_neurodesarrollo
from herramientas.antropometria import calcular_imc
from herramientas.oms_full import (
    zscore_peso_edad,
    zscore_talla_edad,
    zscore_imc_edad,
    zscore_peso_talla,
    zscore_pc_edad
)

# 🔥 IMPORTANTE (NUEVO)
from herramientas.diagnostico_nutricional import (
    diagnostico_menor_5,
    diagnostico_mayor_5
)

def render():

    st.header("📌 HISTORIA CLÍNICA - PEDIATRÍA URGENCIAS")

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre", key="nombre_1")
        documento = st.text_input("Documento", key="documento_1")
        fecha_nacimiento = st.date_input(
            "Fecha de nacimiento",
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key="fecha_1"
        )

    with col2:
        sexo = st.selectbox("Sexo", ["Masculino", "Femenino"], key="sexo_1")
        eps = st.text_input("EPS", key="eps_1")
        informante = st.text_input("Informante", key="informante_1")

    z_pe = z_te = z_imc = z_pt = z_pc = None
    dx_nutricional = "NO EVALUADO"

    años = meses = 0
    grupo = ""
    sexo_data = {"paciente": "paciente"}

    if fecha_nacimiento:
        años, meses, dias = calcular_edad(fecha_nacimiento)
        grupo = grupo_etario(años)
        sexo_data = sexo_texto(sexo)

        st.info(f"Edad: {años} años, {meses} meses, {dias} días")

    motivo = st.text_area("Motivo de consulta", key="motivo_1")
    enfermedad_input = st.text_area("Detalles enfermedad actual", key="enfermedad_1")

    st.subheader("Antecedentes")

    antecedentes_default = """NEONATALES: PRODUCTO XX GESTACIÓN, MADRE DE XX AÑOS, CONTROLADO, SIN COMPLICACIONES, STORCH NEGATIVO Y ECOGRAFÍAS ANTENATALES: NACE VÍA VAGINAL/ CESAREA A LAS XX SEM A TÉRMINO. EGRESO CONJUNTO, PESO XXXX GR - TALLA XX CM.
INMUNOLÓGICOS: VACUNAS AL DÍA SEGÚN PAI.
ALIMENTACIÓN: ACORDE A EDAD.
PATOLÓGICOS: NIEGA.
HOSPITALARIOS: NIEGA.
FARMACOLÓGICOS: NIEGA.
TRAUMÁTICOS: NIEGA.
TOXICOLÓGICO: NIEGA EXPOSICIÓN A HUMO DE LEÑA O CIGARRILLO.
ALÉRGICOS: NIEGA.
TRANSFUSIONALES: NIEGA.
QUIRÚRGICOS: NIEGA.
FAMILIARES: PADRE SANO, MADRE SANA, NO CONSANGUÍNEOS.
HEMOCLASIFICACIÓN: O POSITIVO.
PSICOSOCIALES: VIVIENDA CON TODOS LOS SERVICIOS."""

    # 🔥 SOLO SE CARGA UNA VEZ
    if "antecedentes_1" not in st.session_state:
        st.session_state["antecedentes_1"] = antecedentes_default

    antecedentes = st.text_area(
        "Antecedentes generales",
        key="antecedentes_1",
        height=250
    )

    neuro_editable = ""
    if fecha_nacimiento:
        neuro = obtener_neurodesarrollo(años, meses)

        st.subheader("Neurodesarrollo")

        if "neuro_prev" not in st.session_state or st.session_state["neuro_prev"] != neuro:
            st.session_state["neuro_1"] = neuro
            st.session_state["neuro_prev"] = neuro

        neuro_editable = st.text_area("Neurodesarrollo", key="neuro_1", height=200)

    st.subheader("Revisión por sistemas")
    revision = st.text_area(
        "Revisión",
        value="NIEGA OTROS SINTOMAS/SIGNOS A LOS YA MENCIONADOS.",
        key="revision"
    )

    st.subheader("Signos vitales")

    col1, col2 = st.columns(2)

    with col1:
        ta = st.text_input("TA (mmHg)", key="ta")
        fc = st.number_input("FC (lpm)", min_value=0.0, key="fc")
        fr = st.number_input("FR (rpm)", min_value=0.0, key="fr")

    with col2:
        sat = st.number_input("SpO2 (%)", min_value=0.0, key="sat")
        temp = st.number_input("Temperatura (°C)", min_value=0.0, key="temp")

    peso = st.number_input("Peso (kg)", min_value=0.0, key="peso")
    talla = st.number_input("Talla (cm)", min_value=0.0, key="talla")
    pc = st.number_input("Perímetro cefálico (cm)", min_value=0.0, key="pc")

    if fecha_nacimiento and peso > 0 and talla > 0:

        edad_meses = edad_en_meses(fecha_nacimiento)
        sexo_oms = 1 if sexo == "Masculino" else 2

        imc = calcular_imc(peso, talla)

        z_pe = zscore_peso_edad(peso, edad_meses, sexo_oms)
        z_te = zscore_talla_edad(talla, edad_meses, sexo_oms)
        z_imc = zscore_imc_edad(imc, edad_meses, sexo_oms)
        z_pt = zscore_peso_talla(peso, talla, sexo_oms, edad_meses)
        z_pc = zscore_pc_edad(pc, edad_meses, sexo_oms)

        st.subheader("OMS Automático 🔥")
        st.write(f"P/E Z: {z_pe}")
        st.write(f"T/E Z: {z_te}")
        st.write(f"P/T Z: {z_pt}")
        st.write(f"IMC/E Z: {z_imc}")
        st.write(f"PC/E Z: {z_pc}")

        # 🔥 DIAGNÓSTICO NUTRICIONAL
        if edad_meses < 60:
            dx_nutricional = diagnostico_menor_5(z_pt, z_pe, z_te, z_pc)
        else:
            dx_nutricional = diagnostico_mayor_5(z_imc, z_te)

    # =========================
    # EXAMEN FÍSICO
    # =========================
    st.subheader("Examen físico")

    examen_default = """PACIENTE LUCE EN BUEN ESTADO GENERAL, ALERTA, BUEN ESTADO DE HIDRATACIÓN, AFEBRIL.

CABEZA: NORMOCÉFALA, SIN LESIONES.
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
NEUROLÓGICO: ALERTA, NO FOCALIZACIONES, SIN SIGNOS DE MENINGISMO, ROT NORMALES, FUERZA MUSCULAR CONSERVADA, SIN DÉFICIT.
PIEL: ROSADA, BIEN PERFUNDIDA, SIN LESIONES.
"""

    if "examen" not in st.session_state:
        st.session_state["examen"] = examen_default

    examen = st.text_area("Examen físico", key="examen", height=300)

    # =========================
    # ANÁLISIS
    # =========================
    if fecha_nacimiento:
        años, meses, dias = calcular_edad(fecha_nacimiento)
        edad_texto = f"{años} AÑOS" if años > 0 else f"{meses} MESES"
    else:
        edad_texto = ""

    texto_enfermedad = enfermedad_input.upper() if enfermedad_input else ""

    enfermedad_auto = f"PACIENTE {sexo.upper()} {grupo.upper()} DE {edad_texto}, QUIEN CONSULTA POR {texto_enfermedad}"

    analisis_default = f"""{enfermedad_auto}. AL INGRESO PACIENTE QUE LUCE EN ACEPTABLES CONDICIONES GENERALES, BUEN ESTADO DE HIDRATACIÓN, HEMODINÁMICAMENTE ESTABLE, BUEN PATRÓN RESPIRATORIO, SIN REQUERIMIENTO DE O2 SUPLEMENTARIO, SIN SIGNOS DE ALARMA ABDOMINAL, SIN DISTERMIAS, NO ASPECTO TÓXICO, SIN EDEMAS, SIN DÉFICIT NEUROLÓGICO, PIEL BIEN PERFUNDIDA SIN LESIONES. SE INDICA MANEJO... SE BRINDA INFORMACIÓN A FAMILIARES, SE ACLARAN DUDAS."""

    st.subheader("Análisis")
    st.session_state["analisis"] = analisis_default
    analisis = st.text_area("Análisis clínico", key="analisis", height=200)

    st.subheader("Diagnósticos")
    diagnostico = st.text_area("Diagnóstico principal", key="dx")

    plan_default = """- HOSPITALIZACION PEDIATRICA
- DIETA NORMAL ACORDE A LA EDAD
- CATETER SELLADO
- LACTATO DE RINGER A 45 CC/HORA IV
- ACETAMINOFEN SUSP 150 MG/5 ML: DAR 3 ML VO CADA 6 HORAS (SI FIEBRE O DOLOR)
- DIPIRONA: 500 MG CADA 8 HORAS IV (SI FIEBRE O DOLOR NO CEDE CON ACETAMINOFEN)
- SS PARACLINICOS DE EXTENSIÓN
- CONTROL DE LÍQUIDOS ADMINISTRADOS - ELIMINADOS
- CONTROL DE SIGNOS VITALES, AVISAR CAMBIOS."""

    # 🔥 SOLO SE CARGA UNA VEZ
    if "plan" not in st.session_state:
        st.session_state["plan"] = plan_default

    plan = st.text_area(
        "Plan",
        key="plan",
        height=200
    )

    # =========================
    # GENERAR HISTORIA
    # =========================
    if st.button("Generar Historia Clínica"):

        fecha_str = fecha_nacimiento.strftime("%d/%m/%Y") if fecha_nacimiento else ""

        historia = f"""
NOMBRE: {nombre}
DOCUMENTO: {documento}
FECHA DE NACIMIENTO: {fecha_str}
INFORMANTE: {informante}
EPS: {eps}

MOTIVO DE CONSULTA:
"{motivo}"

ENFERMEDAD ACTUAL:
{enfermedad_auto}

REVISIÓN POR SISTEMAS:
{revision}

ANTECEDENTES:
{antecedentes}

NEURODESARROLLO:
{neuro_editable}

SIGNOS VITALES:
TA {ta} mmHg FC: {fc} lpm FR: {fr} rpm SpO2: {sat}% T: {temp} °C

ANTROPOMETRÍA:
PESO: {peso} kg TALLA: {talla} cm PC: {pc} cm
P/E Z: {z_pe}
T/E Z: {z_te}
P/T Z: {z_pt}
IMC/E Z: {z_imc}
PC/E Z: {z_pc}

EXAMEN FÍSICO:
{examen}

ANÁLISIS:
{analisis}

DIAGNÓSTICOS:
{diagnostico}

DIAGNÓSTICO NUTRICIONAL:
{dx_nutricional}

PLAN:
{plan}
"""

        st.success("Historia clínica generada")
        st.text_area("Resultado final", historia.upper(), height=500)