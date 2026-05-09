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

PASSWORD_APP = "8041003"

st.set_page_config(page_title="Historias Clínicas", page_icon="🩺", layout="wide")
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
    st.title("🩺 FORMATO DE HISTORIA CLÍNICA DEL DR. ANDRÉS LÓPEZ RUIZ")
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

st.title("🩺 FORMATO DE HISTORIA CLÍNICA DEL DR. ANDRÉS LÓPEZ RUIZ")

col_titulo, col_drive = st.columns([6, 1.8])
with col_drive:
    if google_oauth_configurado():
        usuario_drive = obtener_google_drive_usuario()
        etiqueta_drive = "🟢 Drive" if google_drive_conectado() else "⚪ Drive"
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
        with st.popover("⚪ Drive", use_container_width=True):
            st.caption("OAuth de Google Drive no configurado.")

area_servicio = st.selectbox(
    "Área de servicio",
    [
        "Pediatría Urgencias",
        "Pediatría Hospitalización",
        "Adaptación Neonatal",
        "Evolución Neonatal",
        "Consulta Externa",
        "Homeopatía"
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
            "HOMEOPATÍA PEDIÁTRICA",
            "HOMEOPATÍA ADULTOS",
        ],
        key="tipo_historia_clinica_consulta_externa",
    )
elif area_servicio == "Homeopatía":
    st.selectbox(
        "Tipo de historia clínica",
        [
            "HOMEOPATÍA PEDIÁTRICA",
            "HOMEOPATÍA ADULTOS",
        ],
        key="tipo_historia_clinica_homeopatia",
    )

# ENRUTADOR 🔥
if area_servicio == "Pediatría Urgencias":
    pediatria_urgencias.render()

elif area_servicio == "Adaptación Neonatal":
    neonatologia_adaptacion.render()
elif area_servicio == "Consulta Externa":
    tipo_consulta = st.session_state.get("tipo_historia_clinica_consulta_externa")
    if tipo_consulta == "PEDIATRÍA Y PUERICULTURA":
        consulta_pediatria_puericultura.render()
    elif tipo_consulta == "HOMEOPATÍA PEDIÁTRICA":
        consulta_homeopatia_pediatrica.render()
    elif tipo_consulta == "HOMEOPATÍA ADULTOS":
        consulta_homeopatia_adultos.render()
elif area_servicio == "Homeopatía":
    tipo_homeopatia = st.session_state.get("tipo_historia_clinica_homeopatia")
    if tipo_homeopatia == "HOMEOPATÍA PEDIÁTRICA":
        consulta_homeopatia_pediatrica.render()
    elif tipo_homeopatia == "HOMEOPATÍA ADULTOS":
        consulta_homeopatia_adultos.render()
