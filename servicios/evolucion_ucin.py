import hashlib
import json
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from servicios.pediatria_urgencias import (
    complementar_analisis_con_ia,
    construir_nombre_base_docx,
    generar_docx_informe,
    guardar_docx_exportado,
    subir_docx_a_google_drive,
)


BOGOTA_TZ = ZoneInfo("America/Bogota")
PREFIX = "neo_ucin"
TITULO = "EVOLUCIÓN DEL RECIÉN NACIDO EN UCIN"
HISTORIAS_UCIN_PATH = Path(__file__).resolve().parents[1] / "data" / "historias_neonatologia_ucin.jsonl"


def _numero(texto, default=0.0):
    try:
        return float(str(texto or "").replace(",", ".").strip())
    except (TypeError, ValueError):
        return default


def _entero(texto, default=0):
    return int(round(_numero(texto, default)))


def _texto_seccion(nota, inicio, finales):
    if finales:
        patron_final = "|".join(re.escape(valor) for valor in finales)
        patron = rf"{re.escape(inicio)}\s*:?\s*(.*?)(?=\n\s*(?:{patron_final})\b|\Z)"
    else:
        patron = rf"{re.escape(inicio)}\s*:?\s*(.*)\Z"
    match = re.search(patron, nota, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _valor_regex(nota, patron, default=""):
    match = re.search(patron, nota, flags=re.IGNORECASE)
    return match.group(1).strip() if match else default


def _extraer_nota_previa(nota):
    nota = str(nota or "").replace("\u00a0", " ")
    nombre = _valor_regex(nota, r"(?:HIJA|HIJO)\s+DE\s+([^\n]+)")
    nv = _valor_regex(nota, r"\bNV\s*[:#]?\s*([A-Z0-9-]+)")
    fecha_nacimiento = _valor_regex(nota, r"\bFN\s*:\s*(\d{2}[-/]\d{2}[-/]\d{4})")
    edad = _valor_regex(nota, r"\bEDAD\s*:\s*([^\n]+)")
    peso_nacer = _entero(_valor_regex(nota, r"PESO\s+AL\s+NACER\s*:\s*([\d.,]+)"))
    peso_anterior = _entero(_valor_regex(nota, r"PESO\s+ANTERIOR\s*:\s*([\d.,]+)"))
    peso_actual = _entero(_valor_regex(nota, r"PESO\s+ACTUAL\s*:\s*([\d.,]+)"))
    soporte = _valor_regex(nota, r"SOPORTES?\s*:\s*([^\n]+)")
    balance = _texto_seccion(nota, "BALANCE HIDRICO EN 24 HORAS", ["FC", "-NEUROLÓGICO", "NEUROLÓGICO", "ANÁLISIS"])
    la = _numero(_valor_regex(balance, r"\bLA\s*[: ]\s*([\d.,]+)"))
    le = _numero(_valor_regex(balance, r"\bLE\s*[: ]\s*([\d.,]+)"))
    pi = _numero(_valor_regex(balance, r"\bPI\s*[: ]\s*([\d.,]+)"))
    gu = _numero(_valor_regex(balance, r"GASTO\s+(?:URINARIO|MIXTO)\s*:\s*([\d.,]+)"))
    signos = _valor_regex(nota, r"\bFC\s*:\s*([^\n]+)")
    diagnosticos = _texto_seccion(nota, "DIAGNÓSTICOS", ["TAMIZAJES", "ESTUDIOS", "SOPORTES"])
    tamizajes = _texto_seccion(nota, "TAMIZAJES", ["ESTUDIOS", "SOPORTES"])
    estudios = _texto_seccion(nota, "ESTUDIOS", ["SOPORTES", "BALANCE"])
    examen = _texto_seccion(nota, "-NEUROLÓGICO", ["ANÁLISIS", "PLAN"])
    if examen:
        examen = "-NEUROLÓGICO: " + examen
    analisis = _texto_seccion(nota, "ANÁLISIS", ["PLAN"])
    plan = _texto_seccion(nota, "PLAN", [])
    return {
        "nombre": nombre,
        "nv": nv,
        "fecha_nacimiento": fecha_nacimiento,
        "edad": edad,
        "peso_nacer": peso_nacer,
        "peso_anterior": peso_anterior,
        "peso_actual": peso_actual,
        "soporte": soporte,
        "la": la,
        "le": le,
        "pi": pi,
        "gu": gu,
        "signos": signos,
        "diagnosticos": diagnosticos,
        "tamizajes": tamizajes,
        "estudios": estudios,
        "examen": examen,
        "analisis": analisis,
        "plan": plan,
    }


def _peso_resumen(peso_nacer, peso_anterior, peso_actual):
    if not peso_actual:
        return "PESO ACTUAL PENDIENTE DE REGISTRO."
    partes = [f"PESO AL NACER: {peso_nacer} G." if peso_nacer else "PESO AL NACER: NO DOCUMENTADO."]
    if peso_anterior:
        diferencia = peso_actual - peso_anterior
        cambio = "GANA" if diferencia > 0 else "PIERDE" if diferencia < 0 else "SIN CAMBIOS"
        partes.append(
            f"PESO ANTERIOR: {peso_anterior} G, PESO ACTUAL: {peso_actual} G. "
            f"{cambio} {abs(diferencia)} G."
        )
    else:
        partes.append(f"PESO ACTUAL: {peso_actual} G.")
    if peso_nacer:
        diferencia_nacer = peso_actual - peso_nacer
        if diferencia_nacer < 0:
            porcentaje = abs(diferencia_nacer) * 100 / peso_nacer
            partes.append(
                f"PÉRDIDA GLOBAL DESDE EL NACIMIENTO: {abs(diferencia_nacer)} G ({porcentaje:.1f}%). "
                "AÚN NO HA RECUPERADO EL PESO AL NACER."
            )
        elif diferencia_nacer == 0:
            partes.append("RECUPERÓ EL PESO AL NACER.")
        else:
            partes.append(f"SUPERA EL PESO AL NACER EN {diferencia_nacer} G.")
    return " ".join(partes)


def _balance_texto(periodo, la, le, pi, gu):
    total_egresos = le + pi
    balance = la - total_egresos
    estado = "POSITIVO" if balance > 0 else "NEGATIVO" if balance < 0 else "NEUTRO"
    return (
        f"BALANCE HÍDRICO EN {periodo} HORAS:\n"
        f"LA: {la:.1f} ML\n"
        f"LE: {le:.1f} ML + PI: {pi:.1f} ML = TOTAL EGRESOS: {total_egresos:.1f} ML\n"
        f"BALANCE {estado}: {abs(balance):.1f} ML\n"
        f"GASTO URINARIO: {gu:.2f} ML/KG/HORA"
    )


def _analisis_local(datos):
    cambios = str(datos["cambios_examen"] or "").strip()
    soporte = str(datos["soporte"] or "").strip()
    cierre = "SE BRINDA INFORMACIÓN A PADRES O CUIDADOR RESPONSABLE SOBRE LA EVOLUCIÓN Y EL PLAN, QUIEN REFIERE ENTENDER Y ACEPTAR."
    return (
        f"RECIÉN NACIDO EN EVOLUCIÓN, CON DIAGNÓSTICOS Y ANTECEDENTES CONSIGNADOS. "
        f"{_peso_resumen(datos['peso_nacer'], datos['peso_anterior'], datos['peso_actual'])} "
        f"{_balance_texto(datos['periodo'], datos['la'], datos['le'], datos['pi'], datos['gu']).replace(chr(10), ' ')} "
        f"SOPORTE ACTUAL: {soporte or 'NO DOCUMENTADO'}. "
        f"{('SE DOCUMENTAN LOS SIGUIENTES CAMBIOS CLÍNICOS: ' + cambios + '. ') if cambios else ''}"
        f"SE CONTINÚA VIGILANCIA CLÍNICA Y SE AJUSTA LA CONDUCTA SEGÚN LA RESPUESTA, LOS HALLAZGOS DEL EXAMEN FÍSICO Y LA TOLERANCIA AL MANEJO. {cierre}"
    ).upper()


def _recalcular_balance_por_periodo():
    periodo_key = f"{PREFIX}_periodo_balance"
    anterior_key = f"{PREFIX}_periodo_balance_aplicado"
    anterior = int(st.session_state.get(anterior_key, 24) or 24)
    nuevo = int(st.session_state.get(periodo_key, 24) or 24)
    if anterior == nuevo:
        return
    factor = nuevo / anterior
    for campo in ("la", "le", "pi"):
        key = f"{PREFIX}_{campo}_balance"
        st.session_state[key] = round(_numero(st.session_state.get(key)) * factor, 1)
    st.session_state[anterior_key] = nuevo


def _cargar_previa():
    datos = _extraer_nota_previa(st.session_state.get(f"{PREFIX}_nota_previa", ""))
    for campo, valor in datos.items():
        if campo in {"la", "le", "pi", "gu"}:
            st.session_state[f"{PREFIX}_{campo}_balance"] = valor
        elif campo == "peso_nacer":
            st.session_state[f"{PREFIX}_peso_nacer"] = valor
        elif campo == "peso_anterior":
            st.session_state[f"{PREFIX}_peso_anterior"] = valor
        elif campo == "peso_actual":
            st.session_state[f"{PREFIX}_peso_actual"] = valor
        else:
            st.session_state[f"{PREFIX}_{campo}"] = valor
    st.session_state[f"{PREFIX}_periodo_balance"] = 24
    st.session_state[f"{PREFIX}_periodo_balance_aplicado"] = 24
    st.session_state[f"{PREFIX}_cambios_examen"] = ""
    st.session_state[f"{PREFIX}_cambios_soporte"] = ""
    st.session_state[f"{PREFIX}_cambios_plan"] = ""
    st.session_state[f"{PREFIX}_analisis_actualizado"] = datos.get("analisis", "")
    st.session_state[f"{PREFIX}_plan_actualizado"] = datos.get("plan", "")


def _generar_actualizacion():
    datos = {
        "peso_nacer": _entero(st.session_state.get(f"{PREFIX}_peso_nacer")),
        "peso_anterior": _entero(st.session_state.get(f"{PREFIX}_peso_anterior")),
        "peso_actual": _entero(st.session_state.get(f"{PREFIX}_peso_actual")),
        "periodo": int(st.session_state.get(f"{PREFIX}_periodo_balance", 24)),
        "la": _numero(st.session_state.get(f"{PREFIX}_la_balance")),
        "le": _numero(st.session_state.get(f"{PREFIX}_le_balance")),
        "pi": _numero(st.session_state.get(f"{PREFIX}_pi_balance")),
        "gu": _numero(st.session_state.get(f"{PREFIX}_gu_balance")),
        "soporte": st.session_state.get(f"{PREFIX}_soporte_actual", ""),
        "cambios_examen": st.session_state.get(f"{PREFIX}_cambios_examen", ""),
    }
    base = _analisis_local(datos)
    contexto = {
        "nota_previa": st.session_state.get(f"{PREFIX}_nota_previa", ""),
        "diagnosticos": st.session_state.get(f"{PREFIX}_diagnosticos", ""),
        "signos_vitales": st.session_state.get(f"{PREFIX}_signos", ""),
        "peso_actualizado": _peso_resumen(datos["peso_nacer"], datos["peso_anterior"], datos["peso_actual"]),
        "balance_actualizado": _balance_texto(datos["periodo"], datos["la"], datos["le"], datos["pi"], datos["gu"]),
        "soporte_actual": datos["soporte"],
        "cambios_examen": datos["cambios_examen"],
        "examen_fisico_actual": st.session_state.get(f"{PREFIX}_examen", ""),
        "cambios_plan": st.session_state.get(f"{PREFIX}_cambios_plan", ""),
    }
    fingerprint = hashlib.md5(json.dumps(contexto, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    instrucciones = (
        "Eres un asistente clínico neonatal que actualiza una nota de evolución de UCIN en español. "
        "Usa exclusivamente la nota previa y los datos actualizados. No inventes diagnósticos, hallazgos, tratamientos ni cifras. "
        "Redacta un solo párrafo clínico en MAYÚSCULAS. Integra obligatoriamente peso, variación frente al peso anterior, "
        "pérdida global desde el nacimiento solo si el peso actual es menor, balance hídrico del período actual, soporte, "
        "cambios de examen físico y conducta. Si no hay cambios, indícalo de forma breve. "
        "Finaliza con constancia de información brindada a padres o cuidador responsable; no uses instrucciones tipo 'EXPLICAR AL CUIDADOR'."
    )
    st.session_state[f"{PREFIX}_analisis_actualizado"] = complementar_analisis_con_ia(
        base, contexto, f"{PREFIX}_{fingerprint}", instrucciones=instrucciones, forzar=True
    )
    plan_previo = str(st.session_state.get(f"{PREFIX}_plan", "")).strip()
    cambios_plan = str(st.session_state.get(f"{PREFIX}_cambios_plan", "")).strip()
    if cambios_plan:
        plan_previo = f"{plan_previo}\n{cambios_plan}".strip()
    st.session_state[f"{PREFIX}_plan_actualizado"] = plan_previo


def _guardar_historia_ucin(datos):
    """Mantiene las evoluciones UCIN en un historial independiente de urgencias."""
    HISTORIAS_UCIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORIAS_UCIN_PATH.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(datos, ensure_ascii=False) + "\n")


def render():
    st.header(TITULO)
    st.caption("Pegue la evolución previa, actualice los datos del turno y revise la nota antes de generar el informe.")

    st.text_area("Nota evolutiva previa", key=f"{PREFIX}_nota_previa", height=300)
    if st.button("Leer y preparar actualización", key=f"{PREFIX}_leer_previa", use_container_width=True):
        _cargar_previa()
        st.rerun()

    col_fecha, col_nombre, col_nv = st.columns([1, 2, 1])
    with col_fecha:
        fecha_evolucion = st.date_input("Fecha de evolución", value=date.today(), key=f"{PREFIX}_fecha_evolucion")
    with col_nombre:
        nombre = st.text_input("Nombre del recién nacido", key=f"{PREFIX}_nombre")
    with col_nv:
        nv = st.text_input("Número de nacido vivo", key=f"{PREFIX}_nv")

    col_fn, col_edad, col_dx = st.columns([1, 1, 2])
    with col_fn:
        fn = st.text_input("Fecha de nacimiento", key=f"{PREFIX}_fecha_nacimiento", placeholder="DD-MM-AAAA")
    with col_edad:
        edad = st.text_input("Edad neonatal", key=f"{PREFIX}_edad")
    with col_dx:
        diagnosticos = st.text_area("Diagnósticos", key=f"{PREFIX}_diagnosticos", height=100)

    st.subheader("Peso y crecimiento")
    col_pn, col_pa, col_pc = st.columns(3)
    with col_pn:
        peso_nacer = st.number_input("Peso al nacer (g)", min_value=0, step=1, key=f"{PREFIX}_peso_nacer")
    with col_pa:
        peso_anterior = st.number_input("Peso anterior (g)", min_value=0, step=1, key=f"{PREFIX}_peso_anterior")
    with col_pc:
        peso_actual = st.number_input("Peso actual (g)", min_value=0, step=1, key=f"{PREFIX}_peso_actual")
    st.info(_peso_resumen(peso_nacer, peso_anterior, peso_actual))

    st.subheader("Soporte y balance hídrico")
    soporte_previo = st.text_area("Soporte registrado en la nota previa", key=f"{PREFIX}_soporte", height=70)
    cambio_soporte = st.radio(
        "¿Hubo cambios en el soporte?", ["NO", "SÍ"], horizontal=True, key=f"{PREFIX}_hubo_cambio_soporte"
    )
    cambios_soporte = st.text_area("Soporte actual o cambio realizado", key=f"{PREFIX}_cambios_soporte", height=70)
    soporte_actual = cambios_soporte.strip() if cambio_soporte == "SÍ" and cambios_soporte.strip() else soporte_previo
    st.session_state[f"{PREFIX}_soporte_actual"] = soporte_actual

    periodo = st.selectbox(
        "Período del balance hídrico", [6, 12, 24], key=f"{PREFIX}_periodo_balance", on_change=_recalcular_balance_por_periodo
    )
    col_la, col_le, col_pi, col_gu = st.columns(4)
    with col_la:
        la = st.number_input("LA (ml)", min_value=0.0, step=1.0, key=f"{PREFIX}_la_balance")
    with col_le:
        le = st.number_input("LE (ml)", min_value=0.0, step=1.0, key=f"{PREFIX}_le_balance")
    with col_pi:
        pi = st.number_input("PI (ml)", min_value=0.0, step=1.0, key=f"{PREFIX}_pi_balance")
    with col_gu:
        gu = st.number_input("Gasto urinario (ml/kg/h)", min_value=0.0, step=0.1, key=f"{PREFIX}_gu_balance")
    balance_actualizado = _balance_texto(periodo, la, le, pi, gu)
    st.text_area("Balance hídrico actualizado", value=balance_actualizado, height=150, disabled=True)

    signos = st.text_input("Signos vitales actuales", key=f"{PREFIX}_signos", placeholder="FC, FR, TA, TAM, T°, SpO2")
    tamizajes = st.text_area("Tamizajes", key=f"{PREFIX}_tamizajes", height=110)
    estudios = st.text_area("Estudios y paraclínicos", key=f"{PREFIX}_estudios", height=130)

    st.subheader("Cambios clínicos del turno")
    st.text_area("Examen físico de referencia", key=f"{PREFIX}_examen", height=230)
    cambios_examen = st.text_area(
        "Cambios en el examen físico desde la nota previa", key=f"{PREFIX}_cambios_examen", height=110,
        placeholder="SIN CAMBIOS CLÍNICOS RELEVANTES O DESCRIBA LOS HALLAZGOS NUEVOS.",
    )
    cambios_plan = st.text_area(
        "Cambios o nuevas indicaciones en el plan", key=f"{PREFIX}_cambios_plan", height=110,
        placeholder="SIN CAMBIOS EN EL PLAN O REGISTRE LAS INDICACIONES NUEVAS.",
    )
    st.text_area("Plan de referencia", key=f"{PREFIX}_plan", height=190)

    if st.button("Actualizar análisis y plan", key=f"{PREFIX}_actualizar", use_container_width=True):
        with st.spinner("Actualizando evolución neonatal..."):
            _generar_actualizacion()

    analisis = st.text_area("Análisis actualizado", key=f"{PREFIX}_analisis_actualizado", height=220)
    plan_actualizado = st.text_area("Plan actualizado", key=f"{PREFIX}_plan_actualizado", height=220)

    if st.button("Generar evolución clínica", key=f"{PREFIX}_generar", use_container_width=True):
        peso_texto = _peso_resumen(peso_nacer, peso_anterior, peso_actual)
        examen_final = st.session_state.get(f"{PREFIX}_examen", "")
        if cambios_examen.strip() and "SIN CAMBIOS" not in cambios_examen.upper():
            examen_final = f"{examen_final}\n\nCAMBIOS DURANTE EL TURNO:\n{cambios_examen}".strip()
        secciones = [
            (
                "DATOS DE IDENTIFICACIÓN",
                f"FECHA DE EVOLUCIÓN: {fecha_evolucion.strftime('%d-%m-%Y')}\n"
                f"NOMBRE: {nombre}\nNV: {nv}\nFECHA DE NACIMIENTO: {fn}\nEDAD: {edad}",
            ),
            ("DIAGNÓSTICOS", diagnosticos),
            ("TAMIZAJES", tamizajes),
            ("ESTUDIOS Y PARACLÍNICOS", estudios),
            ("SOPORTE ACTUAL", soporte_actual),
            ("PESO Y CRECIMIENTO", peso_texto),
            ("BALANCE HÍDRICO", balance_actualizado),
            ("SIGNOS VITALES", signos),
            ("EXAMEN FÍSICO", examen_final),
            ("ANÁLISIS", analisis),
            ("PLAN", plan_actualizado),
        ]
        historia = "\n\n".join(f"{titulo}\n{contenido}" for titulo, contenido in secciones if str(contenido).strip())
        docx_bytes = generar_docx_informe(TITULO, secciones)
        fecha_guardado = datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        nombre_docx = f"{construir_nombre_base_docx('UCIN', nombre=nombre, documento=nv, fecha_guardado=fecha_guardado)}.docx"
        guardar_docx_exportado(docx_bytes, nombre_docx.removesuffix('.docx'), subcarpeta=PREFIX)
        _guardar_historia_ucin({"fecha": fecha_guardado, "nombre": nombre, "documento": nv, "historia": historia, "tipo": TITULO})
        st.success("Evolución clínica generada")
        st.download_button(
            "Descargar evolución en Word", data=docx_bytes, file_name=nombre_docx,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True,
        )
        resultado_drive = subir_docx_a_google_drive(docx_bytes, nombre_docx)
        if resultado_drive.get("ok"):
            enlace = resultado_drive.get("webViewLink")
            st.success(f"HC guardada en Drive. [VER]({enlace})" if enlace else "HC guardada en Drive.")
        elif resultado_drive.get("configured"):
            st.warning(resultado_drive.get("message", "No se pudo guardar en Google Drive."))
