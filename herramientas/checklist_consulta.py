"""Checklist documental: registra decisiones del profesional, sin inferir normalidad."""
import re
from herramientas.revision_documental import ancla_criterio


def quitar_edad_del_inicio(texto):
    """Solo elimina el encabezado demográfico inicial; conserva edades de antecedentes."""
    return re.sub(
        r"^\s*(?:LACTANTE(?: MENOR| MAYOR)?|PACIENTE|NIÑ[OA]|ESCOLAR|PREESCOLAR)\s+DE\s+\d+\s*(?:AÑOS?|MESES?|D[IÍ]AS?)(?:\s*(?:,|Y)\s*\d+\s*(?:AÑOS?|MESES?|D[IÍ]AS?))*\s+(?:CON|QUIEN PRESENTA|QUE PRESENTA)\s+",
        "", str(texto or ""), count=1, flags=re.I,
    ).strip()


def resumen_cuadro(texto):
    texto = re.sub(r"^SE TRATA DE .*?QUIEN ES TRA[IÍ]D[OA] POR [^.]+\.\s*CUADRO ACTUAL:\s*", "", str(texto or ""), count=1, flags=re.I)
    texto = re.sub(r"^SE TRATA DE .*?QUIEN ES TRA[IÍ]D[OA] POR .*? POR\s+", "", str(texto or ""), count=1, flags=re.I)
    texto = quitar_edad_del_inicio(texto)
    return re.split(r"(?<=[.!?])\s+", texto, maxsplit=1)[0].strip(" .")


def unir_registro(texto, adicional):
    if not adicional or adicional.strip().upper() in str(texto).upper():
        return texto
    return "\n".join(x for x in (str(texto or "").strip(), adicional.strip()) if x)


def render_checklist(st, prefix, contenedores, conducta, fr="", sat="", sugerencia_egreso=""):
    base = f"{prefix}_checklist"
    filas = []
    bloques = {k: [] for k in ("inicial", "evaluacion", "fundamento", "plan", "reevaluacion", "egreso", "educacion", "pendientes")}

    def opcion(campo, etiqueta, opciones, etapa):
        key = f"{base}_{campo}"
        ancla = ancla_criterio(key)
        st.markdown(f'<span id="{ancla}"></span>', unsafe_allow_html=True)
        valor = st.selectbox(etiqueta, ["Pendiente", *opciones], key=key)
        filas.append(dict(etiqueta=etiqueta, respuesta="" if valor == "Pendiente" else valor, ancla=ancla, etapa=etapa))
        return valor

    with contenedores["inicial"]:
        st.markdown("**Checklist de la valoración actual**")
        peligro = opcion("peligro", "Signos generales de peligro", ["Ausentes", "Presentes"], "inicial")
        if peligro != "Pendiente":
            detalle = st.text_input("Especifique los signos presentes", key=f"{base}_peligro_detalle") if peligro == "Presentes" else ""
            bloques["inicial"].append(f"Signos generales de peligro: {peligro.lower()}" + (f" ({detalle})" if detalle else "") + ".")
        for campo, etiqueta, opciones in (
            ("ingesta", "Ingesta actual", ["Habitual", "Disminuida", "No tolera", "No evaluada"]),
            ("diuresis", "Diuresis actual", ["Habitual", "Disminuida", "Ausente", "No evaluada"]),
        ):
            valor = opcion(campo, etiqueta, opciones, "inicial")
            if valor != "Pendiente":
                bloques["inicial"].append(f"{etiqueta}: {valor.lower()}.")
        nota = st.text_input("Otros hallazgos del interrogatorio (opcional)", key=f"{base}_inicial_nota")
        if nota.strip(): bloques["inicial"].append(nota.strip())

    with contenedores["evaluacion"]:
        st.caption(f"Datos del formulario: FR {fr or 'sin registrar'} rpm · SpO₂ {sat or 'sin registrar'} %. No se asignan clasificaciones ni umbrales automáticamente.")
        contexto = opcion("oximetria", "Condición de la medición de SpO₂", ["Aire ambiente", "Con oxígeno", "No evaluada"], "evaluacion")
        if contexto != "Pendiente":
            bloques["evaluacion"].append(f"Condición de la oximetría: {contexto.lower()}.")
        if contexto == "Con oxígeno":
            soporte = st.text_input("Dispositivo y flujo / FiO₂ registrados", key=f"{base}_oxigeno_soporte")
            if soporte.strip(): bloques["evaluacion"].append(f"Soporte durante la medición: {soporte.strip()}.")
        clasificacion = st.text_input("Clasificación o gravedad según su valoración", key=f"{base}_clasificacion")
        if clasificacion.strip(): bloques["evaluacion"].append(f"Clasificación clínica: {clasificacion.strip()}.")

    with contenedores["cierre"]:
        st.caption(f"Conducta actual seleccionada: {conducta}. Para cambiarla, use el selector de conducta del formulario.")
        fundamento = st.text_input("Fundamento de la conducta seleccionada (opcional)", key=f"{base}_fundamento")
        if fundamento.strip(): bloques["fundamento"].append(fundamento.strip())
        estudios = opcion("estudios", "¿Solicita estudios complementarios en esta valoración?", ["No", "Sí"], "cierre")
        if estudios == "Sí":
            detalle = st.text_input("Estudios solicitados y justificación", key=f"{base}_estudios_detalle")
            if detalle.strip(): bloques["plan"].append(f"Estudios solicitados y justificación: {detalle.strip()}.")
            else: st.warning("Especifique los estudios; no se añadirá una orden genérica al plan.")
        elif estudios == "No":
            bloques["plan"].append("No se solicitan estudios complementarios en esta valoración.")
        if conducta in ("OBSERVACIÓN", "HOSPITALIZACIÓN"):
            realizada = st.checkbox("Ya realicé una reevaluación", key=f"{base}_reevaluacion_realizada")
            if realizada:
                momento = st.text_input("Fecha y hora de la reevaluación", key=f"{base}_reevaluacion_hora")
                evolucion = st.text_area("Hallazgos, respuesta y decisión tras reevaluar", key=f"{base}_reevaluacion_texto", height=100)
                if evolucion.strip(): bloques["reevaluacion"].append(f"{momento or 'Hora no registrada'}: {evolucion.strip()}")
            condiciones = st.text_input("Condiciones pendientes para considerar un egreso posterior (opcional)", key=f"{base}_condiciones_egreso")
            if condiciones.strip(): bloques["pendientes"].append(condiciones.strip())
        if conducta == "EGRESO":
            if sugerencia_egreso:
                with st.expander("Recomendaciones sugeridas para revisar", expanded=False):
                    st.text(sugerencia_egreso)
                if st.checkbox("Revisé e incluyo las recomendaciones sugeridas", key=f"{base}_egreso_sugerido"):
                    bloques["egreso"].append(sugerencia_egreso)
            instrucciones = st.text_area("Recomendaciones de egreso y seguimiento individualizados", key=f"{base}_egreso_texto", height=100)
            if instrucciones.strip(): bloques["egreso"].append(instrucciones.strip())
        if st.checkbox("Realicé educación al paciente o cuidador", key=f"{base}_educacion_realizada"):
            temas = st.text_input("A quién informó y temas explicados", key=f"{base}_educacion_texto")
            if temas.strip(): bloques["educacion"].append(f"Educación realizada: {temas.strip()}.")
            comprension = opcion("comprension", "Verificación de comprensión", ["Confirmada", "Persisten dudas", "No evaluada"], "cierre")
            if comprension != "Pendiente": bloques["educacion"].append(f"Comprensión: {comprension.lower()}.")
    st.session_state[f"{base}_revision"] = filas
    return {k: "\n".join(v) for k, v in bloques.items()}


def incorporar_checklist(secciones, checklist):
    """Cada hallazgo se incorpora en su sección, sin volcados de guías al análisis."""
    destinos = {"ENFERMEDAD ACTUAL": "inicial", "EXAMEN FÍSICO": "evaluacion", "ANÁLISIS": "fundamento", "PLAN": "plan"}
    resultado = [(titulo, unir_registro(texto, checklist.get(destinos.get(titulo, ""), ""))) for titulo, texto in secciones]
    for titulo, clave in (("REEVALUACIÓN", "reevaluacion"), ("CONDICIONES PENDIENTES PARA EVENTUAL EGRESO", "pendientes"), ("RECOMENDACIONES DE EGRESO", "egreso"), ("EDUCACIÓN DOCUMENTADA", "educacion")):
        if checklist.get(clave): resultado.append((titulo, checklist[clave]))
    return [(titulo, re.sub(r"(?m)^\\-", "-", re.sub(r"(?m)^(\d+)\\\.", r"\1.", texto))) for titulo, texto in resultado]


def texto_desde_secciones(titulo, secciones):
    return titulo + "\n\n" + "\n\n".join(f"{nombre}:\n{texto}" for nombre, texto in secciones)


def crear_referencias(st, contenedores):
    referencias = {}
    for etapa, contenedor in contenedores.items():
        with contenedor:
            if etapa == "inicial":
                st.caption("Las respuestas previas del ejemplo o borrador están en el detalle de referencia. Verifique y registre en la checklist los hallazgos que corresponden a esta valoración.")
            referencias[etapa] = st.expander("Detalle previo GPC/AIEPI y del ejemplo (referencia)", expanded=False)
            with referencias[etapa]:
                st.caption("Estos registros se conservan en modo de lectura para consulta. Ya no se copian automáticamente al informe ni a la IA. Incorpore los hallazgos verificados en la checklist o en los campos clínicos correspondientes.")
    return referencias
