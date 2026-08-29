import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from servicios.pediatria_urgencias import (
    construir_nombre_base_docx,
    extraer_texto_respuesta_openai,
    generar_docx_informe,
    guardar_docx_exportado,
    ia_analisis_configurada,
    obtener_secret_app,
    solicitar_respuesta_openai,
    subir_docx_a_google_drive,
)


BOGOTA_TZ = ZoneInfo("America/Bogota")
PREFIX = "neo_ucin"
TITULO = "EVOLUCIÓN DEL RECIÉN NACIDO EN UCIN"
HISTORIAS_UCIN_PATH = Path(__file__).resolve().parents[1] / "data" / "historias_neonatologia_ucin.jsonl"


def _numero(valor, default=0.0):
    try:
        return float(str(valor or "").replace(",", ".").strip())
    except (TypeError, ValueError):
        return default


def _entero(valor, default=0):
    return int(round(_numero(valor, default)))


def _buscar(nota, patron, default=""):
    coincidencia = re.search(patron, nota, flags=re.IGNORECASE)
    return coincidencia.group(1).strip() if coincidencia else default


def _peso_texto(peso_nacer, peso_previo, peso_actual):
    if not peso_actual:
        return ""
    partes = []
    if peso_previo:
        cambio = peso_actual - peso_previo
        accion = "GANA" if cambio > 0 else "PIERDE" if cambio < 0 else "SIN CAMBIOS"
        partes.append(f"PESO ANTERIOR: {peso_previo} G, PESO ACTUAL: {peso_actual} G. {accion} {abs(cambio)} G.")
    if peso_nacer and peso_actual < peso_nacer:
        perdida = peso_nacer - peso_actual
        partes.append(
            f"PÉRDIDA GLOBAL DESDE EL NACIMIENTO: {perdida} G ({perdida * 100 / peso_nacer:.1f}%). "
            "AÚN NO HA RECUPERADO EL PESO AL NACER."
        )
    elif peso_nacer and peso_actual >= peso_nacer:
        partes.append(f"SUPERA EL PESO AL NACER EN {peso_actual - peso_nacer} G.")
    return " ".join(partes)


def _actualizar_balance(nota, periodo):
    patron = re.compile(
        r"BALANCE\s+H[IÍ]DRICO\s+EN\s+(\d+)\s+HORAS\s*:\s*(.*?)(?=\n\s*(?:FC\s*:|-?NEUROL[ÓO]GICO|AN[ÁA]LISIS|PLAN)\b|\Z)",
        flags=re.IGNORECASE | re.DOTALL,
    )
    coincidencia = patron.search(nota)
    if not coincidencia:
        return nota
    periodo_previo = _entero(coincidencia.group(1), 24) or 24
    contenido = coincidencia.group(2)
    factor = periodo / periodo_previo

    def escalar(patron_valor):
        encontrado = re.search(patron_valor, contenido, flags=re.IGNORECASE)
        return _numero(encontrado.group(1)) * factor if encontrado else None

    la = escalar(r"\bLA\s*[: ]\s*([\d.,]+)")
    le = escalar(r"\bLE\s*[: ]\s*([\d.,]+)")
    pi = escalar(r"\bPI\s*[: ]\s*([\d.,]+)")
    gu = escalar(r"GASTO\s+(?:URINARIO|MIXTO)\s*:\s*([\d.,]+)")
    if la is None and le is None and pi is None and gu is None:
        return nota

    la = la or 0
    le = le or 0
    pi = pi or 0
    total_egresos = le + pi
    balance = la - total_egresos
    estado = "POSITIVO" if balance > 0 else "NEGATIVO" if balance < 0 else "NEUTRO"
    nuevo = (
        f"BALANCE HÍDRICO EN {periodo} HORAS:\n"
        f"LA {la:.1f} ML\n"
        f"LE {le:.1f} ML + PI {pi:.1f} ML. TOTAL EGRESOS: {total_egresos:.1f} ML\n"
        f"BALANCE {estado}: {abs(balance):.1f} ML\n"
        f"GASTO URINARIO: {(gu or 0):.2f} ML/KG/HORA"
    )
    return nota[:coincidencia.start()] + nuevo + nota[coincidencia.end():]


def _actualizar_nota_local(nota, edad_dia, peso_dia, periodo):
    nota = str(nota or "").replace("\u00a0", " ").strip()
    peso_nacer = _entero(_buscar(nota, r"PESO\s+AL\s+NACER\s*:\s*([\d.,]+)"))
    peso_previo = _entero(_buscar(nota, r"PESO\s+ANTERIOR\s*:\s*([\d.,]+)"))
    peso_previo = peso_previo or _entero(_buscar(nota, r"PESO\s+ACTUAL\s*:\s*([\d.,]+)"))
    peso_actual = _entero(peso_dia) or _entero(_buscar(nota, r"PESO\s+ACTUAL\s*:\s*([\d.,]+)"))
    if edad_dia:
        nota = re.sub(r"(\bEDAD\s*:\s*)[^\n]+", rf"\g<1>{edad_dia} DÍAS.", nota, count=1, flags=re.IGNORECASE)
    if peso_actual:
        reemplazo = _peso_texto(peso_nacer, peso_previo, peso_actual)
        patron_peso = r"PESO\s+ANTERIOR\s*:\s*[\d.,]+\s*G\s*,?\s*PESO\s+ACTUAL\s*:\s*[\d.,]+\s*G[^\n]*(?:\n\s*(?:P[ÉE]RDIDA\s+GLOBAL|SUPERA\s+EL\s+PESO|RECUPER[ÓO]\s+EL\s+PESO)[^\n]*)?"
        if re.search(patron_peso, nota, flags=re.IGNORECASE):
            nota = re.sub(patron_peso, reemplazo, nota, count=1, flags=re.IGNORECASE)
        else:
            nota = re.sub(
                r"(PESO\s+AL\s+NACER\s*:\s*[^\n]+)",
                lambda m: f"{m.group(1)}\n{reemplazo}",
                nota,
                count=1,
                flags=re.IGNORECASE,
            )
    return _actualizar_balance(nota, periodo), peso_nacer, peso_previo, peso_actual


def _actualizar_nota_con_ia(base, contexto, firma):
    """Solicita una nota completa; el asistente de análisis común solo devuelve un párrafo."""
    if not ia_analisis_configurada():
        return base
    cache_key = f"{PREFIX}_nota_ia_cache"
    cache = st.session_state.get(cache_key, {})
    if cache.get("firma") == firma and cache.get("texto"):
        return cache["texto"]

    instrucciones = (
        "Actualiza una evolución neonatal en español usando exclusivamente la nota previa y los datos actualizados. "
        "Devuelve la NOTA COMPLETA con todos sus encabezados clínicos, en MAYÚSCULAS, respetando diagnósticos, estudios, "
        "tamizajes, soportes y plan ya documentados. Cambia solamente edad, peso y balance cuando existan datos nuevos. "
        "Redacta un ANÁLISIS nuevo, coherente y diferente al previo, integrando los hallazgos disponibles sin inventar diagnósticos, "
        "tratamientos, resultados ni cambios clínicos. Conserva el plan previo, salvo que la información suministrada justifique de forma "
        "explícita una actualización. No agregues comentarios, advertencias ni texto fuera de la nota clínica."
    )
    try:
        modelo = obtener_secret_app("openai_model", "gpt-4o-mini")
        respuesta = solicitar_respuesta_openai(
            modelo,
            {
                "model": modelo,
                "input": json.dumps({"nota_base_actualizada": base, "datos_actualizados": contexto}, ensure_ascii=False),
                "instructions": instrucciones,
                "temperature": 0.15,
                "max_output_tokens": 2200,
            },
            timeout=45,
            max_reintentos=2,
        )
        texto = extraer_texto_respuesta_openai(respuesta).strip()
        if texto:
            st.session_state[cache_key] = {"firma": firma, "texto": texto}
            return texto
    except Exception:
        pass
    return base


def _generar_evolucion():
    nota_previa = st.session_state.get(f"{PREFIX}_nota_previa", "")
    edad = _entero(st.session_state.get(f"{PREFIX}_edad_dia"))
    peso = _entero(st.session_state.get(f"{PREFIX}_peso_dia"))
    periodo = int(st.session_state.get(f"{PREFIX}_periodo_balance", 24))
    base, peso_nacer, peso_previo, peso_actual = _actualizar_nota_local(nota_previa, edad, peso, periodo)
    contexto = {
        "nota_evolutiva_previa": nota_previa,
        "edad_actual_dias": edad or "SIN CAMBIO REGISTRADO",
        "peso_actual_gramos": peso_actual or "SIN CAMBIO REGISTRADO",
        "peso_al_nacer_gramos": peso_nacer or "NO DOCUMENTADO",
        "peso_previo_gramos": peso_previo or "NO DOCUMENTADO",
        "periodo_balance_horas": periodo,
        "nota_actualizada_por_calculos": base,
    }
    firma = hashlib.md5(json.dumps(contexto, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    resultado = _actualizar_nota_con_ia(base, contexto, firma)
    st.session_state[f"{PREFIX}_informe_final"] = resultado or base


def _guardar_historia_ucin(datos):
    HISTORIAS_UCIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HISTORIAS_UCIN_PATH.open("a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(datos, ensure_ascii=False) + "\n")


def render():
    st.header(TITULO)
    st.caption("Pegue la evolución previa y registre solamente los cambios del día. Revise y edite el resultado antes de firmarlo.")
    st.text_area("Evolución previa completa", key=f"{PREFIX}_nota_previa", height=420)

    col_edad, col_peso, col_balance = st.columns(3)
    with col_edad:
        st.number_input(
            "Edad del día (opcional)", min_value=0, step=1, key=f"{PREFIX}_edad_dia",
            help="Si no se diligencia, se conserva la edad de la nota previa.",
        )
    with col_peso:
        st.number_input(
            "Peso actual del día en gramos (opcional)", min_value=0, step=1, key=f"{PREFIX}_peso_dia",
            help="Si no se diligencia, se conserva el peso de la nota previa.",
        )
    with col_balance:
        st.selectbox(
            "Período para balance", [6, 12, 24], index=2, key=f"{PREFIX}_periodo_balance",
            help="Si la nota previa contiene balance, se extrapola proporcionalmente y queda editable en el informe final.",
        )

    if st.button("Actualizar evolución con IA", key=f"{PREFIX}_actualizar", use_container_width=True):
        if not str(st.session_state.get(f"{PREFIX}_nota_previa", "")).strip():
            st.warning("Pegue primero la evolución previa completa.")
        else:
            with st.spinner("Actualizando evolución neonatal..."):
                _generar_evolucion()

    informe = st.text_area(
        "Evolución actualizada y editable", key=f"{PREFIX}_informe_final", height=700,
        placeholder="Aquí aparecerá la evolución completa actualizada. Puede corregirla, completarla o copiarla antes de generar el Word.",
    )

    if st.button("Generar evolución clínica", key=f"{PREFIX}_generar", use_container_width=True):
        if not informe.strip():
            st.warning("Genere o pegue primero la evolución clínica final.")
            return
        fecha_guardado = datetime.now(BOGOTA_TZ).strftime("%Y-%m-%d %H:%M:%S")
        nombre = _buscar(informe, r"(?:HIJA|HIJO)\s+DE\s+([^\n]+)") or "RECIEN_NACIDO"
        nv = _buscar(informe, r"\bNV\s*[:#]?\s*([A-Z0-9-]+)")
        nombre_docx = f"{construir_nombre_base_docx('UCIN', nombre=nombre, documento=nv, fecha_guardado=fecha_guardado)}.docx"
        docx_bytes = generar_docx_informe(TITULO, [(TITULO, informe)])
        guardar_docx_exportado(docx_bytes, nombre_docx.removesuffix(".docx"), subcarpeta=PREFIX)
        _guardar_historia_ucin({"fecha": fecha_guardado, "nombre": nombre, "documento": nv, "historia": informe, "tipo": TITULO})
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
