import streamlit as st

# IMPORTAR SERVICIOS
from servicios import pediatria_urgencias
from servicios import neonatologia_adaptacion

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

# ENRUTADOR 🔥
if area_servicio == "Pediatría Urgencias":
    pediatria_urgencias.render()

elif area_servicio == "Adaptación Neonatal":
    neonatologia_adaptacion.render()
