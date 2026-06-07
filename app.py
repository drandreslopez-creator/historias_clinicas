import streamlit as st
import streamlit.components.v1 as components
from utils.google_drive_oauth import (
    desconectar_google_drive,
    google_drive_conectado,
    google_oauth_configurado,
    obtener_google_auth_url,
    obtener_google_drive_usuario,
    procesar_google_oauth_callback,
)

# IMPORTAR SERVICIOS
from servicios import pediatria_urgencias
from servicios import neonatologia_adaptacion
from servicios import consulta_homeopatia_pediatrica
from servicios import consulta_homeopatia_adultos
from servicios import consulta_pediatria_puericultura
from servicios import scores_pediatricos
from servicios import procedimientos_espirometria
from servicios import plantillas_genericas

PASSWORD_APP = "8041003"

st.set_page_config(page_title="Medinexus", layout="wide")
components.html(
    """
    <script>
      document.documentElement.lang = "es";
      document.documentElement.setAttribute("translate", "no");
      const meta = document.createElement("meta");
      meta.name = "google";
      meta.content = "notranslate";
      document.head.appendChild(meta);
    </script>
    """,
    height=0,
)

oauth_resultado = procesar_google_oauth_callback()
if oauth_resultado is True:
    st.session_state["google_drive_oauth_notice"] = "Google Drive conectado correctamente."
elif oauth_resultado is False:
    st.session_state["google_drive_oauth_notice"] = "No se pudo completar la conexión con Google Drive."

if "app_autenticada" not in st.session_state:
    st.session_state["app_autenticada"] = False

if not st.session_state["app_autenticada"]:
    st.title("Medinexus")
    st.caption("Plataforma de documentación clínica")
    st.subheader("Acceso")
    with st.form("login_form"):
        password_input = st.text_input("Contraseña", type="password")
        login_submit = st.form_submit_button("Ingresar")

    if login_submit:
        if password_input == PASSWORD_APP:
            st.session_state["app_autenticada"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")

    st.stop()

st.title("Medinexus")
st.caption("Plataforma de documentación clínica")

col_titulo, col_drive = st.columns([6, 1.8])
with col_drive:
    if google_oauth_configurado():
        usuario_drive = obtener_google_drive_usuario()
        etiqueta_drive = "Drive"
        with st.popover(etiqueta_drive, use_container_width=True):
            if google_drive_conectado():
                correo = usuario_drive.get("email") if usuario_drive else ""
                st.caption(f"Conectado{f': {correo}' if correo else ''}")
                if st.button("Desconectar", use_container_width=True):
                    desconectar_google_drive()
                    st.rerun()
            else:
                auth_url = obtener_google_auth_url()
                if auth_url:
                    st.link_button("Conectar Google Drive", auth_url, use_container_width=True)
            if st.session_state.get("google_drive_oauth_notice"):
                st.caption(st.session_state["google_drive_oauth_notice"])
    else:
        with st.popover("Drive", use_container_width=True):
            st.caption("OAuth de Google Drive no configurado.")

area_servicio = st.selectbox(
    "Área de servicio",
    [
        "Consulta Externa",
        "Pediatría Urgencias",
        "Pediatría Hospitalización",
        "Neonatología",
        "Telemedicina",
        "Procedimientos",
        "Scores Pediátricos",
    ]
)

if area_servicio == "Pediatría Urgencias":
    st.selectbox(
        "Tipo de historia clínica",
        [
            "RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA DE URGENCIAS",
            "HISTORIA CLINICA DE INGRESO A URGENCIAS PEDIATRICAS",
        ],
        key="tipo_historia_clinica_ped_urg",
    )
elif area_servicio == "Consulta Externa":
    st.selectbox(
        "Tipo de historia clínica",
        [
            "PEDIATRÍA Y PUERICULTURA",
            "MEDICINA ALTERNATIVA - HOMEOPATÍA PEDIÁTRICA",
            "MEDICINA ALTERNATIVA - HOMEOPATÍA ADULTOS",
            "NEONATOLOGÍA",
        ],
        key="tipo_historia_clinica_consulta_externa",
    )
elif area_servicio == "Pediatría Hospitalización":
    st.selectbox(
        "Tipo de historia clínica",
        [
            "HISTORIA CLINICA DE INGRESO A URGENCIAS PEDIATRICAS",
            "NOTA DE EVOLUCIÓN DE HOSPITALIZACIÓN PEDIÁTRICA",
            "RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA",
        ],
        key="tipo_historia_clinica_hospitalizacion",
    )
elif area_servicio == "Neonatología":
    st.selectbox(
        "Tipo de historia clínica",
        [
            "HISTORIA CLÍNICA DE ADAPTACIÓN NEONATAL",
            "EVOLUCIÓN DEL RECIÉN NACIDOS EN ALOJAMIENTO CONJUNTO",
            "RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA PERINATAL Y NEONATOLOGÍA",
            "EVOLUCIÓN DEL RECIÉN NACIDOS EN SERVICIO DE URGENCIAS",
            "HISTORIA CLINICA DE INGRESO A UNIDAD DE RECIÉN NACIDOS",
            "EVOLUCIÓN DEL RECIÉN NACIDO EN UCIN",
        ],
        key="tipo_historia_clinica_neonatologia",
    )
elif area_servicio == "Telemedicina":
    st.selectbox(
        "Tipo de historia clínica",
        [
            "HISTORIA CLÍNICA DE TELEMEDICINA - PEDIATRÍA",
            "HISTORIA CLÍNICA DE TELEMEDICINA - HOMEOPATÍA PEDIÁTRICA",
            "HISTORIA CLÍNICA DE TELEMEDICINA - HOMEOPATÍA ADULTOS",
        ],
        key="tipo_historia_clinica_telemedicina",
    )
elif area_servicio == "Procedimientos":
    st.selectbox(
        "Subitem",
        [
            "Espirometría",
        ],
        key="tipo_procedimiento",
    )
elif area_servicio == "Scores Pediátricos":
    st.caption("Módulo independiente de scores. No genera historia clínica.")

# ENRUTADOR 🔥
if area_servicio == "Pediatría Urgencias":
    pediatria_urgencias.render()
elif area_servicio == "Consulta Externa":
    tipo_consulta = st.session_state.get("tipo_historia_clinica_consulta_externa")
    if tipo_consulta == "PEDIATRÍA Y PUERICULTURA":
        consulta_pediatria_puericultura.render()
    elif tipo_consulta == "MEDICINA ALTERNATIVA - HOMEOPATÍA PEDIÁTRICA":
        consulta_homeopatia_pediatrica.render()
    elif tipo_consulta == "MEDICINA ALTERNATIVA - HOMEOPATÍA ADULTOS":
        consulta_homeopatia_adultos.render()
    elif tipo_consulta == "NEONATOLOGÍA":
        plantillas_genericas.render_consulta_neonatologia()
elif area_servicio == "Pediatría Hospitalización":
    tipo_hospitalizacion = st.session_state.get("tipo_historia_clinica_hospitalizacion")
    if tipo_hospitalizacion == "HISTORIA CLINICA DE INGRESO A URGENCIAS PEDIATRICAS":
        plantillas_genericas.render_hospitalizacion_ingreso()
    elif tipo_hospitalizacion == "NOTA DE EVOLUCIÓN DE HOSPITALIZACIÓN PEDIÁTRICA":
        plantillas_genericas.render_hospitalizacion_evolucion()
    elif tipo_hospitalizacion == "RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA":
        plantillas_genericas.render_hospitalizacion_interconsulta()
elif area_servicio == "Neonatología":
    tipo_neonatologia = st.session_state.get("tipo_historia_clinica_neonatologia")
    if tipo_neonatologia == "HISTORIA CLÍNICA DE ADAPTACIÓN NEONATAL":
        neonatologia_adaptacion.render()
    elif tipo_neonatologia == "EVOLUCIÓN DEL RECIÉN NACIDOS EN ALOJAMIENTO CONJUNTO":
        plantillas_genericas.render_neonatologia_evolucion_alojamiento()
    elif tipo_neonatologia == "RESPUESTA DE INTERCONSULTA - SERVICIO DE PEDIATRÍA PERINATAL Y NEONATOLOGÍA":
        plantillas_genericas.render_neonatologia_interconsulta()
    elif tipo_neonatologia == "EVOLUCIÓN DEL RECIÉN NACIDOS EN SERVICIO DE URGENCIAS":
        plantillas_genericas.render_neonatologia_evolucion_urgencias()
    elif tipo_neonatologia == "HISTORIA CLINICA DE INGRESO A UNIDAD DE RECIÉN NACIDOS":
        plantillas_genericas.render_neonatologia_ingreso_unidad()
    elif tipo_neonatologia == "EVOLUCIÓN DEL RECIÉN NACIDO EN UCIN":
        plantillas_genericas.render_neonatologia_evolucion_ucin()
elif area_servicio == "Telemedicina":
    tipo_telemedicina = st.session_state.get("tipo_historia_clinica_telemedicina")
    if tipo_telemedicina == "HISTORIA CLÍNICA DE TELEMEDICINA - PEDIATRÍA":
        plantillas_genericas.render_telemedicina_pediatria()
    elif tipo_telemedicina == "HISTORIA CLÍNICA DE TELEMEDICINA - HOMEOPATÍA PEDIÁTRICA":
        plantillas_genericas.render_telemedicina_homeopatia_pediatrica()
    elif tipo_telemedicina == "HISTORIA CLÍNICA DE TELEMEDICINA - HOMEOPATÍA ADULTOS":
        plantillas_genericas.render_telemedicina_homeopatia_adultos()
elif area_servicio == "Procedimientos":
    tipo_procedimiento = st.session_state.get("tipo_procedimiento")
    if tipo_procedimiento == "Espirometría":
        procedimientos_espirometria.render()
elif area_servicio == "Scores Pediátricos":
    scores_pediatricos.render()
