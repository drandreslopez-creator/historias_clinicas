import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date
from datetime import datetime
from zoneinfo import ZoneInfo
import unicodedata
import json
import re
from html import escape
from pathlib import Path
from difflib import SequenceMatcher
from deep_translator import GoogleTranslator

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


BASE_DIR = Path(__file__).resolve().parent.parent
HISTORIAS_PATH = BASE_DIR / "data" / "historias_pediatria_urgencias.jsonl"
BOGOTA_TZ = ZoneInfo("America/Bogota")

ANTECEDENTES_DEFAULT = """NEONATALES: PRODUCTO XX GESTACIÓN, MADRE DE XX AÑOS, CONTROLADO, SIN COMPLICACIONES, STORCH NEGATIVO Y ECOGRAFÍAS ANTENATALES: NACE VÍA VAGINAL/ CESAREA A LAS XX SEM A TÉRMINO. EGRESO CONJUNTO, PESO XXXX GR - TALLA XX CM.
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

EXAMEN_DEFAULT = """PACIENTE LUCE EN BUEN ESTADO GENERAL, ALERTA, BUEN ESTADO DE HIDRATACIÓN, AFEBRIL.

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

PLAN_DEFAULT = """- HOSPITALIZACION PEDIATRICA
- DIETA NORMAL ACORDE A LA EDAD
- CATETER SELLADO
- LACTATO DE RINGER A 45 CC/HORA IV
- ACETAMINOFEN SUSP 150 MG/5 ML: DAR 3 ML VO CADA 6 HORAS (SI FIEBRE O DOLOR)
- DIPIRONA: 500 MG CADA 8 HORAS IV (SI FIEBRE O DOLOR NO CEDE CON ACETAMINOFEN)
- SS PARACLINICOS DE EXTENSIÓN
- CONTROL DE LÍQUIDOS ADMINISTRADOS - ELIMINADOS
- CONTROL DE SIGNOS VITALES, AVISAR CAMBIOS."""

REVISION_DEFAULT = "NIEGA OTROS SINTOMAS/SIGNOS A LOS YA MENCIONADOS."

FORM_DEFAULTS = {
    "nombre_1": "",
    "tipo_documento_1": None,
    "documento_1": "",
    "fecha_1": None,
    "sexo_1": None,
    "eps_1": "",
    "informante_1": "",
    "proveniente_1": "",
    "motivo_1": "",
    "enfermedad_1": "",
    "antecedentes_1": ANTECEDENTES_DEFAULT,
    "neuro_1": "",
    "neuro_prev": None,
    "revision": REVISION_DEFAULT,
    "ta": "",
    "fc": 0.0,
    "fr": 0.0,
    "sat": 0.0,
    "temp": 0.0,
    "peso": 0.0,
    "talla": 0.0,
    "pc": 0.0,
    "examen": EXAMEN_DEFAULT,
    "analisis": "",
    "analisis_base": "",
    "busqueda_cie10": "",
    "dx_cie10": None,
    "obs_dx": "",
    "plan": PLAN_DEFAULT,
}

EQUIVALENCIAS_BUSQUEDA = {
    "asma": "asthma",
    "agud": "acute",
    "aguda": "acute",
    "agudo": "acute",
    "infec": "infection",
    "infec": "infection",
    "infect": "infection",
    "vias": "tract",
    "via": "tract",
    "resp": "respiratory",
    "bonquioli": "bronchiolitis",
    "bronquioli": "bronchiolitis",
    "bronquiolit": "bronchiolitis",
    "bronquiol": "bronchiolitis",
    "bronquit": "bronchitis",
    "nasofarin": "nasopharyngitis",
    "nasofaring": "nasopharyngitis",
    "nasofar": "nasopharyngitis",
    "rinofarin": "rhinopharyngitis",
    "rinofaring": "rhinopharyngitis",
    "faring": "pharyngitis",
    "faringo": "pharyngitis",
    "amigdal": "tonsillitis",
    "adenoid": "adenoid",
    "laring": "laryngitis",
    "traque": "tracheitis",
    "neumon": "pneumonia",
    "otit": "otitis",
    "sinus": "sinusitis",
    "gastroenter": "gastroenteritis",
    "diarre": "diarrhoea",
    "vomit": "vomiting",
    "apendic": "appendicitis",
    "celulit": "cellulitis",
    "dermatit": "dermatitis",
    "urin": "urinary",
    "cistit": "cystitis",
    "pielon": "pyelonephritis",
    "convuls": "convulsion",
    "cuerpo": "body",
    "extran": "foreign",
    "extra": "foreign",
    "esof": "oesoph",
    "esofag": "oesophag",
    "esofago": "oesophagus",
    "esofagu": "oesophag",
    "estomac": "stomach",
    "intestin": "intestin",
    "gargant": "throat",
    "oido": "ear",
    "pulmon": "lung",
}

ALIAS_DESCRIPCION = {
    "acute": "agudo aguda agud",
    "chronic": "cronico cronica cron",
    "infection": "infeccion infec infect",
    "infections": "infeccion infecciones infec infect",
    "infective": "infeccioso infecciosa infect",
    "inflammatory": "inflamatorio inflamatoria inflama",
    "respiratory": "respiratorio respiratoria resp",
    "upper": "superior alta altas sup",
    "lower": "inferior inferiores baja bajas inf",
    "tract": "via vias tracto",
    "multiple": "multiple multiples",
    "unspecified": "no especificado no especificada inespecifico inespecifica",
    "body": "cuerpo",
    "foreign": "extrano extra",
    "oesophagus": "esofago esofag esof",
    "oesophageal": "esofagico esofag",
    "esophagus": "esofago esofag esof",
    "nasopharyngitis": "nasofaringitis nasofarin nasofaring nasofar",
    "nasopharyngeal": "nasofaringea nasofaringeo nasofar",
    "pharyngitis": "faringitis faringo faring",
    "tonsillitis": "amigdalitis amigdal",
    "laryngitis": "laringitis laring",
    "tracheitis": "traqueitis traque",
    "bronchiolitis": "bronquiolitis bonquioli bronquioli bronquiolit bronquiol",
    "bronchitis": "bronquitis bronquit",
    "pneumonia": "neumonia neumon",
    "otitis": "otitis otit oido",
    "sinusitis": "sinusitis sinus",
    "gastroenteritis": "gastroenteritis gastroenter",
    "appendicitis": "apendicitis apendic",
    "diarrhoea": "diarrea diarre",
    "urinary": "urinario urinaria urin",
    "cystitis": "cistitis cistit",
    "pyelonephritis": "pielonefritis pielon",
    "convulsion": "convulsion convuls",
}


@st.cache_data
def cargar_cie10():
    df = pd.read_csv("data/cie10_who.csv")
    df["label_normalized"] = df["label"].map(normalizar_texto)
    df["description_normalized"] = df["description"].astype(str).map(normalizar_texto)
    df["code_normalized"] = df["code"].astype(str).map(normalizar_texto)
    df["search_text"] = df.apply(
        lambda row: construir_texto_busqueda(
            row["code_normalized"],
            row["description_normalized"],
            row["label_normalized"]
        ),
        axis=1
    )
    df["search_tokens"] = df["search_text"].map(tokenizar_texto)
    return df

def normalizar_texto(texto):
    texto = "" if texto is None else str(texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.lower().strip()


def tokenizar_texto(texto):
    return [t for t in re.split(r"[^a-z0-9]+", normalizar_texto(texto)) if t]


def construir_texto_busqueda(code, description, label):
    partes = [code, description, label]
    for termino, alias in ALIAS_DESCRIPCION.items():
        if termino in description:
            partes.append(alias)
    return " ".join(partes)


@st.cache_data(show_spinner=False)
def traducir_cie10_descripcion(descripcion):
    try:
        return GoogleTranslator(source="en", target="es").translate(str(descripcion))
    except Exception:
        return str(descripcion)


@st.cache_data(show_spinner=False)
def traducir_texto_a_ingles(texto):
    try:
        return GoogleTranslator(source="es", target="en").translate(str(texto))
    except Exception:
        return str(texto)


def expandir_terminos_busqueda(texto):
    termino = normalizar_texto(texto)
    terminos = {termino} if termino else set()
    encontro_equivalencia = False

    for origen, destino in sorted(EQUIVALENCIAS_BUSQUEDA.items(), key=lambda item: len(item[0]), reverse=True):
        if origen in termino:
            encontro_equivalencia = True
            terminos.add(destino)
            break

    if len(termino) >= 5 and not encontro_equivalencia:
        traduccion = normalizar_texto(traducir_texto_a_ingles(texto))
        if traduccion:
            terminos.add(traduccion)

    return {t for t in terminos if t}


def construir_grupos_busqueda(texto):
    texto_normalizado = normalizar_texto(texto)
    if "%" in texto_normalizado:
        partes = [p for p in texto_normalizado.split("%") if normalizar_texto(p)]
    else:
        partes = [p for p in texto_normalizado.split() if normalizar_texto(p)]

    if len(partes) <= 1:
        return []

    if not partes:
        return []

    grupos = []
    tiene_vias = any(parte.startswith("via") or parte.startswith("vias") for parte in partes)

    for parte in partes:
        opciones = set(expandir_terminos_busqueda(parte))
        if tiene_vias and (parte == "via" or parte == "vias"):
            opciones.update({"tract", "respiratory", "airway", "airways"})
        if tiene_vias and parte == "inf":
            opciones = {"inferior", "inferiores", "lower", "baja", "bajas"}
        if tiene_vias and parte == "sup":
            opciones = {"superior", "superiores", "upper", "alta", "altas"}
        grupos.append(list(opciones))

    return grupos


def aplanar_grupos_busqueda(grupos):
    terminos = []
    for grupo in grupos:
        for termino in grupo:
            if termino and termino not in terminos:
                terminos.append(termino)
    return terminos


def coincide_termino(term, row):
    if not term:
        return False

    code = row["code_normalized"]
    search_text = row["search_text"]
    search_tokens = row["search_tokens"]

    if code.startswith(term):
        return True

    if len(term) <= 3:
        return any(token.startswith(term) for token in search_tokens)

    return term in search_text or any(token.startswith(term) for token in search_tokens)


def coincide_grupos(row, grupos):
    if not grupos:
        return True

    return all(
        any(coincide_termino(opcion, row) for opcion in opciones_fragmento)
        for opciones_fragmento in grupos
        if opciones_fragmento
    )


def puntuar_diagnostico(row, terminos, grupos=None):
    score = 0
    code = row["code_normalized"]
    desc = row["description_normalized"]
    label = row["label_normalized"]
    search_tokens = row["search_tokens"]

    for termino in terminos:
        if code.startswith(termino):
            score = max(score, 100)
        elif desc.startswith(termino):
            score = max(score, 95)
        elif f" {termino}" in desc or desc == termino:
            score = max(score, 92)
        elif any(token.startswith(termino) for token in search_tokens):
            score = max(score, 90)
        elif termino in desc:
            score = max(score, 85)
        elif termino in label:
            score = max(score, 75)
        else:
            similitud = max(
                SequenceMatcher(None, termino, code).ratio(),
                SequenceMatcher(None, termino, desc[: max(len(termino) + 8, 12)]).ratio(),
            )
            if similitud >= 0.72:
                score = max(score, int(similitud * 100))

    if grupos:
        if coincide_grupos(row, grupos):
            score = max(score, 120 + len(grupos))

    return score


def limpiar_formulario():
    for key, value in FORM_DEFAULTS.items():
        st.session_state[key] = value


def solicitar_limpieza_formulario():
    st.session_state["_limpiar_formulario"] = True


def guardar_historia(datos):
    HISTORIAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORIAS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(datos, ensure_ascii=False) + "\n")


def texto_a_html(texto):
    if not texto:
        return ""
    return "<br>".join(escape(str(texto)).splitlines())


def render_informe_html(titulo, secciones, texto_copiar):
    bloques = []
    for encabezado, contenido in secciones:
        bloques.append(
            f"""
            <div style="margin-top:18px;">
                <div style="font-weight:700; margin-bottom:8px;">{escape(encabezado)}</div>
                <div style="line-height:1.55;">{texto_a_html(contenido)}</div>
            </div>
            """
        )

    html = f"""
    <div style="border:1px solid rgba(250,250,250,.12); border-radius:14px; padding:18px 20px; background:#171923; color:#f5f5f5; font-family:Arial, sans-serif;">
        <div style="display:flex; justify-content:flex-end; margin-bottom:8px;">
            <button
                onclick='navigator.clipboard.writeText({json.dumps(texto_copiar)})'
                style="background:#2b6cb0; color:white; border:none; border-radius:8px; padding:8px 12px; cursor:pointer; font-size:14px;"
            >
                Copiar informe
            </button>
        </div>
        <div style="font-size:24px; font-weight:800; text-align:center; margin-bottom:18px;">{escape(titulo)}</div>
        {''.join(bloques)}
    </div>
    """
    components.html(html, height=1200, scrolling=True)


def cargar_historias_guardadas():
    if not HISTORIAS_PATH.exists():
        return []

    historias = []
    with HISTORIAS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                historias.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return list(reversed(historias))


def render():
    if st.session_state.pop("_limpiar_formulario", False):
        limpiar_formulario()
        st.rerun()

    for key, value in FORM_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

    titulo_historia = st.session_state.get(
        "tipo_historia_clinica_ped_urg",
        "HISTORIA CLINICA DE INGRESO A URGENCIAS PEDIATRICAS"
    )

    st.header(f"📌 {titulo_historia}")

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombres y apellidos", key="nombre_1")
        tipo_documento = st.selectbox(
            "Tipo de documento",
            ["NV", "RC", "TI", "PEP", "PS", "OTRO"],
            index=None,
            placeholder="Seleccione tipo de documento",
            key="tipo_documento_1"
        )
        fecha_nacimiento = st.date_input(
            "Fecha de nacimiento",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key="fecha_1"
        )
        eps = st.text_input("EPS", key="eps_1")

    with col2:
        sexo = st.selectbox(
            "Sexo",
            ["Masculino", "Femenino"],
            index=None,
            placeholder="Seleccione sexo",
            key="sexo_1"
        )
        documento = st.text_input("Documento", key="documento_1")
        informante = st.text_input("Informante (parentesco - edad - ocupacion)", key="informante_1")
        proveniente = st.text_input("Proveniente", key="proveniente_1")

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
    sexo_texto_analisis = sexo.upper() if sexo else ""

    enfermedad_auto = f"PACIENTE {sexo_texto_analisis} {grupo.upper()} DE {edad_texto}, QUIEN CONSULTA POR {texto_enfermedad}"

    analisis_default = f"""{enfermedad_auto}. AL INGRESO PACIENTE QUE LUCE EN ACEPTABLES CONDICIONES GENERALES, BUEN ESTADO DE HIDRATACIÓN, HEMODINÁMICAMENTE ESTABLE, BUEN PATRÓN RESPIRATORIO, SIN REQUERIMIENTO DE O2 SUPLEMENTARIO, SIN SIGNOS DE ALARMA ABDOMINAL, SIN DISTERMIAS, NO ASPECTO TÓXICO, SIN EDEMAS, SIN DÉFICIT NEUROLÓGICO, PIEL BIEN PERFUNDIDA SIN LESIONES. SE INDICA MANEJO... SE BRINDA INFORMACIÓN A FAMILIARES, SE ACLARAN DUDAS."""

    st.subheader("Análisis")

    # Carga el análisis por defecto una sola vez y solo lo refresca si el
    # contenido previo seguía siendo el automático.
    if "analisis" not in st.session_state:
        st.session_state["analisis"] = analisis_default
        st.session_state["analisis_base"] = analisis_default
    elif st.session_state.get("analisis_base") != analisis_default:
        if st.session_state.get("analisis") == st.session_state.get("analisis_base"):
            st.session_state["analisis"] = analisis_default
        st.session_state["analisis_base"] = analisis_default

    analisis = st.text_area("Análisis clínico", key="analisis", height=200)

    st.subheader("Diagnósticos")
    clasificacion_diagnostica = "CIE-10"
    cie10 = cargar_cie10()
    busqueda_cie10 = st.text_input(
        "Buscar CIE-10 por código o descripción",
        key="busqueda_cie10"
    ).strip()

    if busqueda_cie10:
        grupos_busqueda = construir_grupos_busqueda(busqueda_cie10)
        if grupos_busqueda:
            terminos = aplanar_grupos_busqueda(grupos_busqueda)
        else:
            terminos = list(expandir_terminos_busqueda(busqueda_cie10))

        cie10_filtrado = cie10.copy()
        if grupos_busqueda:
            cie10_filtrado_estricto = cie10_filtrado[
                cie10_filtrado.apply(lambda row: coincide_grupos(row, grupos_busqueda), axis=1)
            ]
            if not cie10_filtrado_estricto.empty:
                cie10_filtrado = cie10_filtrado_estricto
        if cie10_filtrado.empty:
            cie10_filtrado = cie10.iloc[0:0].copy()
        else:
            cie10_filtrado["score_busqueda"] = cie10_filtrado.apply(
                lambda row: puntuar_diagnostico(row, terminos, grupos_busqueda),
                axis=1
            )
            cie10_filtrado = cie10_filtrado[cie10_filtrado["score_busqueda"] > 0]
            cie10_filtrado = cie10_filtrado.sort_values(
                by=["score_busqueda", "code_normalized"],
                ascending=[False, True]
            ).head(20)
    else:
        cie10_filtrado = cie10.iloc[0:0]

    if cie10_filtrado.empty:
        if busqueda_cie10:
            st.caption("No se encontraron diagnósticos CIE-10 con esa búsqueda.")
        diagnostico_seleccionado = ""
    else:
        cie10_filtrado = cie10_filtrado.copy()
        cie10_filtrado["description_es"] = cie10_filtrado["description"].map(traducir_cie10_descripcion)
        cie10_filtrado["label_es"] = cie10_filtrado["code"].astype(str) + " - " + cie10_filtrado["description_es"]
        with st.expander(f"Resultados de diagnóstico ({len(cie10_filtrado)})", expanded=False):
            diagnostico_seleccionado = st.selectbox(
                "Diagnóstico CIE-10",
                cie10_filtrado["label_es"].tolist(),
                index=None,
                placeholder="Seleccione un diagnóstico",
                key="dx_cie10"
            )

    observacion_diagnostico = st.text_area(
        "Observación diagnóstica",
        key="obs_dx",
        height=100
    )

    plan = st.text_area(
        "Plan",
        key="plan",
        height=200
    )

    # =========================
    # GENERAR / LIMPIAR
    # =========================
    col_btn_1, col_btn_2 = st.columns(2)
    generar_historia = col_btn_1.button("Generar Historia Clínica", use_container_width=True)
    col_btn_2.button(
        "Limpiar y empezar otra historia",
        use_container_width=True,
        on_click=solicitar_limpieza_formulario
    )

    if generar_historia:

        fecha_str = fecha_nacimiento.strftime("%d/%m/%Y") if fecha_nacimiento else ""
        diagnostico_final = diagnostico_seleccionado or ""

        historia = f"""
{titulo_historia.upper()}

DATOS DE IDENTIFICACIÓN:

NOMBRE: {nombre}
TIPO DE DOCUMENTO: {tipo_documento}
DOCUMENTO: {documento}
FECHA DE NACIMIENTO: {fecha_str}
INFORMANTE: {informante}
EPS: {eps}
PROVENIENTE: {proveniente}

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

CLASIFICACIÓN DIAGNÓSTICA:
{clasificacion_diagnostica}

DIAGNÓSTICOS:
{diagnostico_final}

OBSERVACIÓN DIAGNÓSTICA:
{observacion_diagnostico}

DIAGNÓSTICO NUTRICIONAL:
{dx_nutricional}

PLAN:
{plan}
"""

        fecha_guardado = datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        identificador = f"{fecha_guardado} | {nombre or 'SIN NOMBRE'} | {documento or 'SIN DOCUMENTO'}"

        guardar_historia({
            "id": identificador,
            "fecha_guardado": fecha_guardado,
            "nombre": nombre,
            "tipo_documento": tipo_documento,
            "documento": documento,
            "historia": historia.upper()
        })

        st.success("Historia clínica generada")
        secciones_informe = [
            ("DATOS DE IDENTIFICACIÓN", f"NOMBRES Y APELLIDOS: {nombre}\nTIPO DE DOCUMENTO: {tipo_documento}\nDOCUMENTO: {documento}\nFECHA DE NACIMIENTO: {fecha_str}\nINFORMANTE: {informante}\nEPS: {eps}\nPROVENIENTE: {proveniente}"),
            ("MOTIVO DE CONSULTA", motivo),
            ("ENFERMEDAD ACTUAL", enfermedad_auto),
            ("REVISIÓN POR SISTEMAS", revision),
            ("ANTECEDENTES", antecedentes),
            ("NEURODESARROLLO", neuro_editable),
            ("SIGNOS VITALES", f"TA {ta} mmHg FC: {fc} lpm FR: {fr} rpm SpO2: {sat}% T: {temp} °C"),
            ("ANTROPOMETRÍA", f"PESO: {peso} kg TALLA: {talla} cm PC: {pc} cm\nP/E Z: {z_pe}\nT/E Z: {z_te}\nP/T Z: {z_pt}\nIMC/E Z: {z_imc}\nPC/E Z: {z_pc}"),
            ("EXAMEN FÍSICO", examen),
            ("ANÁLISIS", analisis),
            ("CLASIFICACIÓN DIAGNÓSTICA", clasificacion_diagnostica),
            ("DIAGNÓSTICOS", diagnostico_final),
            ("OBSERVACIÓN DIAGNÓSTICA", observacion_diagnostico),
            ("DIAGNÓSTICO NUTRICIONAL", dx_nutricional),
            ("PLAN", plan),
        ]
        render_informe_html(titulo_historia.upper(), secciones_informe, historia.upper())

    st.divider()
    with st.expander("Historias guardadas", expanded=False):
        historias_guardadas = cargar_historias_guardadas()

        if historias_guardadas:
            opciones_historias = [h["id"] for h in historias_guardadas]
            historia_consulta_id = st.selectbox(
                "Consultar historia previa",
                opciones_historias,
                key="historia_consulta_id"
            )

            historia_seleccionada = next(
                (h for h in historias_guardadas if h["id"] == historia_consulta_id),
                None
            )

            if historia_seleccionada:
                st.text_area(
                    "Informe guardado",
                    historia_seleccionada["historia"],
                    height=500,
                    key="historia_guardada_texto"
                )
        else:
            st.info("Aún no hay historias guardadas.")
