"""Importación local y prudente de datos desde historias clínicas previas."""

from datetime import datetime
from io import BytesIO
import hashlib
import json
import os
import re
import unicodedata

import requests
import streamlit as st
from docx import Document
from pypdf import PdfReader


TIPOS_DOCUMENTO = {"NV", "RC", "TI", "CC", "CE", "PEP", "PS", "OTRO"}


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto or ""))
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")
    return re.sub(r"\s+", " ", texto).strip().upper()


def _texto_docx(datos):
    documento = Document(BytesIO(datos))
    partes = [parrafo.text.strip() for parrafo in documento.paragraphs if parrafo.text.strip()]
    for tabla in documento.tables:
        for fila in tabla.rows:
            valores = [celda.text.strip() for celda in fila.cells if celda.text.strip()]
            if valores:
                partes.append(" | ".join(valores))
    return "\n".join(partes)


@st.cache_data(show_spinner=False, max_entries=12)
def extraer_texto_historia_previa(nombre_archivo, datos):
    """Extrae texto de PDF con capa textual o de archivos DOCX.

    No guarda el documento ni lo envía a servicios externos. Los PDF escaneados
    sin capa de texto se reportan para que el usuario pueda transcribir los datos.
    """
    extension = nombre_archivo.rsplit(".", 1)[-1].lower() if "." in nombre_archivo else ""
    try:
        if extension == "pdf":
            lector = PdfReader(BytesIO(datos))
            texto = "\n".join((pagina.extract_text() or "") for pagina in lector.pages).strip()
            return texto or "__PDF_SIN_TEXTO_EXTRAIBLE__"
        if extension == "docx":
            return _texto_docx(datos)
    except Exception:
        return "__ARCHIVO_NO_LEIBLE__"
    return ""


def _valor_etiqueta(texto, etiquetas):
    for etiqueta in etiquetas:
        patron = rf"(?:^|\n)\s*{etiqueta}\s*[:\-]?\s*([^\n|]+)"
        coincidencia = re.search(patron, texto, flags=re.IGNORECASE)
        if coincidencia:
            valor = coincidencia.group(1).strip(" -:\t")
            if valor and _normalizar(valor) not in {_normalizar(etiqueta), "NO REGISTRADO"}:
                return valor
    return ""


def _fecha_desde_texto(valor):
    coincidencia = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b", str(valor or ""))
    if not coincidencia:
        return None
    try:
        return datetime.strptime("/".join(coincidencia.groups()), "%d/%m/%Y").date()
    except ValueError:
        return None


def _extraer_antecedentes(texto):
    lineas = [linea.strip() for linea in str(texto or "").splitlines()]
    inicio = None
    for indice, linea in enumerate(lineas):
        normalizada = _normalizar(linea).rstrip(":")
        if normalizada in {
            "ANTECEDENTES",
            "ANTECEDENTES GENERALES",
            "ANTECEDENTES PERSONALES Y FAMILIARES",
        }:
            inicio = indice + 1
            break
    if inicio is None:
        return ""

    cierres = {
        "NEURODESARROLLO", "REVISION POR SISTEMAS", "SIGNOS VITALES",
        "EXAMEN FISICO", "PARACLINICOS", "ANALISIS", "DIAGNOSTICOS",
        "IMPRESION DIAGNOSTICA", "PLAN", "CONDUCTA FINAL", "EVOLUCION",
    }
    bloque = []
    for linea in lineas[inicio:]:
        normalizada = _normalizar(linea).rstrip(":")
        if normalizada in cierres:
            break
        if linea:
            bloque.append(linea)
    return "\n".join(bloque).strip()


def extraer_datos_historia_previa(texto):
    """Obtiene únicamente datos de continuidad que pueden migrarse con seguridad."""
    texto = str(texto or "")[:120000]
    tipo_documento = _normalizar(_valor_etiqueta(texto, [r"TIPO DE DOCUMENTO", r"TIPO DOCUMENTO"]))
    sexo = _valor_etiqueta(texto, [r"SEXO"])
    sexo_normalizado = _normalizar(sexo)
    if sexo_normalizado.startswith("FEMEN"):
        sexo = "Femenino"
    elif sexo_normalizado.startswith("MASCUL"):
        sexo = "Masculino"
    else:
        sexo = ""

    return {
        "nombre": _valor_etiqueta(texto, [r"NOMBRES? Y APELLIDOS?", r"NOMBRE(?: DEL)?(?: PACIENTE| RN)?"]),
        "tipo_documento": tipo_documento if tipo_documento in TIPOS_DOCUMENTO else "",
        "documento": _valor_etiqueta(texto, [r"DOCUMENTO", r"IDENTIFICACION", r"N[ÚU]MERO DE DOCUMENTO"]),
        "fecha_nacimiento": _fecha_desde_texto(_valor_etiqueta(texto, [r"FECHA DE NACIMIENTO", r"FECHA NACIMIENTO", r"FN"])),
        "sexo": sexo,
        "eps": _valor_etiqueta(texto, [r"EPS", r"ASEGURADORA"]),
        "telefono": _valor_etiqueta(texto, [r"TEL[EÉ]FONO", r"CELULAR"]),
        "informante": _valor_etiqueta(
            texto,
            [r"INFORMANTE(?:\s*\([^\n)]*\))?(?:\s*/\s*ACOMPA[ÑN]ANTE)?", r"ACOMPA[ÑN]ANTE"],
        ),
        "antecedentes": _extraer_antecedentes(texto),
    }


def _obtener_secret(nombre, default=""):
    try:
        valor = st.secrets.get(nombre, default)
        if valor:
            return str(valor)
    except Exception:
        pass
    return os.getenv(nombre.upper(), default)


def _texto_respuesta_openai(respuesta):
    if not isinstance(respuesta, dict):
        return ""
    if respuesta.get("output_text"):
        return str(respuesta["output_text"])
    partes = []
    for salida in respuesta.get("output", []):
        for contenido in salida.get("content", []):
            if contenido.get("type") == "output_text" and contenido.get("text"):
                partes.append(str(contenido["text"]))
    return "\n".join(partes)


def _json_desde_respuesta(texto):
    texto = str(texto or "").strip()
    texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.IGNORECASE)
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        inicio, final = texto.find("{"), texto.rfind("}")
        if inicio >= 0 and final > inicio:
            try:
                return json.loads(texto[inicio:final + 1])
            except json.JSONDecodeError:
                pass
    return {}


def verificar_datos_historia_previa_con_ia(texto, datos_locales):
    """Contrasta datos migrables con el documento sin completar información faltante."""
    api_key = _obtener_secret("openai_api_key")
    if not api_key:
        return datos_locales, "No hay una clave de IA configurada; se usó la extracción local."

    modelo = _obtener_secret("openai_model", "gpt-4o-mini")
    instrucciones = (
        "Eres un verificador documental de historias clínicas en español. Extrae solo datos "
        "explícitos del texto original. Nunca infieras, completes, corrijas ni inventes valores. "
        "Si un valor es ambiguo o no está escrito con claridad, devuélvelo como cadena vacía. "
        "Para antecedentes, conserva únicamente el bloque expresamente documentado bajo "
        "ANTECEDENTES; no agregues información de diagnósticos, análisis o plan. "
        "Responde exclusivamente JSON válido con estas llaves: nombre, tipo_documento, documento, "
        "fecha_nacimiento, sexo, eps, telefono, informante, antecedentes, advertencias. "
        "fecha_nacimiento debe usar DD/MM/AAAA o cadena vacía. tipo_documento debe ser una de "
        "NV, RC, TI, CC, CE, PEP, PS, OTRO o cadena vacía. sexo debe ser Masculino, Femenino o cadena vacía. "
        "advertencias debe ser una lista breve de campos no confirmados o inconsistencias."
    )
    contexto = {
        "datos_extraidos_localmente": datos_locales,
        "texto_historia_previa": str(texto or "")[:90000],
    }
    try:
        respuesta = requests.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": modelo,
                "input": json.dumps(contexto, ensure_ascii=False),
                "instructions": instrucciones,
                "temperature": 0,
                "max_output_tokens": 900,
            },
            timeout=35,
        )
        respuesta.raise_for_status()
        resultado = _json_desde_respuesta(_texto_respuesta_openai(respuesta.json()))
    except Exception as error:
        return datos_locales, f"No fue posible verificar con IA; se usó la extracción local. {error}"

    if not isinstance(resultado, dict):
        return datos_locales, "La IA no devolvió un formato verificable; se usó la extracción local."

    verificados = dict(datos_locales)
    for campo in ("nombre", "tipo_documento", "documento", "eps", "telefono", "informante", "antecedentes"):
        valor = str(resultado.get(campo) or "").strip()
        if valor:
            verificados[campo] = valor

    fecha = _fecha_desde_texto(resultado.get("fecha_nacimiento"))
    if fecha:
        verificados["fecha_nacimiento"] = fecha
    sexo = str(resultado.get("sexo") or "").strip()
    if sexo in {"Masculino", "Femenino"}:
        verificados["sexo"] = sexo
    tipo = _normalizar(resultado.get("tipo_documento"))
    if tipo in TIPOS_DOCUMENTO:
        verificados["tipo_documento"] = tipo

    advertencias = resultado.get("advertencias", [])
    if isinstance(advertencias, str):
        advertencias = [advertencias]
    advertencias = [str(advertencia).strip() for advertencia in advertencias if str(advertencia).strip()]
    return verificados, " ".join(advertencias)


def _resumen_datos(datos):
    etiquetas = {
        "nombre": "Nombre", "tipo_documento": "Tipo de documento", "documento": "Documento",
        "fecha_nacimiento": "Fecha de nacimiento", "sexo": "Sexo", "eps": "EPS",
        "telefono": "Teléfono", "informante": "Informante", "antecedentes": "Antecedentes",
    }
    partes = []
    for clave, etiqueta in etiquetas.items():
        valor = datos.get(clave)
        if clave == "fecha_nacimiento" and valor:
            valor = valor.strftime("%d/%m/%Y")
        if valor:
            if clave == "antecedentes":
                partes.append(f"{etiqueta}: se identificó un bloque clínico editable.")
            else:
                partes.append(f"{etiqueta}: {valor}")
    return "\n".join(partes) or "No se identificaron datos estructurados para migrar."


def render_importador_historia_previa(prefix, campos, antecedentes_default=""):
    """Renderiza un importador reutilizable antes de identificación.

    `campos` relaciona nombres estándar con las claves de Session State de cada
    plantilla. Solo se migra información identificada de forma explícita.
    """
    with st.expander("Historia clínica previa", expanded=False):
        st.caption(
            "Adjunte una historia previa en PDF con texto o Word (.docx). Se lee localmente "
            "para migrar identificación y antecedentes; el documento no se adjunta al informe actual."
        )
        archivo = st.file_uploader(
            "Seleccionar historia previa",
            type=["pdf", "docx"],
            accept_multiple_files=False,
            key=f"{prefix}_historia_previa_archivo",
        )
        if not archivo:
            return

        texto = extraer_texto_historia_previa(archivo.name, archivo.getvalue())
        if texto == "__PDF_SIN_TEXTO_EXTRAIBLE__":
            st.warning("El PDF parece escaneado y no contiene texto seleccionable. Use un PDF con texto o un archivo Word (.docx).")
            return
        if texto in {"", "__ARCHIVO_NO_LEIBLE__"}:
            st.error("No fue posible leer el archivo. Verifique que sea un PDF o Word (.docx) válido.")
            return

        firma_archivo = hashlib.sha256(archivo.getvalue()).hexdigest()
        datos_locales = extraer_datos_historia_previa(texto)
        datos = datos_locales
        ia_configurada = bool(_obtener_secret("openai_api_key"))
        verificacion_ia_completa = st.session_state.get(f"{prefix}_historia_previa_ia_firma") == firma_archivo
        if verificacion_ia_completa:
            datos_ia = st.session_state.get(f"{prefix}_historia_previa_ia_datos", {})
            if isinstance(datos_ia, dict):
                datos = datos_ia

        col_ia, col_estado = st.columns([1.4, 2.6])
        if col_ia.button(
            "Verificar datos con IA",
            key=f"{prefix}_verificar_historia_previa_ia",
            use_container_width=True,
        ):
            with st.spinner("Verificando datos documentados en la historia previa..."):
                datos_verificados, advertencia_ia = verificar_datos_historia_previa_con_ia(texto, datos_locales)
            st.session_state[f"{prefix}_historia_previa_ia_firma"] = firma_archivo
            st.session_state[f"{prefix}_historia_previa_ia_datos"] = datos_verificados
            st.session_state[f"{prefix}_historia_previa_ia_advertencia"] = advertencia_ia
            st.rerun()
        if verificacion_ia_completa:
            col_estado.caption("Datos contrastados con IA contra el documento original.")
            advertencia_ia = st.session_state.get(f"{prefix}_historia_previa_ia_advertencia", "")
            if advertencia_ia:
                st.warning(f"Verificación IA: {advertencia_ia}")
        else:
            if ia_configurada:
                col_estado.caption("La extracción inicial es local. Verifique con IA antes de migrar para contrastar los valores.")
            else:
                col_estado.caption("La IA no está configurada; solo está disponible la extracción local.")

        st.text_area(
            "Datos preparados para migración",
            value=_resumen_datos(datos),
            height=170,
            disabled=True,
        )
        sobrescribir = st.checkbox(
            "Reemplazar los datos que ya están diligenciados",
            value=False,
            key=f"{prefix}_historia_previa_sobrescribir",
        )
        if st.button(
            "Migrar datos de historia previa",
            key=f"{prefix}_migrar_historia_previa",
            use_container_width=True,
            disabled=ia_configurada and not verificacion_ia_completa,
        ):
            migrados = []
            for campo, clave_estado in campos.items():
                valor = datos.get(campo)
                if not valor or not clave_estado:
                    continue
                actual = st.session_state.get(clave_estado)
                es_default_antecedentes = campo == "antecedentes" and actual == antecedentes_default
                if sobrescribir or not actual or es_default_antecedentes:
                    st.session_state[clave_estado] = valor
                    migrados.append(campo)
            if migrados:
                st.session_state[f"{prefix}_historia_previa_notice"] = (
                    "Datos migrados: " + ", ".join(migrados) + ". Revise y actualice la información antes de generar la historia."
                )
                st.rerun()
            st.info("No se modificó ningún campo: los datos ya estaban diligenciados o no se identificaron valores migrables.")
