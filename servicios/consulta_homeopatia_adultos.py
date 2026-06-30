import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from core.calculos import calcular_edad
from servicios.pediatria_urgencias import (
    actualizar_texto_extraido,
    complementar_analisis_con_ia,
    construir_conducta_final_analisis,
    construir_conducta_sugerida_analisis,
    construir_resumen_paraclinicos_para_analisis,
    construir_resumen_signos_para_analisis,
    construir_nombre_base_docx,
    eliminar_historia_guardada,
    extraer_destinatario_informacion,
    extraer_resumen_antecedentes_para_analisis,
    extraer_resumen_examen_para_analisis,
    fusionar_analisis_editado_con_base_nueva,
    generar_docx_informe,
    generar_analisis_asistido_urgencias,
    guardar_docx_exportado,
    render_informe_html,
    subir_docx_a_google_drive,
)


BASE_DIR = Path(__file__).resolve().parent.parent
BOGOTA_TZ = ZoneInfo("America/Bogota")
HISTORY_FILENAME = "historias_homeopatia_adultos.jsonl"

ANTECEDENTES_HOMEO_ADULTOS_DEFAULT = """PATOLÓGICOS: SEGÚN REFIERE.
HOSPITALARIOS: SEGÚN REFIERE.
FARMACOLÓGICOS: SEGÚN REFIERE.
ALÉRGICOS: SEGÚN REFIERE.
QUIRÚRGICOS: SEGÚN REFIERE.
GINECO-OBSTÉTRICOS: SEGÚN CORRESPONDA.
FAMILIARES: SEGÚN REFIERE."""

REVISION_HOMEO_DEFAULT = "NEGADOS."

BIOPATOGRAFIA_DEFAULT = """DINÁMICA FAMILIAR DE ORIGEN, VÍNCULOS AFECTIVOS, EVENTOS IMPORTANTES DE VIDA, DUELOS, CAMBIOS RELEVANTES Y RASGOS CONSTITUCIONALES SEGÚN REFIERA."""

SINTOMAS_GENERALES_DEFAULT = """APETITO:
¿CÓMO ES EL APETITO? ¿AUMENTADO, DISMINUIDO, VARIABLE? ¿A QUÉ HORAS SIENTE MÁS HAMBRE?

SED:
¿TIENE MUCHA O POCA SED? ¿PREFIERE AGUA FRÍA, AL CLIMA O CALIENTE? ¿TOMA GRANDES O PEQUEÑAS CANTIDADES?

DESEOS:
¿QUÉ ALIMENTOS O BEBIDAS DESEA CON FRECUENCIA? ¿DULCE, SALADO, ÁCIDO, HIELO, LÁCTEOS, PICANTE, ETC.?

AVERSIONES:
¿QUÉ ALIMENTOS O BEBIDAS LE GENERAN RECHAZO O INTOLERANCIA?

AGRAVACIONES:
¿QUÉ SITUACIONES, HORARIOS, ALIMENTOS, CLIMAS O ACTIVIDADES AGRAVAN SUS SÍNTOMAS?

EMPEORA:
¿EN QUÉ MOMENTOS O CONDICIONES EMPEORA? MAÑANA, TARDE, NOCHE, MOVIMIENTO, REPOSO, FRÍO, CALOR, AYUNO, ESTRÉS, CICLO MENSTRUAL, ETC.?

CALOR VITAL:
¿ES CALUROSO O FRIOLENTO? ¿DESTAPA PIES? ¿BUSCA ABRIGO O VENTILACIÓN?

TRANSPIRACIÓN:
¿SUDA MUCHO O POCO? ¿EN QUÉ PARTES? ¿OLOR, MANCHAS, SUDOR NOCTURNO?

SUEÑO:
¿DUERME BIEN O MAL? ¿INSOMNIO DE INICIO, MANTENIMIENTO O DESPERTAR PRECOZ? ¿POSTURA AL DORMIR?

SUEÑOS:
¿SUEÑOS FRECUENTES, ANGUSTIANTES, REPETITIVOS, VÍVIDOS, CON CAÍDAS, AGUA, PERSECUCIÓN, TRABAJO, MUERTOS, ETC.?

SEXUALIDAD:
¿CÓMO ESTÁ EL DESEO SEXUAL? ¿CAMBIOS, DISMINUCIÓN, EXCESO, AVERSIÓN, MOLESTIAS ASOCIADAS?

ESTADO DEL TIEMPO:
¿CÓMO LE AFECTA EL CLIMA? HUMEDAD, LLUVIA, VIENTO, SOL, NUBLADO, CALOR, FRÍO, CAMBIOS DE PRESIÓN, TORMENTAS?"""

SINTOMAS_MENTALES_DEFAULT = """AFECTO Y AMOR:
¿CÓMO EXPRESA EL AFECTO? ¿NECESITA COMPAÑÍA, CONTENCIÓN, CONTACTO O PREFIERE DISTANCIA? ¿CELOS, APEGO, DEPENDENCIA, INDIFERENCIA?

VOLUNTAD Y CONDUCTA:
¿CÓMO ES SU INICIATIVA, CONSTANCIA Y CAPACIDAD DE DECISIÓN? ¿IMPULSIVIDAD, PASIVIDAD, OPOSICIÓN, TERQUEDAD, APATÍA?

ENTENDIMIENTO, INTELIGENCIA Y JUICIO:
¿CÓMO ESTÁ LA CONCENTRACIÓN, MEMORIA, CLARIDAD MENTAL, TOMA DE DECISIONES, COMPRENSIÓN Y JUICIO?

EMOCIONALES:
¿TEMORES, ANGUSTIA, ANSIEDAD, DUELos, SENSIBILIDAD, FACILIDAD PARA LLORAR, INSEGURIDAD, SOBRESALTOS?

HUMOR:
¿TRISTEZA, IRRITABILIDAD, CAMBIOS DE HUMOR, SUSCEPTIBILIDAD, EUFORIA, DESÁNIMO, TENDENCIA AL AISLAMIENTO?

GUSTOS:
¿PREFERENCIAS MARCADAS EN ACTIVIDADES, PERSONAS, RUTINAS, AMBIENTES, MÚSICA, ORDEN, LIMPIEZA, SILENCIO, TRABAJO?

CONCIENCIA MORAL:
¿CULPA, EXIGENCIA CONSIGO MISMO, PERFECCIONISMO, SENTIDO DEL DEBER, REMORDIMIENTOS, AUTOCRÍTICA?

PERSONALIDAD:
RASGOS DOMINANTES DEL CARÁCTER, MANERA DE RELACIONARSE, RESPUESTA AL CONFLICTO, MECANISMOS DE DEFENSA Y CONSTITUCIÓN MENTAL GLOBAL."""

EXAMEN_HOMEO_ADULTOS_DEFAULT = """PACIENTE EN BUEN ESTADO GENERAL, ALERTA, ORIENTADO, BUEN ESTADO DE HIDRATACIÓN.

CABEZA Y CUELLO: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
CARDIOPULMONAR: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
ABDOMEN: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
EXTREMIDADES: SIN HALLAZGOS PATOLÓGICOS EVIDENTES.
NEUROLÓGICO: SIN FOCALIZACIONES CLÍNICAS."""

PARACLINICOS_DEFAULT = "NO SE SOLICITAN."

ANALISIS_HOMEOPATICO_DEFAULT = """REALIZAR ANÁLISIS INTEGRATIVO DEL CASO DESDE EL ENFOQUE CLÍNICO Y HOMEOPÁTICO, CORRELACIONANDO TERRENO CONSTITUCIONAL, SÍNTOMAS GENERALES, SÍNTOMAS MENTALES Y RUBROS RELEVANTES."""

RUBROS_DEFAULT = """MENTE

GENERALES

PARTICULARES"""

TRATAMIENTO_DEFAULT = """HOMEOPATÍA:

ORTOMOLECULAR:

SUEROTERAPIA:

RECOMENDACIONES:

SEGUIMIENTO:"""


def _float_or_none(valor):
    texto = str(valor or "").strip().replace(",", ".")
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def _historia_path(nombre_archivo):
    return BASE_DIR / "data" / nombre_archivo


def _init_state(defaults):
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _clear_state(prefix, defaults):
    keys_to_clear = [key for key in st.session_state.keys() if key.startswith(prefix)]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
    for key, value in defaults.items():
        st.session_state[key] = value


def _load_histories(path):
    if not path.exists():
        return []
    historias = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                historias.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return list(reversed(historias))


def _save_history(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def render():
    prefix = "homeo_adult"
    titulo = "CONSULTA EXTERNA - MEDICINA ALTERNATIVA - HOMEOPATÍA ADULTOS"
    history_path = _historia_path(HISTORY_FILENAME)

    modalidad = st.selectbox(
        "Modalidad de la consulta",
        ["PRIMERA VEZ", "CITA DE CONTROL"],
        key=f"{prefix}_modalidad_consulta_selector",
    )

    defaults = {
        f"{prefix}_nombre": "",
        f"{prefix}_tipo_documento": None,
        f"{prefix}_documento": "",
        f"{prefix}_fecha_nacimiento": None,
        f"{prefix}_sexo": None,
        f"{prefix}_eps": "",
        f"{prefix}_telefono": "",
        f"{prefix}_informante": "",
        f"{prefix}_motivo": "",
        f"{prefix}_enfermedad_actual": "",
        f"{prefix}_antecedentes": ANTECEDENTES_HOMEO_ADULTOS_DEFAULT,
        f"{prefix}_revision": REVISION_HOMEO_DEFAULT,
        f"{prefix}_biopatografia": BIOPATOGRAFIA_DEFAULT,
        f"{prefix}_sintomas_generales": SINTOMAS_GENERALES_DEFAULT,
        f"{prefix}_sintomas_mentales": SINTOMAS_MENTALES_DEFAULT,
        f"{prefix}_ta": "",
        f"{prefix}_fc": "",
        f"{prefix}_fr": "",
        f"{prefix}_sat": "",
        f"{prefix}_glucometria": "",
        f"{prefix}_temp": "",
        f"{prefix}_peso": "",
        f"{prefix}_talla": "",
        f"{prefix}_imc_manual": "",
        f"{prefix}_examen": EXAMEN_HOMEO_ADULTOS_DEFAULT,
        f"{prefix}_diagnosticos": "",
        f"{prefix}_paraclinicos": PARACLINICOS_DEFAULT,
        f"{prefix}_paraclinicos_auto": "",
        f"{prefix}_paraclinicos_pdf_sig": "",
        f"{prefix}_imagenes_texto": "",
        f"{prefix}_imagenes_auto": "",
        f"{prefix}_imagenes_pdf_sig": "",
        f"{prefix}_analisis_homeopatico": ANALISIS_HOMEOPATICO_DEFAULT,
        f"{prefix}_analisis_homeopatico_base": "",
        f"{prefix}_conducta_final_analisis": "PENDIENTE DEFINIR",
        f"{prefix}_rubros": RUBROS_DEFAULT,
        f"{prefix}_tratamiento": TRATAMIENTO_DEFAULT,
        f"{prefix}_historia_consulta_id": None,
    }

    if st.session_state.pop(f"{prefix}_clear_requested", False):
        _clear_state(prefix, defaults)
        st.rerun()

    _init_state(defaults)

    st.header(titulo)
    st.info(f"Modalidad de la consulta: {modalidad}")

    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombres y apellidos", key=f"{prefix}_nombre")
    with col2:
        sexo = st.selectbox(
            "Sexo",
            ["Masculino", "Femenino"],
            index=None,
            placeholder="Seleccione sexo",
            key=f"{prefix}_sexo",
        )

    col3, col4 = st.columns(2)
    with col3:
        tipo_documento = st.selectbox(
            "Tipo de documento",
            ["CC", "CE", "PEP", "PS", "OTRO"],
            index=None,
            placeholder="Seleccione tipo de documento",
            key=f"{prefix}_tipo_documento",
        )
    with col4:
        documento = st.text_input("Documento", key=f"{prefix}_documento")

    col5, col6 = st.columns(2)
    with col5:
        fecha_nacimiento = st.date_input(
            "Fecha de nacimiento",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key=f"{prefix}_fecha_nacimiento",
        )
    with col6:
        informante = st.text_input("Informante / acompañante", key=f"{prefix}_informante")

    col7, col8 = st.columns(2)
    with col7:
        eps = st.text_input("EPS", key=f"{prefix}_eps")
    with col8:
        telefono = st.text_input("Telefono", key=f"{prefix}_telefono")

    if fecha_nacimiento:
        años, meses, dias = calcular_edad(fecha_nacimiento)
        st.info(f"Edad: {años} años, {meses} meses, {dias} días")

    st.subheader("Motivo de consulta")
    motivo = st.text_area("", key=f"{prefix}_motivo", height=90, label_visibility="collapsed")

    st.subheader("Enfermedad actual")
    st.caption("Guía sugerida: inicio, tiempo de evolución, desencadenantes, forma de presentación, localización, irradiación, intensidad, modalidades, agravantes, mejorías, tratamientos previos y estado actual.")
    enfermedad_actual = st.text_area(
        "",
        key=f"{prefix}_enfermedad_actual",
        height=220,
        label_visibility="collapsed",
    )

    st.subheader("Antecedentes personales y familiares")
    antecedentes = st.text_area("", key=f"{prefix}_antecedentes", height=220, label_visibility="collapsed")

    st.subheader("Revisión por sistemas")
    revision = st.text_area("", key=f"{prefix}_revision", height=90, label_visibility="collapsed")

    st.subheader("Resumen de biopatografía")
    st.caption("Guía sugerida: infancia, dinámica familiar, duelos, traumas, pérdidas, enfermedades previas, eventos vitales marcantes, relaciones afectivas, escolaridad/trabajo y cambios importantes de vida.")
    biopatografia = st.text_area("", key=f"{prefix}_biopatografia", height=180, label_visibility="collapsed")

    st.subheader("Síntomas generales")
    st.caption("Guía sugerida: apetito, sed, deseos, aversiones, agravaciones, empeora, calor vital, transpiración, sueño, sueños, sexualidad y estado del tiempo.")
    sintomas_generales = st.text_area("", key=f"{prefix}_sintomas_generales", height=180, label_visibility="collapsed")

    st.subheader("Síntomas mentales")
    st.caption("Guía sugerida: afecto y amor, voluntad y conducta, entendimiento/inteligencia/juicio, emocionales, humor, gustos, conciencia moral y personalidad.")
    sintomas_mentales = st.text_area("", key=f"{prefix}_sintomas_mentales", height=220, label_visibility="collapsed")

    st.subheader("Examen físico")
    col_sv1, col_sv2, col_sv3 = st.columns(3)
    with col_sv1:
        ta = st.text_input("TA (mmHg)", key=f"{prefix}_ta")
    with col_sv2:
        fc = st.text_input("FC (lpm)", key=f"{prefix}_fc")
    with col_sv3:
        sat = st.text_input("SpO2 (%)", key=f"{prefix}_sat")

    col_sv4, col_sv5, col_sv6 = st.columns(3)
    with col_sv4:
        fr = st.text_input("FR (rpm)", key=f"{prefix}_fr")
    with col_sv5:
        glucometria = st.text_input("Glucometría (mg/dl)", key=f"{prefix}_glucometria")
    with col_sv6:
        temp = st.text_input("Temperatura (°C)", key=f"{prefix}_temp")

    col_ant1, col_ant2, col_ant3 = st.columns(3)
    with col_ant1:
        peso = st.text_input("Peso (kg)", key=f"{prefix}_peso")
    with col_ant2:
        talla = st.text_input("Talla (cm)", key=f"{prefix}_talla")
    with col_ant3:
        imc_manual = st.text_input("IMC (kg/m²)", key=f"{prefix}_imc_manual")

    _ = (
        _float_or_none(fc),
        _float_or_none(fr),
        _float_or_none(sat),
        _float_or_none(glucometria),
        _float_or_none(temp),
        _float_or_none(peso),
        _float_or_none(talla),
    )

    examen = st.text_area("", key=f"{prefix}_examen", height=220, label_visibility="collapsed")

    st.subheader("Diagnósticos médicos")
    diagnosticos = st.text_area("", key=f"{prefix}_diagnosticos", height=120, label_visibility="collapsed")

    st.subheader("Exámenes paraclínicos")
    col_pdf_1, col_pdf_2 = st.columns(2)
    with col_pdf_1:
        pdf_labs = st.file_uploader(
            "Subir PDF de laboratorios",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"{prefix}_paraclinicos_pdf_v1",
        )
    with col_pdf_2:
        pdf_imgs = st.file_uploader(
            "Subir PDF de imágenes",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"{prefix}_imagenes_pdf_v1",
        )

    if pdf_labs:
        actualizar_texto_extraido(
            f"{prefix}_paraclinicos",
            f"{prefix}_paraclinicos_auto",
            f"{prefix}_paraclinicos_pdf_sig",
            pdf_labs,
            "laboratorios",
        )
    if pdf_imgs:
        actualizar_texto_extraido(
            f"{prefix}_imagenes_texto",
            f"{prefix}_imagenes_auto",
            f"{prefix}_imagenes_pdf_sig",
            pdf_imgs,
            "imagenes",
        )

    paraclinicos = st.text_area("", key=f"{prefix}_paraclinicos", height=140, label_visibility="collapsed")
    imagenes_texto = st.text_area("Imágenes", key=f"{prefix}_imagenes_texto", height=120)
    conducta_final_analisis = st.selectbox(
        "Conducta final",
        ["PENDIENTE DEFINIR", "OBSERVACIÓN", "HOSPITALIZACIÓN", "EGRESO", "REMISIÓN"],
        key=f"{prefix}_conducta_final_analisis",
    )
    permitir_generacion_analisis = conducta_final_analisis != "PENDIENTE DEFINIR"

    resumen_examen_analisis = extraer_resumen_examen_para_analisis(examen)
    resumen_antecedentes_analisis = extraer_resumen_antecedentes_para_analisis(antecedentes)
    destinatario_informacion = extraer_destinatario_informacion(informante)
    resumen_signos_analisis = construir_resumen_signos_para_analisis(
        _float_or_none(fc),
        _float_or_none(fr),
        _float_or_none(sat),
        _float_or_none(temp),
        _float_or_none(glucometria),
        _float_or_none(peso),
        "",
    )
    resumen_paraclinicos_analisis = construir_resumen_paraclinicos_para_analisis(paraclinicos)
    conducta_sugerida_analisis = construir_conducta_sugerida_analisis(
        enfermedad_actual,
        examen,
        paraclinicos,
        resumen_signos_analisis,
    )
    conducta_final_texto = construir_conducta_final_analisis(
        conducta_final_analisis,
        conducta_sugerida_analisis,
    )
    enfermedad_auto = (
        f"PACIENTE {(sexo or '').upper()} DE "
        f"{f'{años} AÑOS' if fecha_nacimiento and años > 0 else ''}, QUIEN CONSULTA POR {str(enfermedad_actual).upper()}"
    ).replace("  ", " ").strip(" ,")
    analisis_homeopatico_default = ""
    if permitir_generacion_analisis:
        analisis_homeopatico_default = generar_analisis_asistido_urgencias(
            enfermedad_auto,
            resumen_antecedentes_analisis,
            resumen_examen_analisis,
            resumen_signos_analisis,
            resumen_paraclinicos_analisis,
            conducta_final_texto,
            destinatario_informacion,
        )
        contexto_analisis_ia = {
            "titulo": titulo,
            "modalidad_consulta": modalidad,
            "motivo_consulta": motivo,
            "enfermedad_actual": enfermedad_actual,
            "antecedentes": antecedentes,
            "parentesco_acompanante": destinatario_informacion,
            "conducta_final_definida": conducta_final_analisis,
            "conducta_sugerida_local": conducta_sugerida_analisis,
            "conducta_final_texto": conducta_final_texto,
            "revision_por_sistemas": revision,
            "biopatografia": biopatografia,
            "sintomas_generales": sintomas_generales,
            "sintomas_mentales": sintomas_mentales,
            "signos_vitales": {
                "ta": ta,
                "fc": fc,
                "fr": fr,
                "spo2": sat,
                "glucometria": glucometria,
                "temperatura": temp,
                "peso": peso,
                "talla": talla,
                "imc": imc_manual,
            },
            "examen_fisico": examen,
            "diagnosticos": diagnosticos,
            "paraclinicos": paraclinicos,
            "imagenes": imagenes_texto,
            "rubros": rubros if 'rubros' in locals() else "",
        }
        fingerprint_analisis_ia = hashlib.md5(
            json.dumps(contexto_analisis_ia, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        analisis_homeopatico_default = complementar_analisis_con_ia(
            analisis_homeopatico_default,
            contexto_analisis_ia,
            fingerprint_analisis_ia,
            instrucciones=(
                "Eres un asistente clínico que redacta análisis clínico-homeopáticos en español. "
                "Usa únicamente la información entregada. No inventes diagnósticos, remedios ni hallazgos. "
                "Redacta un solo párrafo en MAYÚSCULAS, profesional y coherente, integrando motivo de consulta, "
                "antecedentes relevantes, evolución, biopatografía, síntomas generales, síntomas mentales, examen físico y paraclínicos. "
                "Debes tomar como fuente principal todo el contexto clínico ya consignado antes del análisis. "
                "Si existe una conducta final definida en el contexto, úsala como marco principal del cierre y constrúyela de forma coherente con el resto de la historia, "
                "sin contradecirla ni duplicar frases genéricas. Si la conducta final está PENDIENTE DEFINIR, no inventes una decisión final. "
                "Usa el parentesco del acompañante en el cierre si está disponible."
            ),
        )

    st.subheader("Análisis homeopático")
    if permitir_generacion_analisis and st.session_state.get(f"{prefix}_analisis_homeopatico_base") != analisis_homeopatico_default:
        if st.session_state.get(f"{prefix}_analisis_homeopatico") == st.session_state.get(
            f"{prefix}_analisis_homeopatico_base",
            "",
        ):
            st.session_state[f"{prefix}_analisis_homeopatico"] = analisis_homeopatico_default
        else:
            merge_fp = hashlib.md5(
                json.dumps(
                    {
                        "actual": st.session_state.get(f"{prefix}_analisis_homeopatico", ""),
                        "base_anterior": st.session_state.get(f"{prefix}_analisis_homeopatico_base", ""),
                        "base_nueva": analisis_homeopatico_default,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            st.session_state[f"{prefix}_analisis_homeopatico"] = fusionar_analisis_editado_con_base_nueva(
                st.session_state.get(f"{prefix}_analisis_homeopatico", ""),
                st.session_state.get(f"{prefix}_analisis_homeopatico_base", ""),
                analisis_homeopatico_default,
                merge_fp,
            )
        st.session_state[f"{prefix}_analisis_homeopatico_base"] = analisis_homeopatico_default
    analisis_homeopatico = st.text_area(
        "",
        key=f"{prefix}_analisis_homeopatico",
        height=280,
        label_visibility="collapsed",
    )

    st.subheader("Rubros importantes")
    rubros = st.text_area("", key=f"{prefix}_rubros", height=220, label_visibility="collapsed")

    st.subheader("Análisis y tratamiento")
    tratamiento = st.text_area("", key=f"{prefix}_tratamiento", height=320, label_visibility="collapsed")

    col_btn_1, col_btn_2 = st.columns(2)
    generar = col_btn_1.button("Generar Historia Clínica", key=f"{prefix}_generar", use_container_width=True)
    if col_btn_2.button("Limpiar y empezar otra historia", key=f"{prefix}_limpiar", use_container_width=True):
        st.session_state[f"{prefix}_clear_requested"] = True
        st.rerun()

    if generar:
        fecha_str = fecha_nacimiento.strftime("%d/%m/%Y") if fecha_nacimiento else ""
        antropometria = f"PESO {peso} KG TALLA {talla} CM"
        if imc_manual:
            antropometria += f" IMC {imc_manual} KG/M²"
        paraclinicos_reporte = paraclinicos.strip() if str(paraclinicos).strip() else "NO HAY LABORATORIOS POR REPORTAR"
        imagenes_reporte = imagenes_texto.strip() if str(imagenes_texto).strip() else "NO HAY IMAGENES POR REPORTAR"

        historia = f"""
{titulo.upper()}

MODALIDAD DE LA CONSULTA:
{modalidad}

DATOS DE IDENTIFICACIÓN:
NOMBRES Y APELLIDOS: {nombre}
TIPO DE DOCUMENTO: {tipo_documento}
DOCUMENTO: {documento}
FECHA DE NACIMIENTO: {fecha_str}
EPS: {eps}
TELEFONO: {telefono}
INFORMANTE / ACOMPAÑANTE: {informante}

MOTIVO DE CONSULTA:
{"\"" + str(motivo).strip() + "\"" if str(motivo).strip() else "\"NO REGISTRADO\""}

ENFERMEDAD ACTUAL (EVOLUCIÓN Y MODALIDADES):
{enfermedad_actual}

ANTECEDENTES PERSONALES Y FAMILIARES:
{antecedentes}

REVISIÓN POR SISTEMAS:
{revision}

RESUMEN DE BIOPATOGRAFÍA:
{biopatografia}

SÍNTOMAS GENERALES:
{sintomas_generales}

SÍNTOMAS MENTALES:
{sintomas_mentales}

EXAMEN FÍSICO:
TA {ta or "NO EVALUADO"} mmHg FC {fc or "NO EVALUADO"} lpm SpO2 {sat or "NO EVALUADO"}% FR {fr or "NO EVALUADO"} rpm GLUCOMETRÍA {glucometria or "NO EVALUADO"} mg/dl T {temp or "NO EVALUADO"} °C
{antropometria}
{examen}
DIAGNÓSTICOS MÉDICOS:
{diagnosticos}

EXÁMENES PARACLÍNICOS:
{paraclinicos_reporte}

IMÁGENES:
{imagenes_reporte}

ANÁLISIS HOMEOPÁTICO:
{analisis_homeopatico}

RUBROS IMPORTANTES:
{rubros}

ANÁLISIS Y TRATAMIENTO:
{tratamiento}
""".strip()

        secciones = [
            ("MODALIDAD DE LA CONSULTA", modalidad),
            (
                "DATOS DE IDENTIFICACIÓN",
                f"NOMBRES Y APELLIDOS: {nombre}\nTIPO DE DOCUMENTO: {tipo_documento}\nDOCUMENTO: {documento}\nFECHA DE NACIMIENTO: {fecha_str}\nEPS: {eps}\nTELEFONO: {telefono}\nINFORMANTE / ACOMPAÑANTE: {informante}",
            ),
            ("MOTIVO DE CONSULTA", f'"{motivo}"' if str(motivo).strip() else '"NO REGISTRADO"'),
            ("ENFERMEDAD ACTUAL (EVOLUCIÓN Y MODALIDADES)", enfermedad_actual),
            ("ANTECEDENTES PERSONALES Y FAMILIARES", antecedentes),
            ("REVISIÓN POR SISTEMAS", revision),
            ("RESUMEN DE BIOPATOGRAFÍA", biopatografia),
            ("SÍNTOMAS GENERALES", sintomas_generales),
            ("SÍNTOMAS MENTALES", sintomas_mentales),
            (
                "EXAMEN FÍSICO",
                f"TA {ta or 'NO EVALUADO'} mmHg FC {fc or 'NO EVALUADO'} lpm SpO2 {sat or 'NO EVALUADO'}% FR {fr or 'NO EVALUADO'} rpm GLUCOMETRÍA {glucometria or 'NO EVALUADO'} mg/dl T {temp or 'NO EVALUADO'} °C\n{antropometria}\n{examen}",
            ),
            ("DIAGNÓSTICOS MÉDICOS", diagnosticos),
            ("EXÁMENES PARACLÍNICOS", paraclinicos_reporte),
            ("IMÁGENES", imagenes_reporte),
            ("ANÁLISIS HOMEOPÁTICO", analisis_homeopatico),
            ("RUBROS IMPORTANTES", rubros),
            ("ANÁLISIS Y TRATAMIENTO", tratamiento),
        ]

        st.success("Historia clínica generada")
        fecha_guardado = datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        docx_bytes = generar_docx_informe(titulo.upper(), secciones)
        nombre_base_docx = construir_nombre_base_docx(
            "CE",
            nombre=nombre,
            documento=documento,
            fecha_guardado=fecha_guardado,
        )
        ruta_docx_guardado = guardar_docx_exportado(
            docx_bytes,
            nombre_base_docx,
            subcarpeta=prefix,
        )
        nombre_docx = f"{nombre_base_docx}.docx"
        st.download_button(
            "Descargar informe en Word",
            data=docx_bytes,
            file_name=nombre_docx,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"{prefix}_download_docx",
        )
        resultado_drive = subir_docx_a_google_drive(docx_bytes, nombre_docx)
        if resultado_drive.get("ok"):
            enlace_drive = resultado_drive.get("webViewLink")
            if enlace_drive:
                st.success(f"HC guardada en Drive. [VER]({enlace_drive})")
            else:
                st.success("HC guardada en Drive.")
        elif resultado_drive.get("configured"):
            st.warning(resultado_drive.get("message", "No se pudo guardar en Google Drive."))
        else:
            st.info("Google Drive no está configurado aún. El Word sí quedó disponible para descarga.")

        identificador = f"{fecha_guardado} | {nombre or 'SIN NOMBRE'} | {documento or 'SIN DOCUMENTO'}"
        _save_history(
            history_path,
            {
                "id": identificador,
                "fecha_guardado": fecha_guardado,
                "nombre": nombre,
                "documento": documento,
                "historia": historia.upper(),
                "docx_local_path": str(ruta_docx_guardado),
                "drive_file_id": resultado_drive.get("file_id"),
                "drive_webview_link": resultado_drive.get("webViewLink"),
            },
        )
        render_informe_html(titulo.upper(), secciones, historia.upper())

    st.divider()
    with st.expander("Historias guardadas", expanded=False):
        historias_guardadas = _load_histories(history_path)
        if historias_guardadas:
            opciones = [h["id"] for h in historias_guardadas]
            historia_consulta_id = st.selectbox(
                "Consultar historia previa",
                opciones,
                key=f"{prefix}_historia_consulta_id",
            )
            historia_sel = next((h for h in historias_guardadas if h["id"] == historia_consulta_id), None)
            if historia_sel:
                st.text_area(
                    "Informe guardado",
                    historia_sel["historia"],
                    height=500,
                    key=f"{prefix}_historia_guardada_texto",
                )
                if st.button("Eliminar esta historia", key=f"{prefix}_eliminar_historia", use_container_width=True):
                    resultado_eliminacion = eliminar_historia_guardada(history_path, historia_consulta_id)
                    if resultado_eliminacion.get("ok"):
                        st.success("Historia eliminada correctamente.")
                        st.rerun()
                    else:
                        st.warning(resultado_eliminacion.get("message", "No se pudo eliminar la historia."))
        else:
            st.info("Aún no hay historias guardadas.")
