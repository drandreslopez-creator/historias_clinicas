"""Revisión documental local: no evalúa adherencia ni toma decisiones clínicas."""
import hashlib
import json
import re
import unicodedata


def ancla_criterio(key):
    return "criterio-" + hashlib.sha256(key.encode()).hexdigest()[:16]


def estado_registro(respuesta):
    texto = str(respuesta or "").strip()
    if not texto:
        return "Sin registrar"
    normal = "".join(c for c in unicodedata.normalize("NFD", texto.upper()) if unicodedata.category(c) != "Mn")
    coincidencia = re.match(r"^(?:NO APLICA|N/?A)(?=$|[\s:;.—-])", normal)
    if coincidencia:
        motivo = normal[coincidencia.end():].strip(" :;.,—-\n")
        return "No aplica con justificación" if motivo else "No aplica sin justificación"
    return "Con registro"


def marcar_ejemplo(st, prefix, nombre):
    st.session_state[f"{prefix}_ejemplo_origen"] = nombre
    st.session_state.pop(f"{prefix}_ejemplo_confirmado", None)


def huella_revision(estado, claves):
    datos = {k: estado.get(k) for k in sorted(set(claves))}
    return hashlib.sha256(json.dumps(datos, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


def aviso_ejemplo(st, prefix):
    origen = st.session_state.get(f"{prefix}_ejemplo_origen", "")
    if origen:
        st.warning(f"Datos cargados desde un ejemplo: {origen}. Revise identificación, antecedentes, hallazgos y conducta; confirme su adaptación al paciente al final del formulario.")


def render_revision_documental(st, *, prefix, registros=(), claves_revision=()):
    origen = st.session_state.get(f"{prefix}_ejemplo_origen", "")
    if not registros and not origen:
        return True
    st.subheader("Revisión antes de generar")
    filas = []
    for registro in registros:
        filas.extend(st.session_state.get(f"{registro}_revision", []))
    # La pregunta compartida tiene un único destino y se revisa una sola vez.
    filas = list({fila["ancla"]: fila for fila in filas}.values())
    pendientes = [f for f in filas if estado_registro(f["respuesta"]) in ("Sin registrar", "No aplica sin justificación")]
    if filas:
        st.caption(f"{len(pendientes)} pendientes de registro · {len(filas)} criterios de las rutas seleccionadas. Esta revisión comprueba documentación, no adherencia clínica.")
        st.caption('Cuando no corresponda un criterio, escriba «No aplica: motivo». Los avisos no bloquean la generación.')
        with st.expander("Ver pendientes y registros", expanded=bool(pendientes)):
            for fila in sorted(filas, key=lambda f: f not in pendientes):
                estado = estado_registro(fila["respuesta"])
                etapa = {"inicial": "Evaluación inicial", "evaluacion": "Evaluación y clasificación", "cierre": "Conducta y cierre"}[fila["etapa"]]
                st.markdown(f"- **{estado}** · [{fila['etiqueta']}](#{fila['ancla']}) · {etapa}")
    elif registros:
        st.info("No hay criterios específicos disponibles para revisar en la selección actual.")
    if not origen:
        return True
    claves = list(claves_revision)
    for registro in registros:
        claves += [k for k in st.session_state if k == registro or k.startswith(f"{registro}_criterio_")]
    # Las respuestas compartidas también forman parte de la revisión.
    huella = huella_revision(st.session_state, claves)
    confirmacion_key = f"{prefix}_ejemplo_confirmado"
    confirmado = st.session_state.get(confirmacion_key) == huella
    if not confirmado:
        st.warning("Ejemplo pendiente de revisión. Adapte o elimine los datos ficticios antes de confirmar, incluidos los que parecen normales.")
        if st.button("Confirmo que revisé y adapté los datos del ejemplo al paciente", key=f"{prefix}_confirmar_ejemplo"):
            st.session_state[confirmacion_key] = huella
            confirmado = True
    if confirmado:
        st.success("Revisión del ejemplo confirmada para los datos actuales. Si modifica el formulario, deberá confirmar de nuevo.")
    return confirmado
