import streamlit as st

# IMPORTAR SERVICIOS
from servicios import pediatria_urgencias
from servicios import neonatologia_adaptacion
from servicios import consulta_homeopatia_pediatrica
from servicios import consulta_homeopatia_adultos
from servicios import consulta_pediatria_puericultura

PASSWORD_APP = "8041003"

st.set_page_config(page_title="Historias Clínicas", page_icon="🩺", layout="wide")

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
