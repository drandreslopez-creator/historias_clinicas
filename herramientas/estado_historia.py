"""Estado persistible y revisión del informe final, sin decisiones clínicas."""
import hashlib

from herramientas.revision_documental import huella_revision


def claves_auxiliares(key, prefix):
    base = "" if prefix == "urgencias" else prefix + "_"
    return (key in (base + "aiepi_apoyo", base + "aiepi_registro", base + "consulta_cie10_dx")
            or key.startswith((base + "gpc_registro_criterio_", base + "aiepi_registro_criterio_"))
            or (prefix == "urgencias" and key.startswith(("_plan_ejemplo_", "_analisis_ejemplo_")))
            or (prefix != "urgencias" and key.startswith((f"_{prefix}_plan_ejemplo_", f"_{prefix}_analisis_ejemplo_"))))


def snapshot_formulario(estado, defaults, prefix):
    datos = {k: estado.get(k, v) for k, v in defaults.items()}
    datos.update({k: estado[k] for k in estado if claves_auxiliares(k, prefix)})
    return datos


def restaurar_formulario(estado, datos, defaults, prefix):
    for k, v in datos.items():
        if k in defaults or claves_auxiliares(k, prefix):
            estado[k] = v


def huella_formulario(estado, defaults, prefix):
    datos = snapshot_formulario(estado, defaults, prefix)
    # Cachés y bases generadas no son campos editados por el profesional.
    datos = {k: v for k, v in datos.items() if not k.startswith("_") and not k.endswith(("_base", "_auto", "_pdf_sig", "_id"))}
    for k in (["dx_cie10", "tipo_historia_clinica_ped_urg"] if prefix == "urgencias" else [f"{prefix}_consulta_cie10_dx"]):
        datos[k] = estado.get(k)
    return huella_revision(datos, datos)


def preparar_informe(st, prefix, huella, titulo, secciones, historia, nombre, documento, tipo_documento=""):
    st.session_state[f"{prefix}_informe_final"] = dict(
        huella=huella, titulo=titulo, secciones=secciones, historia=historia,
        nombre=nombre, documento=documento, tipo_documento=tipo_documento, guardado=False,
    )


def revisar_informe(st, prefix, huella, guardar):
    informe = st.session_state.get(f"{prefix}_informe_final")
    if not informe:
        return
    if informe["huella"] != huella:
        st.session_state.pop(f"{prefix}_informe_final", None)
        st.info("El formulario cambió. Genere de nuevo la vista previa antes de guardar.")
        return
    st.subheader("Informe final para revisión")
    st.caption("Revise el texto definitivo, incluido el análisis y el plan generados. Para corregirlo, modifique el formulario y vuelva a generar.")
    st.text_area("Texto definitivo", value=informe["historia"], height=500, disabled=True, key=clave_texto_informe(f"{prefix}_vista_final", informe["historia"]))
    if not informe["guardado"]:
        if st.button("Confirmar informe final y guardar / enviar a Drive", key=f"{prefix}_guardar_final"):
            guardar(informe)
            informe["guardado"] = True
    if informe["guardado"]:
        st.success("Este informe ya fue guardado.")
        if informe.get("docx_bytes"):
            st.download_button("Descargar informe en Word", data=informe["docx_bytes"],
                               file_name=informe["nombre_docx"],
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               key=f"{prefix}_descargar_final")


def informe_guardado_actual(st, prefix, huella):
    informe = st.session_state.get(f"{prefix}_informe_final", {})
    return informe.get("guardado", False) and informe.get("huella") == huella


def clave_texto_informe(prefix, texto):
    """El widget debe representar el contenido actual, incluso con iguales entradas."""
    return prefix + "_" + hashlib.sha256(texto.encode("utf-8")).hexdigest()
