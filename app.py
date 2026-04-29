import streamlit as st

# IMPORTAR SERVICIOS
from servicios import pediatria_urgencias
from servicios import neonatologia_adaptacion

st.set_page_config(page_title="Historias Clínicas", layout="wide")

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
